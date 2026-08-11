import logging
from pathlib import Path
import shutil

from .file_llm_classifier import classify_file
from .file_reader import read_excel_file
from .ingest_indexes_daily import ingest_indexes_daily
from .ingest_stocks_daily import ingest_stocks_daily

logger = logging.getLogger(__name__)

INGESTORS = {
    "STOCK_DAILY": ingest_stocks_daily,
    "INDEX_DAILY": ingest_indexes_daily,
}


def ingest_file(path: Path) -> None:
    """Ingest a single file; if successful remove it, else move UNKNOWN to unknown/ and log columns."""
    logger.info("Processing file: %s", path.name)
    df = read_excel_file(path)
    file_type = classify_file(path, df)
    logger.info("Classified %s as %s", path.name, file_type)

    if file_type not in INGESTORS:
        # Log columns for later analysis and move file to unknown folder
        cols = list(df.columns)
        logger.warning("File %s classified UNKNOWN; columns: %s", path.name, cols)
        unknown_dir = path.parent / "unknown"
        unknown_dir.mkdir(parents=True, exist_ok=True)
        dest = unknown_dir / path.name
        try:
            shutil.move(str(path), str(dest))
            logger.info("Moved UNKNOWN file %s to %s", path.name, dest)
        except Exception:
            logger.exception("Failed to move UNKNOWN file %s", path.name)
        return

    ingestor = INGESTORS[file_type]
    row_count = ingestor(df, path)
    logger.info("Ingested %d records from %s", row_count, path.name)

    try:
        path.unlink()
        logger.info("Removed file after ingest: %s", path.name)
    except Exception:
        logger.exception("Failed to remove file after ingest: %s", path.name)


def ingest_directory(directory: Path) -> None:
    """Scan a directory for Excel files and ingest them in a deterministic order."""
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Ingest directory not found: {directory}")

    excel_files = sorted(
        [path for path in directory.iterdir() if path.suffix.lower() in {".xls", ".xlsx"}]
    )
    if not excel_files:
        logger.info("No Excel files found in %s", directory)
        return

    for path in excel_files:
        try:
            ingest_file(path)
        except Exception as exc:
            logger.exception("Failed to ingest %s: %s", path.name, exc)
