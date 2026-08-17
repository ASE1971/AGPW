"""Tests for technical and fundamental analysis models."""
import pytest
import pandas as pd
from agent.models.technical import (
    calculate_sma,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_atr,
    calculate_bollinger_bands,
    calculate_obv,
    calculate_ad,
)
from agent.models.fundamental import (
    IncomeStatement,
    BalanceSheet,
    CashFlow,
    FinancialMetrics,
)


class TestTechnicalIndicators:
    """Test technical analysis indicators."""

    @pytest.fixture
    def sample_ohlc(self):
        """Create sample OHLC data."""
        return pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=100),
            "open": [100 + i * 0.5 for i in range(100)],
            "high": [102 + i * 0.5 for i in range(100)],
            "low": [99 + i * 0.5 for i in range(100)],
            "close": [101 + i * 0.5 for i in range(100)],
            "volume": [1000000 + i * 1000 for i in range(100)],
        })

    def test_sma_calculation(self, sample_ohlc):
        """Test Simple Moving Average calculation."""
        sma = calculate_sma(sample_ohlc["close"], window=20)
        assert len(sma) == len(sample_ohlc)
        assert sma.isna().sum() == 19  # First 19 values are NaN
        assert sma.iloc[19] > 0  # First valid SMA value is positive

    def test_ema_calculation(self, sample_ohlc):
        """Test Exponential Moving Average calculation."""
        ema = calculate_ema(sample_ohlc["close"], window=20)
        assert len(ema) == len(sample_ohlc)
        assert ema.isna().sum() == 0  # EMA fills all values
        assert ema.iloc[19] > 0

    def test_macd_calculation(self, sample_ohlc):
        """Test MACD calculation."""
        macd, signal, histogram = calculate_macd(sample_ohlc["close"])
        assert len(macd) == len(sample_ohlc)
        assert len(signal) == len(sample_ohlc)
        assert len(histogram) == len(sample_ohlc)
        # Check that histogram = MACD - Signal
        pd.testing.assert_series_equal(
            histogram.dropna(),
            (macd - signal).dropna(),
            check_names=False,
        )

    def test_rsi_calculation(self, sample_ohlc):
        """Test RSI calculation."""
        rsi = calculate_rsi(sample_ohlc["close"], window=14)
        assert len(rsi) == len(sample_ohlc)
        # RSI should be between 0 and 100 (excluding NaN)
        valid_rsi = rsi.dropna()
        assert valid_rsi.min() >= 0
        assert valid_rsi.max() <= 100

    def test_atr_calculation(self, sample_ohlc):
        """Test Average True Range calculation."""
        atr = calculate_atr(sample_ohlc, window=14)
        assert len(atr) == len(sample_ohlc)
        assert atr.dropna().min() > 0  # ATR should be positive

    def test_bollinger_bands_calculation(self, sample_ohlc):
        """Test Bollinger Bands calculation."""
        upper, middle, lower = calculate_bollinger_bands(
            sample_ohlc["close"], window=20, num_std=2
        )
        assert len(upper) == len(sample_ohlc)
        assert len(middle) == len(sample_ohlc)
        assert len(lower) == len(sample_ohlc)
        # Upper band should be greater than middle
        assert (upper.dropna() >= middle.dropna()).all()
        # Middle band should be greater than lower
        assert (middle.dropna() >= lower.dropna()).all()

    def test_obv_calculation(self, sample_ohlc):
        """Test On-Balance Volume calculation."""
        obv = calculate_obv(sample_ohlc["close"], sample_ohlc["volume"])
        assert len(obv) == len(sample_ohlc)
        assert obv.iloc[0] >= 0  # OBV starts at 0 or positive

    def test_ad_calculation(self, sample_ohlc):
        """Test Accumulation/Distribution calculation."""
        ad = calculate_ad(sample_ohlc)
        assert len(ad) == len(sample_ohlc)
        # A/D line should be continuous without gaps
        assert ad.isna().sum() == 0
        # A/D value should be numeric
        assert ad.dtype in ['float64', 'float32']


class TestFundamentalModels:
    """Test fundamental analysis models."""

    def test_income_statement_creation(self):
        """Test IncomeStatement model initialization."""
        stmt = IncomeStatement(
            ticker="MKCM",
            date="2024-12-31",
            revenue=1_000_000,
            cost_of_goods_sold=500_000,
            operating_expenses=200_000,
            net_income=250_000,
        )
        assert stmt.ticker == "MKCM"
        assert stmt.revenue == 1_000_000
        assert stmt.net_profit_margin == 25.0  # (250_000 / 1_000_000) * 100

    def test_balance_sheet_creation(self):
        """Test BalanceSheet model initialization."""
        sheet = BalanceSheet(
            ticker="MKCM",
            date="2024-12-31",
            total_assets=1_000_000,
            total_liabilities=400_000,
            total_equity=600_000,
            current_assets=300_000,
            current_liabilities=150_000,
        )
        assert sheet.ticker == "MKCM"
        assert sheet.total_assets == 1_000_000
        assert sheet.debt_to_equity == 400_000 / 600_000

    def test_cash_flow_creation(self):
        """Test CashFlow model initialization."""
        flow = CashFlow(
            ticker="MKCM",
            date="2024-12-31",
            operating_cash_flow=200_000,
            investing_cash_flow=-50_000,
            financing_cash_flow=-30_000,
        )
        assert flow.ticker == "MKCM"
        assert flow.net_cash_flow == 120_000  # 200_000 - 50_000 - 30_000
        assert flow.free_cash_flow == 150_000  # 200_000 - 50_000

    def test_financial_metrics_calculation(self):
        """Test FinancialMetrics calculation from components."""
        metrics = FinancialMetrics(
            ticker="MKCM",
            date="2024-12-31",
            earnings_per_share=10.0,
            price_to_earnings=15.0,
            price_to_book=2.5,
            dividend_yield=2.0,
            roe=15.0,
            roa=8.0,
        )
        assert metrics.ticker == "MKCM"
        assert metrics.earnings_per_share == 10.0
        assert metrics.roe == 15.0


class TestTechnicalIndicatorEdgeCases:
    """Test edge cases for technical indicators."""

    def test_sma_with_small_window(self):
        """Test SMA with window smaller than data."""
        data = pd.Series([1, 2, 3, 4, 5])
        sma = calculate_sma(data, window=2)
        assert sma.iloc[1] == 1.5  # (1+2)/2

    def test_rsi_with_constant_prices(self):
        """Test RSI when prices don't change."""
        data = pd.Series([100] * 30)
        rsi = calculate_rsi(data, window=14)
        # When prices are constant, all changes are 0, so RSI is undefined (all NaN)
        # This is expected behavior - no volatility means no RSI
        assert rsi.isna().all() or len(rsi.dropna()) == 0

    def test_macd_with_short_data(self):
        """Test MACD with minimal data."""
        data = pd.Series(range(1, 50))
        macd, signal, histogram = calculate_macd(data)
        assert len(macd) == len(data)
