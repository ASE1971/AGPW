"""Shared header/row normalization helpers used by the ingest modules."""

import logging
from typing import Any, Dict, Iterable, Mapping

logger = logging.getLogger(__name__)

POLISH_FOLDING = {
    "ą": "a",
    "ć": "c",
    "ę": "e",
    "ł": "l",
    "ń": "n",
    "ó": "o",
    "ś": "s",
    "ż": "z",
    "ź": "z",
}

HEADER_MAP = {
    "data": "date",
    "nazwa": "name",
    "isin": "isin",
    "waluta": "currency",
    "kurs otwarcia": "open",
    "kurs max": "high",
    "kurs min": "low",
    "kurs zamkniecia": "close",
    "zmiana": "change_pct",
    "wolumen": "volume",
    "liczba transakcji": "num_trades",
    "obrot": "turnover",
}


def fold_polish(text: Any) -> Any:
    """Lowercase, strip and replace Polish diacritics so headers compare equal."""
    if text is None:
        return text
    folded = str(text).strip().lower()
    for accented, plain in POLISH_FOLDING.items():
        folded = folded.replace(accented, plain)
    return folded


def normalize_column(column: Any, header_map: Mapping[str, str] = HEADER_MAP) -> str:
    """Fold a single column label and map it to its canonical field name."""
    folded = fold_polish(column)
    return header_map.get(folded, folded)


def normalize_columns(
    columns: Iterable[Any], header_map: Mapping[str, str] = HEADER_MAP
) -> set:
    """Return the set of canonical field names present in `columns`."""
    return {normalize_column(column, header_map) for column in columns}


def normalize_row(
    raw_row: Mapping[Any, Any], header_map: Mapping[str, str] = HEADER_MAP
) -> Dict[str, Any]:
    """Return `raw_row` keyed by canonical field names, dropping unlabelled keys."""
    return {
        normalize_column(key, header_map): value
        for key, value in raw_row.items()
        if key is not None
    }


def validate_required_columns(
    columns: Iterable[Any],
    required: Iterable[str],
    table: str,
    header_map: Mapping[str, str] = HEADER_MAP,
) -> None:
    """Raise ValueError if any canonical name in `required` is absent from `columns`."""
    normalized = normalize_columns(columns, header_map)
    missing = [column for column in required if column not in normalized]
    if missing:
        raise ValueError(f"Missing required columns for {table}: {missing}")


def rows_from_dataframe(
    df, fields: Iterable[str], header_map: Mapping[str, str] = HEADER_MAP
) -> list:
    """Convert a DataFrame into a list of tuples ordered by `fields`."""
    fields = list(fields)
    return [
        tuple(normalize_row(raw_row, header_map).get(field) for field in fields)
        for raw_row in df.to_dict(orient="records")
    ]
