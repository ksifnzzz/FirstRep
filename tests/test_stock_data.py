"""
주식 데이터 조회 함수 테스트
"""

import pytest
from datetime import datetime, timedelta
import pandas as pd
from src.stock_data import fetch_stock_data, fetch_multiple_stocks


class TestFetchStockData:
    """fetch_stock_data 함수 테스트"""
    
    def test_korean_stock(self):
        """한국 주식 데이터 조회 테스트 (삼성전자)"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        df = fetch_stock_data("005930", start_date, end_date)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "Close" in df.columns
        assert "Volume" in df.columns
    
    def test_us_stock(self):
        """미국 주식 데이터 조회 테스트 (Apple)"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        df = fetch_stock_data("AAPL", start_date, end_date)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "Close" in df.columns
    
    def test_invalid_date_format(self):
        """잘못된 날짜 형식 테스트"""
        with pytest.raises(ValueError):
            fetch_stock_data("AAPL", "01-01-2024", "12-31-2024")
    
    def test_invalid_date_range(self):
        """시작 날짜가 종료 날짜보다 늦은 경우 테스트"""
        with pytest.raises(ValueError):
            fetch_stock_data("AAPL", "2024-12-31", "2024-01-01")
    
    def test_auto_market_detection(self):
        """시장 자동 판단 테스트"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # 6자리 숫자: 한국 주식으로 자동 판단
        df_kr = fetch_stock_data("005930", start_date, end_date)
        assert isinstance(df_kr, pd.DataFrame)
        
        # 영문: 미국 주식으로 자동 판단
        df_us = fetch_stock_data("AAPL", start_date, end_date)
        assert isinstance(df_us, pd.DataFrame)


class TestFetchMultipleStocks:
    """fetch_multiple_stocks 함수 테스트"""
    
    def test_multiple_stocks(self):
        """여러 주식 동시 조회 테스트"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        tickers = ["AAPL", "GOOGL"]
        results = fetch_multiple_stocks(tickers, start_date, end_date, market="US")
        
        assert isinstance(results, dict)
        assert len(results) > 0
        for ticker, df in results.items():
            assert isinstance(df, pd.DataFrame)
            assert not df.empty
