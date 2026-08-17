from pathlib import Path
import logging
import shutil

from .file_reader import read_file
from .file_llm_classifier import classify_file
from .ingest_stocks_daily import ingest_stocks_daily
from .ingest_indexes_daily import ingest_indexes_daily

logger = logging.getLogger(__name__)

INGESTORS = {
    "STOCK_DAILY": ingest_stocks_daily,
    "INDEX_DAILY": ingest_indexes_daily,
}


def ingest_file(path: Path) -> None:
    """Ingest a single file and move it to loaded/ or unknown/."""
    try:
        df = read_file(path)
        file_type = classify_file(path, df)

        ingestor = INGESTORS.get(file_type)
        if ingestor is None:
            raise ValueError(f"Unsupported file type: {file_type}")

        row_count = ingestor(df, path)
        logger.info("Ingested %s rows from %s", row_count, path.name)

        # Move to loaded/
        loaded_dir = path.parent / "loaded"
        loaded_dir.mkdir(exist_ok=True)
        shutil.move(str(path), loaded_dir / path.name)

    except Exception as e:
        logger.error("Failed to ingest %s: %s", path.name, e)

        # Move to unknown/
        unknown_dir = path.parent / "unknown"
        unknown_dir.mkdir(exist_ok=True)
        shutil.move(str(path), unknown_dir / path.name)


def ingest_directory(directory: Path) -> None:
    """Ingest all files in the given directory."""
    incoming = Path(directory)

    for path in incoming.glob("*"):
        if path.is_file():
            ingest_file(path)
