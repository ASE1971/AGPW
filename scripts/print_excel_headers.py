import sys
import pathlib

# Ensure workspace root is on sys.path for imports
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from agent.ingest.file_reader import read_excel_file

DEFAULT_PATH = pathlib.Path('data/incoming/unknown/_2026-08-07_akcje.xls')

p = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
print('Reading', p)
try:
    df = read_excel_file(p)
    for i, c in enumerate(df.columns, start=1):
        print(f'{i}: {c}')
except Exception as e:
    print('ERROR:', e)
    raise
