from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

SUPPORTED_MARKETS = {"KR", "US"}
SUPPORTED_FREQ = {"daily", "monthly"}
SUPPORTED_PROVIDERS = {"auto", "fdr", "yfinance", "pykrx"}


@dataclass(frozen=True)
class FetchRequest:
    market: str
    symbol: str
    start: str
    end: str
    freq: str = "daily"
    provider: str = "auto"
    adjusted: bool = True


def _ensure_valid_request(req: FetchRequest) -> None:
    if req.market not in SUPPORTED_MARKETS:
        raise ValueError(f"Unsupported market: {req.market}")
    if req.freq not in SUPPORTED_FREQ:
        raise ValueError(f"Unsupported frequency: {req.freq}")
    if req.provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider: {req.provider}")
    start_dt = pd.to_datetime(req.start)
    end_dt = pd.to_datetime(req.end)
    if start_dt > end_dt:
        raise ValueError("start must be <= end")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapped = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
        "시가": "open",
        "고가": "high",
        "저가": "low",
        "종가": "close",
        "거래량": "volume",
    }
    out = df.rename(columns=mapped).copy()
    return out


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Date" in out.columns:
        out["Date"] = pd.to_datetime(out["Date"])
        out = out.set_index("Date")
    if "날짜" in out.columns:
        out["날짜"] = pd.to_datetime(out["날짜"])
        out = out.set_index("날짜")
    out.index = pd.to_datetime(out.index)
    out.index.name = "date"
    out = out.sort_index()
    return out


def _finalize_frame(
    df: pd.DataFrame,
    market: str,
    symbol: str,
    source: str,
    adjusted: bool,
) -> pd.DataFrame:
    out = _normalize_columns(_normalize_index(df))
    required = ["open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in out.columns]
    if missing:
        raise ValueError(f"Missing required OHLCV columns: {missing}")
    out = out[required + (["adj_close"] if "adj_close" in out.columns else [])].copy()
    out["market"] = market
    out["symbol"] = symbol
    out["source"] = source
    out["adjusted"] = adjusted
    out = out.reset_index()
    out["date"] = pd.to_datetime(out["date"]).dt.tz_localize(None)
    return out


def _fetch_fdr(req: FetchRequest) -> pd.DataFrame:
    import FinanceDataReader as fdr

    df = fdr.DataReader(req.symbol, req.start, req.end)
    if df is None or df.empty:
        raise ValueError("No data returned from FinanceDataReader")
    return _finalize_frame(df, req.market, req.symbol, "fdr", req.adjusted)


def _fetch_pykrx(req: FetchRequest) -> pd.DataFrame:
    if req.market != "KR":
        raise ValueError("pykrx is only supported for KR market")
    from pykrx import stock

    start = pd.to_datetime(req.start).strftime("%Y%m%d")
    end = pd.to_datetime(req.end).strftime("%Y%m%d")
    df = stock.get_market_ohlcv(start, end, req.symbol, frequency="d", adjusted=req.adjusted)
    if df is None or df.empty:
        raise ValueError("No data returned from pykrx")
    return _finalize_frame(df, req.market, req.symbol, "pykrx", req.adjusted)


def _fetch_yfinance(req: FetchRequest) -> pd.DataFrame:
    import yfinance as yf

    tickers = [req.symbol]
    if req.market == "KR" and "." not in req.symbol:
        tickers = [f"{req.symbol}.KS", f"{req.symbol}.KQ"]

    err: Exception | None = None
    for ticker in tickers:
        try:
            df = yf.download(
                ticker,
                start=req.start,
                end=req.end,
                interval="1d",
                auto_adjust=False,
                progress=False,
            )
            if df is not None and not df.empty:
                return _finalize_frame(df, req.market, req.symbol, "yfinance", req.adjusted)
        except Exception as exc:  # pragma: no cover
            err = exc

    if err is not None:
        raise ValueError(f"yfinance fetch failed: {err}")
    raise ValueError("No data returned from yfinance")


def fetch_daily(req: FetchRequest) -> pd.DataFrame:
    _ensure_valid_request(req)

    if req.provider == "fdr":
        return _fetch_fdr(req)
    if req.provider == "pykrx":
        return _fetch_pykrx(req)
    if req.provider == "yfinance":
        return _fetch_yfinance(req)

    providers = ["fdr", "yfinance"] if req.market == "US" else ["fdr", "pykrx", "yfinance"]
    errors: list[str] = []
    for provider in providers:
        try:
            if provider == "fdr":
                return _fetch_fdr(req)
            if provider == "pykrx":
                return _fetch_pykrx(req)
            return _fetch_yfinance(req)
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
    raise RuntimeError("All providers failed: " + " | ".join(errors))


def aggregate_monthly_from_daily(df_daily: pd.DataFrame) -> pd.DataFrame:
    if df_daily.empty:
        return df_daily.copy()

    base_cols = {
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "market",
        "symbol",
        "source",
        "adjusted",
    }
    if not base_cols.issubset(df_daily.columns):
        missing = sorted(base_cols - set(df_daily.columns))
        raise ValueError(f"Missing columns for monthly aggregation: {missing}")

    df = df_daily.copy()
    df["date"] = pd.to_datetime(df["date"])
    grouped = []

    for (market, symbol), g in df.groupby(["market", "symbol"], sort=False):
        g = g.sort_values("date").set_index("date")
        monthly = g.resample("MS").agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
                "source": "last",
                "adjusted": "last",
            }
        )
        monthly = monthly.dropna(subset=["open", "high", "low", "close"])
        monthly["market"] = market
        monthly["symbol"] = symbol
        monthly = monthly.reset_index()
        grouped.append(monthly)

    if not grouped:
        return pd.DataFrame(columns=df_daily.columns)

    out = pd.concat(grouped, ignore_index=True)
    cols = [
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "market",
        "symbol",
        "source",
        "adjusted",
    ]
    if "adj_close" in df_daily.columns:
        out["adj_close"] = pd.NA
        cols.append("adj_close")
    return out[cols]


def fetch_ohlcv(req: FetchRequest) -> pd.DataFrame:
    daily = fetch_daily(req)
    if req.freq == "daily":
        return daily
    return aggregate_monthly_from_daily(daily)


def save_dataframe(df: pd.DataFrame, output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    suffix = out.suffix.lower()
    if suffix == ".csv":
        df.to_csv(out, index=False)
        return
    if suffix == ".parquet":
        try:
            df.to_parquet(out, index=False)
        except ImportError as exc:
            raise RuntimeError("Parquet output requires pyarrow or fastparquet installed") from exc
        return
    raise ValueError("Unsupported output extension. Use .csv or .parquet")
