import pandas as pd
import pytest

from data import db

SAMPLE_STOCK_ROWS = {
    'Ticker': ['AAA', 'BBB'],
    'ISIN': ['PLAAA0000001', 'PLBBB0000002'],
    'Date': ['2026-08-10', '2026-08-11'],
    'Open': [100.0, 105.0],
    'High': [110.0, 108.0],
    'Low': [99.0, 103.0],
    'Close': [108.0, 107.0],
}


@pytest.fixture
def sample_stock_frame() -> pd.DataFrame:
    """A minimal English-header stock daily frame that classifies as STOCK_DAILY."""
    return pd.DataFrame(SAMPLE_STOCK_ROWS)


@pytest.fixture
def incoming_dir(tmp_path):
    """An empty ingest directory under tmp_path."""
    directory = tmp_path / 'incoming'
    directory.mkdir()
    return directory


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Point `data.db.DB_PATH` at an initialized database inside tmp_path."""
    db_path = tmp_path / 'agpw.db'
    monkeypatch.setattr(db, 'DB_PATH', db_path)
    db.initialize_database(db_path)
    return db_path


@pytest.fixture
def write_excel():
    """Write a DataFrame to `path` as Excel and return the path."""

    def _write(df: pd.DataFrame, path):
        df.to_excel(path, index=False)
        return path

    return _write
