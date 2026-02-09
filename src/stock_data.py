"""
주식 데이터 조회 모듈
한국 또는 미국 주식/ETF의 일봉 데이터를 조회합니다.
"""

from datetime import datetime
from typing import Literal, Optional
import pandas as pd
import yfinance as yf
from pykrx import stock


def fetch_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    market: Optional[Literal["KR", "US"]] = None
) -> pd.DataFrame:
    """
    한국 또는 미국 주식/ETF의 일봉 데이터를 조회합니다.
    
    Parameters:
    -----------
    ticker : str
        주식 티커 심볼 (예: "005930" for 삼성전자, "AAPL" for Apple)
    start_date : str
        시작 날짜 (형식: "YYYY-MM-DD")
    end_date : str
        종료 날짜 (형식: "YYYY-MM-DD")
    market : Optional[Literal["KR", "US"]]
        시장 구분 ("KR": 한국, "US": 미국)
        None이면 자동으로 판단 (6자리 숫자면 한국, 아니면 미국)
    
    Returns:
    --------
    pd.DataFrame
        날짜, 시가, 고가, 저가, 종가, 거래량 등이 포함된 데이터프레임
    
    Examples:
    ---------
    >>> df = fetch_stock_data("005930", "2024-01-01", "2024-12-31")  # 삼성전자
    >>> df = fetch_stock_data("AAPL", "2024-01-01", "2024-12-31", market="US")  # Apple
    """
    
    # 시장 자동 판단
    if market is None:
        if ticker.isdigit() and len(ticker) == 6:
            market = "KR"
        else:
            market = "US"
    
    # 날짜 형식 검증
    try:
        _start = datetime.strptime(start_date, "%Y-%m-%d")
        _end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식을 사용하세요: {e}")
    
    if _start > _end:
        raise ValueError("시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
    
    # 한국 주식 조회
    if market == "KR":
        try:
            df = stock.get_market_ohlcv(start_date, end_date, ticker)
            # pykrx는 [시가, 고가, 저가, 종가, 거래량, 등락률] 반환
            df.columns = ["Open", "High", "Low", "Close", "Volume", "ChangeRate"]
            df.index.name = "Date"
            return df
        except Exception as e:
            raise ValueError(f"한국 주식 데이터 조회 실패 (티커: {ticker}): {e}")
    
    # 미국 주식 조회
    elif market == "US":
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if df.empty:
                raise ValueError(f"데이터를 찾을 수 없습니다. 티커가 정확한지 확인하세요: {ticker}")
            return df
        except Exception as e:
            raise ValueError(f"미국 주식 데이터 조회 실패 (티커: {ticker}): {e}")


def fetch_multiple_stocks(
    tickers: list[str],
    start_date: str,
    end_date: str,
    market: Optional[Literal["KR", "US"]] = None
) -> dict[str, pd.DataFrame]:
    """
    여러 주식의 일봉 데이터를 한 번에 조회합니다.
    
    Parameters:
    -----------
    tickers : list[str]
        주식 티커 심볼 리스트
    start_date : str
        시작 날짜 (형식: "YYYY-MM-DD")
    end_date : str
        종료 날짜 (형식: "YYYY-MM-DD")
    market : Optional[Literal["KR", "US"]]
        시장 구분
    
    Returns:
    --------
    dict[str, pd.DataFrame]
        {티커: 데이터프레임} 형식의 딕셔너리
    """
    result = {}
    for ticker in tickers:
        try:
            result[ticker] = fetch_stock_data(ticker, start_date, end_date, market)
        except ValueError as e:
            print(f"⚠️  {ticker} 조회 중 오류: {e}")
    
    return result
