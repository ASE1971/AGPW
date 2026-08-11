import logging
from pathlib import Path
from typing import Iterable

from data.db import connect_db

from .columns import rows_from_dataframe, validate_required_columns

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["index_name", "date", "open", "high", "low", "close"]

FIELDS = [
    "index_name",
    "date",
    "open",
    "high",
    "low",
    "close",
    "change_pct",
    "turnover",
    "currency",
]


def validate_columns(columns: Iterable[str]) -> None:
    validate_required_columns(columns, REQUIRED_COLUMNS, "indexes_daily")


def ingest_indexes_daily(df, source: Path) -> int:
    validate_columns(df.columns)
    rows = rows_from_dataframe(df, FIELDS)

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
