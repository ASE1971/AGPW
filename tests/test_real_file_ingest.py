from data import db
from agent.ingest import file_router


def test_real_file_ingest(incoming_dir, temp_db, sample_stock_frame, write_excel):
    file_path = write_excel(sample_stock_frame, incoming_dir / 'real_akcje.xlsx')

    # Run ingest on the incoming dir
    file_router.ingest_directory(incoming_dir)

    # File should be removed after successful ingest
    assert not file_path.exists(), 'Input file should be deleted after ingest'

    # DB should contain two rows
    conn = db.connect_db(temp_db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM stocks_daily")
    cnt = cur.fetchone()['c']
    conn.close()
    assert cnt == 2
