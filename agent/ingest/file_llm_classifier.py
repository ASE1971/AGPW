from pathlib import Path

from typing import Literal

from .columns import fold_polish

FileType = Literal[
    "STOCK_DAILY",
    "INDEX_DAILY",
    "TICKER_MAP",
    "SECTOR_COMPOSITION",
    "SECTOR_INDEX_MAP",
    "UNKNOWN",
]


def classify_file(path: Path, df) -> FileType:
    """Classify an Excel file based on its contents.

    This is a heuristic fallback implementation. In the future,
    replace this with a local LLM classifier.
    """
    lower_cols = {fold_polish(col) for col in df.columns}
    if {"ticker", "open", "high", "low", "close"}.issubset(lower_cols):
        return "STOCK_DAILY"
    if {"index_name", "open", "high", "low", "close"}.issubset(lower_cols):
        return "INDEX_DAILY"
    if {"ticker", "name"}.issubset(lower_cols):
        return "TICKER_MAP"
    if {"sector", "ticker"}.issubset(lower_cols):
        return "SECTOR_COMPOSITION"
    if {"sector", "index_name"}.issubset(lower_cols):
        return "SECTOR_INDEX_MAP"
    return "UNKNOWN"
