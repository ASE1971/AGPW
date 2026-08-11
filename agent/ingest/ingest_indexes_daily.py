import logging
from pathlib import Path
from typing import Iterable

from data.db import connect_db

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["index_name", "date", "open", "high", "low", "close"]


def validate_columns(columns: Iterable[str]) -> None:
    lower_cols = {col.strip().lower() for col in columns}
    missing = [col for col in REQUIRED_COLUMNS if col not in lower_cols]
    if missing:
        raise ValueError(f"Missing required columns for indexes_daily: {missing}")


def ingest_indexes_daily(df, source: Path) -> int:
    validate_columns(df.columns)
    rows = []
    for raw_row in df.to_dict(orient="records"):
        row = {k.strip().lower(): v for k, v in raw_row.items()}
        rows.append(
            (
                row.get("index_name"),
                row.get("date"),
                row.get("open"),
                row.get("high"),
                row.get("low"),
                row.get("close"),
                row.get("change_pct"),
                row.get("turnover"),
                row.get("currency"),
            )
        )

    if not rows:
        raise ValueError("No rows found in indexes_daily file")

    logger.info("Ingesting %d rows from %s", len(rows), source.name)
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO indexes_daily
                (index_name, date, open, high, low, close, change_pct, turnover, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    return len(rows)
