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
    # Use pandas.read_excel directly with the file path so the underlying file is
    # closed immediately after reading (avoids file-lock issues on Windows).
    df = pd.read_excel(path, sheet_name=0, engine=engine)
    if df is None or df.shape[0] == 0:
        raise ValueError("Excel file contains no usable data")
    return df
