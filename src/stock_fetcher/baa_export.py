from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

ATTACK_ASSETS = ["QQQ", "VEA", "VWO", "BND"]
DEFENSE_ASSETS = ["BIL", "IEF", "TLT", "LQD", "TIP", "BND", "DBC"]
CANARY_ASSETS = ["SPY", "VEA", "VWO", "BND"]


def _ordered_unique_assets() -> list[str]:
    ordered = ATTACK_ASSETS + DEFENSE_ASSETS + CANARY_ASSETS
    seen: set[str] = set()
    out: list[str] = []
    for symbol in ordered:
        if symbol not in seen:
            seen.add(symbol)
            out.append(symbol)
    return out


def _fetch_monthly_adjusted_close(symbol: str, start: str, end: str) -> pd.Series:
    df = yf.download(
        symbol,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        progress=False,
    )
    if df is None or df.empty:
        raise RuntimeError(f"No data returned for {symbol}")

    price_col = "Adj Close" if "Adj Close" in df.columns else "Close"
    selected = df[price_col]
    if isinstance(selected, pd.DataFrame):
        series = selected.iloc[:, 0].copy()
    else:
        series = selected.copy()
    series.index = pd.to_datetime(series.index).tz_localize(None)
    series = series.resample("MS").last().dropna()
    return series.rename(symbol)


def build_baa_matrix(years: int = 2) -> pd.DataFrame:
    if years <= 0:
        raise ValueError("years must be > 0")

    end_date = date.today() + timedelta(days=1)
    try:
        start_date = end_date.replace(year=end_date.year - years)
    except ValueError:
        start_date = end_date.replace(year=end_date.year - years, day=28)

    start = start_date.strftime("%Y-%m-%d")
    end = end_date.strftime("%Y-%m-%d")

    assets = _ordered_unique_assets()
    monthly_series = [_fetch_monthly_adjusted_close(symbol, start, end) for symbol in assets]

    matrix = pd.concat(monthly_series, axis=1)
    matrix = matrix.sort_index()
    matrix = matrix[assets]
    matrix.index.name = "date"

    out = matrix.reset_index()
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    return out


def save_matrix(df: pd.DataFrame, output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    suffix = out.suffix.lower()
    if suffix == ".csv":
        df.to_csv(out, index=False)
        return
    if suffix == ".xlsx":
        try:
            df.to_excel(out, index=False)
        except ImportError as exc:
            raise RuntimeError("XLSX output requires openpyxl installed") from exc
        return
    raise ValueError("Unsupported output extension. Use .csv or .xlsx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export BAA monthly adjusted-close matrix")
    _ = parser.add_argument("--years", type=int, default=2, help="Recent years to fetch (default: 2)")
    _ = parser.add_argument(
        "--output",
        default="output/baa_monthly_adjclose_2y.csv",
        help="Output file path (.csv or .xlsx)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    years = int(args.years)
    output = str(args.output)

    df = build_baa_matrix(years=years)
    save_matrix(df, output)
    print(f"Saved {len(df)} rows to {output}")


if __name__ == "__main__":
    main()
