import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".xls", ".xlsx"}


def read_excel_file(path: Path) -> pd.DataFrame:
    """Read the first sheet from an Excel file and return a DataFrame."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported Excel extension: {suffix}")

    engine = "openpyxl" if suffix == ".xlsx" else "xlrd"
    logger.info("Reading Excel file %s with engine %s", path.name, engine)

    df = pd.read_excel(path, sheet_name=0, engine=engine)

    if df is None or df.shape[0] == 0:
        raise ValueError("Excel file contains no usable data")

    return df


def read_file(path: Path) -> pd.DataFrame:
    """
    Unified reader used by router + tests.
    Supports only Excel files (.xls, .xlsx).
    """
    suffix = Path(path).suffix.lower()

    if suffix in SUPPORTED_EXTENSIONS:
        return read_excel_file(path)

    raise ValueError(f"Unsupported file type: {suffix}")
