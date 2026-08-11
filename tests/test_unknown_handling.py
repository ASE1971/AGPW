import shutil
import pandas as pd
from agent.ingest import file_router


def test_unknown_moves_file(incoming_dir, temp_db, write_excel):
    # create an xlsx with headers that should classify as UNKNOWN (e.g., 'Data','Nazwa',...)
    df = pd.DataFrame([[1, 'X', 'PLXXX', 'PLN']], columns=['Data', 'Nazwa', 'ISIN', 'Waluta'])
    write_excel(df, incoming_dir / "unknown_sample.xlsx")

    # Run ingest_directory
    file_router.ingest_directory(incoming_dir)

    # Expect file moved to incoming/unknown
    unknown_dir = incoming_dir / 'unknown'
    assert unknown_dir.exists()
    moved = list(unknown_dir.glob('unknown_sample.*'))
    assert moved, 'Unknown file not moved'

    # Clean up
    shutil.rmtree(str(incoming_dir))
