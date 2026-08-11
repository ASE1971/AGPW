import pandas as pd
import pytest

from agent.ingest.columns import (
    fold_polish,
    normalize_columns,
    normalize_row,
    rows_from_dataframe,
    validate_required_columns,
)


def test_fold_polish_strips_and_folds_diacritics():
    assert fold_polish("  Kurs Zamknięcia ") == "kurs zamkniecia"
    assert fold_polish(None) is None


def test_normalize_columns_maps_polish_headers():
    assert normalize_columns(["Data", "Kurs otwarcia", "Ticker"]) == {
        "date",
        "open",
        "ticker",
    }


def test_normalize_row_drops_unlabelled_keys():
    assert normalize_row({"Nazwa": "A", None: "x"}) == {"name": "A"}


def test_validate_required_columns_reports_missing():
    with pytest.raises(ValueError, match=r"stocks_daily: \['isin'\]"):
        validate_required_columns(["Data"], ["isin", "date"], "stocks_daily")


def test_rows_from_dataframe_orders_by_fields():
    df = pd.DataFrame([{"Data": "2026-08-11", "Kurs otwarcia": 10.0}])

    assert rows_from_dataframe(df, ["open", "date", "close"]) == [
        (10.0, "2026-08-11", None)
    ]
