import logging
from pathlib import Path
from typing import Iterable

from data.db import connect_db

from .columns import normalize_row, validate_required_columns

logger = logging.getLogger(__name__)

REQUIRED_MIN_COLUMNS = ["isin", "date"]

FIELDS = [
    "name",
    "ticker",
    "isin",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "num_trades",
    "change_pct",
    "turnover",
    "currency",
]

KEY_FIELDS = ["isin", "date"]
UPDATABLE_FIELDS = [field for field in FIELDS if field not in KEY_FIELDS]

INSERT_SQL = """
    INSERT INTO stocks_daily
        ({columns})
    VALUES ({placeholders})
    """.format(
    columns=", ".join(FIELDS), placeholders=", ".join("?" for _ in FIELDS)
)

UPDATE_SQL = """
    UPDATE stocks_daily SET
        {assignments}
    WHERE id = ?
    """.format(
    assignments=", ".join(f"{field} = ?" for field in UPDATABLE_FIELDS)
)


def validate_columns(columns: Iterable[str]) -> None:
    validate_required_columns(columns, REQUIRED_MIN_COLUMNS, "stocks_daily")


def ingest_stocks_daily(df, source: Path) -> int:
    validate_columns(df.columns)
    rows = [normalize_row(raw_row) for raw_row in df.to_dict(orient="records")]

    if not rows:
        raise ValueError("No rows found in stocks_daily file")

    logger.info("Ingesting %d rows from %s", len(rows), source.name)
    with connect_db() as conn:
        cursor = conn.cursor()
        for row in rows:
            cursor.execute(
                "SELECT id FROM stocks_daily WHERE isin = ? AND date = ?",
                tuple(row.get(field) for field in KEY_FIELDS),
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    UPDATE_SQL,
                    tuple(row.get(field) for field in UPDATABLE_FIELDS)
                    + (existing["id"],),
                )
            else:
                cursor.execute(
                    INSERT_SQL, tuple(row.get(field) for field in FIELDS)
                )
        conn.commit()
    return len(rows)
