import sqlite3
import logging
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "agpw.db"

CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS stocks_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        name TEXT,
        isin TEXT NOT NULL,
        date DATE NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        num_trades INTEGER,
        open_interest INTEGER,
        open_interest_value REAL,
        par_value REAL,
        change_pct REAL,
        turnover REAL,
        currency TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS indexes_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        index_name TEXT NOT NULL,
        date DATE NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        change_pct REAL,
        turnover REAL,
        currency TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS tickers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL UNIQUE,
        name TEXT,
        sector TEXT,
        market TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sectors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sector TEXT NOT NULL UNIQUE,
        description TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sector_companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sector TEXT NOT NULL,
        ticker TEXT NOT NULL,
        company_name TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sector_index_map (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sector TEXT NOT NULL,
        index_name TEXT NOT NULL
    );
    """,
]


def connect_db(path: Path | str | None = None, timeout: float = 30.0) -> sqlite3.Connection:
    """Open a SQLite database connection with foreign key support enabled.

    If `path` is None, use the module-level `DB_PATH` so tests can monkeypatch `DB_PATH`
    without being affected by a default parameter bound at import time.
    """
    if path is None:
        path = DB_PATH
    connection = sqlite3.connect(path, timeout=timeout)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    """Create all required tables for AGPW in the connected SQLite database."""
    cursor = connection.cursor()
    for statement in CREATE_TABLES_SQL:
        cursor.execute(statement)

    # Ensure `stocks_daily` has expected columns; add missing columns via ALTER TABLE.
    expected_cols = {
        "name": "TEXT",
        "volume": "REAL",
        "num_trades": "INTEGER",
        "open_interest": "INTEGER",
        "open_interest_value": "REAL",
        "par_value": "REAL",
    }
    try:
        cursor.execute("PRAGMA table_info(stocks_daily)")
        rows = cursor.fetchall()
        existing = {row[1] for row in rows} if rows is not None else set()
    except Exception:
        existing = set()

    for col, coltype in expected_cols.items():
        if col not in existing:
            try:
                cursor.execute(f"ALTER TABLE stocks_daily ADD COLUMN {col} {coltype};")
                logging.getLogger(__name__).info("Added column %s to stocks_daily", col)
            except Exception as e:
                logging.getLogger(__name__).warning("Failed to add column %s: %s", col, e)

    # Try to create unique index on (isin, date). If duplicates exist, skip and log.
    try:
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_stocks_daily_isin_date ON stocks_daily(isin, date);"
        )
    except sqlite3.IntegrityError as e:
        logging.getLogger(__name__).warning(
            "Could not create unique index ux_stocks_daily_isin_date due to existing duplicates: %s", e
        )
    connection.commit()


def initialize_database(path: Path | str = DB_PATH) -> Path:
    """Initialize the SQLite database file and create AGPW schema."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect_db(path) as connection:
        create_tables(connection)
    return path


# ---------------------------------------------------------------------------
#  INSERT FUNCTIONS
# ---------------------------------------------------------------------------

def insert_index_daily(
    index_name: str,
    date,
    open: float | None,
    high: float | None,
    low: float | None,
    close: float | None,
    change_pct: float | None = None,
    turnover: float | None = None,
    currency: str | None = None,
    path: Path | str | None = None,
):
    """Insert one INDEX_DAILY row into SQLite."""
    with connect_db(path) as conn:
        conn.execute(
            """
            INSERT INTO indexes_daily (
                index_name, date, open, high, low, close, change_pct, turnover, currency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                index_name,
                date,
                open,
                high,
                low,
                close,
                change_pct,
                turnover,
                currency,
            ),
        )
        conn.commit()


if __name__ == "__main__":
    db_file = initialize_database()
    print(f"Initialized AGPW database at: {db_file}")
