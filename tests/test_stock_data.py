"""get_daily_ohlcv 및 시장 추정 함수 테스트."""

import pytest

from src.stock_data import _infer_market, get_daily_ohlcv


class TestInferMarket:
    """_infer_market(티커) → 'kr' | 'us' 검증."""

    def test_kr_6digit(self):
        assert _infer_market("005930") == "kr"
        assert _infer_market("000660") == "kr"

    def test_kr_6digit_with_spaces(self):
        assert _infer_market("  005930  ") == "kr"

    def test_us_alphabetic(self):
        assert _infer_market("AAPL") == "us"
        assert _infer_market("SPY") == "us"

    def test_us_lowercase(self):
        assert _infer_market("aapl") == "us"


class TestGetDailyOhlcv:
    """get_daily_ohlcv 반환 형식 및 기본 동작 검증."""

    def test_returns_dataframe(self):
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05", market="kr")
        assert hasattr(df, "columns")
        assert hasattr(df, "index")

    def test_kr_has_ohlcv_columns(self):
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05", market="kr")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert col in df.columns, f"컬럼 '{col}' 없음"

    def test_us_has_ohlcv_columns(self):
        df = get_daily_ohlcv("SPY", "2024-01-02", "2024-01-05", market="us")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert col in df.columns, f"컬럼 '{col}' 없음"

    def test_auto_market_kr(self):
        """티커 6자리 숫자면 market 생략 시 kr."""
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")
        assert not df.empty
        assert "Close" in df.columns

    def test_auto_market_us(self):
        """티커가 6자리 숫자가 아니면 market 생략 시 us."""
        df = get_daily_ohlcv("SPY", "2024-01-02", "2024-01-05")
        assert not df.empty
        assert "Close" in df.columns

    def test_index_name_is_date(self):
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05", market="kr")
        if not df.empty:
            assert df.index.name == "Date"
