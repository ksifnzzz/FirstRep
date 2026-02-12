from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.stock_data import get_daily_ohlcv

ASSET_GROUPS: dict[str, list[str]] = {
    "aggressive": ["QQQ", "VEA", "VWO", "BND"],
    "defensive": ["BIL", "IEF", "TLT", "LQD", "TIP", "BND", "DBC"],
    "canary": ["SPY", "VEA", "VWO", "BND"],
}


def _to_monthly_ohlcv(daily_df: pd.DataFrame) -> pd.DataFrame:
    if daily_df.empty:
        return pd.DataFrame()

    agg_map: dict[str, str] = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }

    existing_agg_map = {col: agg for col, agg in agg_map.items() if col in daily_df.columns}
    monthly_df = daily_df.resample("ME").agg(existing_agg_map).dropna(how="all")
    monthly_df.index.name = "Date"

    if "Change" in daily_df.columns:
        monthly_df["Change"] = daily_df["Change"].resample("ME").last()

    return monthly_df


def _fetch_group_monthly_data(
    group_name: str,
    tickers: list[str],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for ticker in tickers:
        daily_df = get_daily_ohlcv(ticker, start_date, end_date)
        monthly_df = _to_monthly_ohlcv(daily_df)

        if monthly_df.empty:
            continue

        temp = monthly_df.reset_index()
        temp.insert(0, "Ticker", ticker)
        temp.insert(0, "Group", group_name)
        frames.append(temp)

    if not frames:
        return pd.DataFrame(columns=["Group", "Ticker", "Date", "Open", "High", "Low", "Close", "Volume", "Change"])

    return pd.concat(frames, ignore_index=True)


def export_baa_monthly_data(output_dir: str = "output") -> list[Path]:
    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=2)

    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []
    all_groups: list[pd.DataFrame] = []

    for group_name, tickers in ASSET_GROUPS.items():
        group_df = _fetch_group_monthly_data(group_name, tickers, start_date, end_date)
        all_groups.append(group_df)

        group_path = out_dir / f"baa_monthly_{group_name}_{start_date}_to_{end_date}.csv"
        group_df.to_csv(group_path, index=False, encoding="utf-8-sig")
        written_files.append(group_path)

    all_df = pd.concat(all_groups, ignore_index=True)
    all_path = out_dir / f"baa_monthly_all_{start_date}_to_{end_date}.csv"
    all_df.to_csv(all_path, index=False, encoding="utf-8-sig")
    written_files.append(all_path)

    return written_files


def main() -> None:
    files = export_baa_monthly_data()
    for path in files:
        print(path)


if __name__ == "__main__":
    main()
