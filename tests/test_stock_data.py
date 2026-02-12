"""get_daily_ohlcv 함수 테스트."""

import pytest
import pandas as pd

from src.stock_data import get_daily_ohlcv


@pytest.fixture(scope="module")
def kr_df():
    """한국 주식(삼성전자) 데이터프레임 fixture."""
    return get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")


@pytest.fixture(scope="module")
def us_df():
    """미국 주식(SPY) 데이터프레임 fixture."""
    return get_daily_ohlcv("SPY", "2024-01-02", "2024-01-05")


class TestGetDailyOhlcv:
    """get_daily_ohlcv 반환 형식 및 기본 동작 검증."""

    def test_returns_dataframe(self):
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")
        assert hasattr(df, "columns")
        assert hasattr(df, "index")
    @pytest.mark.parametrize("df_fixture", ["kr_df", "us_df"])
    def test_returns_dataframe(self, df_fixture, request):
        """반환값이 DataFrame인지 확인합니다."""
        df = request.getfixturevalue(df_fixture)
        assert isinstance(df, pd.DataFrame)

    def test_kr_has_ohlcv_columns(self):
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")
    @pytest.mark.parametrize("df_fixture", ["kr_df", "us_df"])
    def test_has_ohlcv_columns(self, df_fixture, request):
        """DataFrame에 OHLCV 컬럼들이 있는지 확인합니다."""
        df = request.getfixturevalue(df_fixture)
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert col in df.columns, f"컬럼 '{col}' 없음"

    def test_us_has_ohlcv_columns(self):
        df = get_daily_ohlcv("SPY", "2024-01-02", "2024-01-05")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert col in df.columns, f"컬럼 '{col}' 없음"

    def test_auto_market_kr(self):
        """한국 티커(6자리 숫자) 조회 테스트."""
        df = get_daily_ohlcv("005930", "2024-01-02", "2024-01-05")
    @pytest.mark.parametrize("df_fixture", ["kr_df", "us_df"])
    def test_data_is_not_empty_and_valid(self, df_fixture, request):
        """데이터가 비어있지 않고 유효한지 확인합니다."""
        df = request.getfixturevalue(df_fixture)
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
        assert df.index.name == "Date"
