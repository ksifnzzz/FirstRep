from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.stock_data import get_daily_ohlcv

# 자산 순서: 공격자산 → 수비자산 → 카나리아 자산
ASSET_ORDER = [
    # 공격자산 (Aggressive)
    "QQQ", "VEA", "VWO", "BND",
    # 수비자산 (Defensive) - BND 제외 (이미 포함)
    "BIL", "IEF", "TLT", "LQD", "TIP", "DBC",
    # 카나리아 자산 (Canary) - VEA, VWO, BND 제외 (이미 포함)
    "SPY",
]


def _monthly_adjusted_close(daily_df: pd.DataFrame) -> pd.Series:
    """월간 수정종가(Adj Close) 추출."""
    if daily_df.empty:
        return pd.Series(dtype="float64")

    close_col = "Adj Close" if "Adj Close" in daily_df.columns else "Close"
    monthly = daily_df[close_col].resample("ME").last().dropna()
    monthly.index.name = "Date"
    return monthly


def build_baa_monthly_report(start_date: str, end_date: str) -> pd.DataFrame:
    """BAA 월간 수정종가 리포트 생성.

    Returns:
        Date 컬럼과 각 자산(QQQ, VEA, VWO, BND, BIL, IEF, TLT, LQD, TIP, DBC, SPY)의
        수정종가가 포함된 DataFrame.
    """
    price_series: list[pd.Series] = []

    for ticker in ASSET_ORDER:
        daily_df = get_daily_ohlcv(ticker, start_date, end_date)
        monthly = _monthly_adjusted_close(daily_df)
        monthly.name = ticker
        price_series.append(monthly)

    if not price_series:
        return pd.DataFrame(columns=["Date"])

    # Date 기준 정렬 및 열 순서 보장
    result = pd.concat(price_series, axis=1).sort_index()
    result = result.reset_index()
    return result


def export_baa_monthly_report(output_dir: str = "output") -> tuple[Path, Path | None]:
    """BAA 월간 리포트를 CSV/XLSX로 내보내기."""
    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=2)
    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    report_df = build_baa_monthly_report(start_date, end_date)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"baa_monthly_adj_close_{start_date}_to_{end_date}"
    csv_path = out_dir / f"{base_name}.csv"
    report_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    xlsx_path: Path | None = out_dir / f"{base_name}.xlsx"
    try:
        report_df.to_excel(xlsx_path, index=False, sheet_name="BAA Monthly")
    except ImportError:
        xlsx_path = None

    return csv_path, xlsx_path


def main() -> None:
    csv_path, xlsx_path = export_baa_monthly_report()
    print(f"CSV: {csv_path}")
    if xlsx_path is not None:
        print(f"XLSX: {xlsx_path}")


if __name__ == "__main__":
    main()
