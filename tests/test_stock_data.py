"""get_daily_ohlcv 함수 테스트."""

import pytest

from src.stock_data import get_daily_ohlcv


class TestGetDailyOhlcv:
    """get_daily_ohlcv 반환 형식 및 기본 동작 검증."""

    def test_returns_dataframe(self):
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")
        assert hasattr(df, "columns")
        assert hasattr(df, "index")

    def test_kr_has_ohlcv_columns(self):
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert col in df.columns, f"컬럼 '{col}' 없음"

    def test_us_has_ohlcv_columns(self):
        df = get_daily_ohlcv("SPY", "2024-01-02", "2024-01-05")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert col in df.columns, f"컬럼 '{col}' 없음"

    def test_auto_market_kr(self):
        """한국 티커(6자리 숫자) 조회 테스트."""
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")
        assert not df.empty
        assert "Close" in df.columns

    def test_auto_market_us(self):
        """미국 티커(문자열) 조회 테스트."""
        df = get_daily_ohlcv("SPY", "2024-01-02", "2024-01-05")
        assert not df.empty
        assert "Close" in df.columns

    def test_index_name_is_date(self):
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")
        if not df.empty:
            assert df.index.name == "Date"
