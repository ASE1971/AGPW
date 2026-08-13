import json
import subprocess
from pathlib import Path
from typing import Literal

FileType = Literal[
    "STOCK_DAILY",
    "INDEX_DAILY",
    "TICKER_MAP",
    "SECTOR_COMPOSITION",
    "SECTOR_INDEX_MAP",
    "UNKNOWN",
]


def _heuristic_classify(df) -> FileType:
    """Fallback heuristics when LLM fails or is uncertain."""
    lower_cols = {str(col).strip().lower() for col in df.columns}

    # GPW STOCK DAILY (polskie nazwy)
    if "isin" in lower_cols and (
        "kurs zamknięcia" in lower_cols or "kurs zamkniecia" in lower_cols
    ):
        return "STOCK_DAILY"

    # GPW INDEX DAILY (polskie nazwy indeksów)
    if "nazwa" in lower_cols and (
        "kurs zamknięcia" in lower_cols or "kurs zamkniecia" in lower_cols
    ):
        return "INDEX_DAILY"

    # English-based formats
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


def classify_file(path: Path, df) -> FileType:
    """Classify an Excel file using local LLM (Phi-3) with heuristic fallback."""

    cols = list(df.columns)
    sample = df.head(5).to_dict(orient="records")

    prompt = f"""
    You are a classifier for financial Excel files.

    Decide the file type based on columns, file name, and sample rows.
    Allowed types:
    STOCK_DAILY
    INDEX_DAILY
    TICKER_MAP
    SECTOR_COMPOSITION
    SECTOR_INDEX_MAP
    UNKNOWN

    Respond with ONLY the type name.

    File name: {path.name}
    Columns: {cols}
    Sample rows: {json.dumps(sample)}
    """

    try:
        result = subprocess.run(
            ["ollama", "run", "phi3"],
            input=prompt.encode(),
            capture_output=True,
            timeout=5,
        )
        llm_output = result.stdout.decode().strip().upper()

        if llm_output in {
            "STOCK_DAILY",
            "INDEX_DAILY",
            "TICKER_MAP",
            "SECTOR_COMPOSITION",
            "SECTOR_INDEX_MAP",
            "UNKNOWN",
        }:
            return llm_output

    except Exception:
        pass

    # fallback heuristics
    return _heuristic_classify(df)
