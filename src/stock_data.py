"""Stock data retrieval module."""

from datetime import datetime
from typing import Literal

import pandas as pd
import yfinance as yf
from pykrx import stock


def fetch_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: Literal["daily", "monthly"] = "daily",
) -> pd.DataFrame:
    """Fetch OHLCV data for KR/US stocks and ETFs using auto market detection."""
    if interval not in ["daily", "monthly"]:
        raise ValueError("interval must be either 'daily' or 'monthly'.")

    detected_market = "KR" if ticker.isdigit() and len(ticker) == 6 else "US"

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(
            f"Invalid date format. Use YYYY-MM-DD format. {e}"
        ) from e

    if start_dt > end_dt:
        raise ValueError("start_date cannot be later than end_date.")

    if detected_market == "KR":
        try:
            # Always fetch daily data first to ensure column consistency and handle resampling manually
            df = stock.get_market_ohlcv(start_date, end_date, ticker, "d")

            if df.empty:
                raise ValueError(f"No data found for ticker: {ticker}")

            # Select first 5 columns (Open, High, Low, Close, Volume) to avoid length mismatch
            df = df.iloc[:, :5]
            df.columns = ["Open", "High", "Low", "Close", "Volume"]

            if interval == "monthly":
                # Manual resampling to avoid "Invalid frequency: M" error and ensure consistency
                try:
                    resampler = df.resample("ME")
                except ValueError:
                    resampler = df.resample("M")
                
                df = resampler.agg({
                    "Open": "first",
                    "High": "max",
                    "Low": "min",
                    "Close": "last",
                    "Volume": "sum"
                })
                df["ChangeRate"] = df["Close"].pct_change().fillna(0) * 100
                df = df.dropna()

            df.index.name = "Date"
            return df
        except Exception as e:
            raise ValueError(
                f"Failed to fetch KR stock data (ticker: {ticker}, interval: {interval}): {e}"
            ) from e

    try:
        yf_interval = "1d" if interval == "daily" else "1mo"
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=yf_interval,
            progress=False,
        )
        if df.empty:
            raise ValueError(f"No data found for ticker: {ticker}")
        return df
    except Exception as e:
        raise ValueError(
            f"Failed to fetch US stock data (ticker: {ticker}, interval: {interval}): {e}"
        ) from e


def fetch_multiple_stocks(
    tickers: list[str],
    start_date: str,
    end_date: str,
    interval: Literal["daily", "monthly"] = "daily",
) -> dict[str, pd.DataFrame]:
    """Fetch OHLCV data for multiple stock tickers."""
    result: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        try:
            result[ticker] = fetch_stock_data(ticker, start_date, end_date, interval)
        except ValueError as e:
            print(f"Warning: failed to fetch {ticker}: {e}")
    return result
