from agent.ingest.file_reader import read_excel_file


def test_read_excel_file(tmp_path, sample_stock_frame, write_excel):
    file_path = write_excel(sample_stock_frame, tmp_path / "sample.xlsx")

    result = read_excel_file(file_path)

    assert result.shape == (2, 7)
    assert list(result.columns) == ["Ticker", "ISIN", "Date", "Open", "High", "Low", "Close"]
    assert result.loc[0, "Ticker"] == "AAA"
