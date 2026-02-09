"""한국·미국 주식/ETF 일봉 데이터 조회."""

from __future__ import annotations

from typing import Literal

import pandas as pd

try:
    import FinanceDataReader as fdr
except ImportError:
    fdr = None  # type: ignore[assignment]


def _infer_market(ticker: str) -> Literal["kr", "us"]:
    """티커 형식으로 시장 추정: 6자리 숫자면 한국, 아니면 미국."""
    s = ticker.strip().upper()
    if s.isdigit() and len(s) == 6:
        return "kr"
    return "us"


def get_daily_ohlcv(
    ticker: str,
    start_date: str,
    end_date: str,
    market: Literal["kr", "us"] | None = None,
) -> pd.DataFrame:
    """한국 또는 미국 주식/ETF의 해당 기간 일봉 데이터를 반환합니다.

    Args:
        ticker: 종목 코드 (한국 예: '005930', 미국 예: 'AAPL', 'SPY')
        start_date: 시작일 (YYYY-MM-DD 또는 YYYY)
        end_date: 종료일 (YYYY-MM-DD 또는 YYYY)
        market: 'kr' | 'us' | None. None이면 티커로 자동 판단 (6자리 숫자 → kr)

    Returns:
        Date 인덱스, 컬럼: Open, High, Low, Close, Volume, Change(있을 경우) 등

    Raises:
        ImportError: FinanceDataReader 미설치 시
    """
    if fdr is None:
        raise ImportError(
            "FinanceDataReader가 필요합니다. 설치: pip install finance-datareader"
        )

    if market is None:
        market = _infer_market(ticker)

    # FinanceDataReader: DataReader(symbol, start, end)
    df = fdr.DataReader(ticker.strip(), start_date.strip(), end_date.strip())

    if df is None or df.empty:
        return pd.DataFrame()

    # 인덱스 이름 통일 (Date)
    if df.index.name is None or df.index.name != "Date":
        df.index.name = "Date"
    return df


# 사용 예시 (python -m src.stock_data 로 실행 시)
if __name__ == "__main__":
    # 한국: 삼성전자 2024년 1월~3월
    df_kr = get_daily_ohlcv("005930", "2024-01-01", "2024-03-31", market="kr")
    print("한국 005930 (삼성전자) 일봉:", len(df_kr), "건")
    if not df_kr.empty:
        print(df_kr.tail(3))

    # 미국: SPY ETF 2024년 1월~3월
    df_us = get_daily_ohlcv("SPY", "2024-01-01", "2024-03-31", market="us")
    print("\n미국 SPY 일봉:", len(df_us), "건")
    if not df_us.empty:
        print(df_us.tail(3))
