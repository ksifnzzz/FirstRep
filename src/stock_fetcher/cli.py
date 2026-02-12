from __future__ import annotations

import argparse

from stock_fetcher.collector import FetchRequest, fetch_ohlcv, save_dataframe


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch KR/US stock OHLCV data")
    parser.add_argument("--market", choices=["KR", "US"], required=True)
    parser.add_argument(
        "--symbol",
        required=True,
        help="KR: 6-digit (e.g. 005930), US: ticker (e.g. AAPL)",
    )
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--freq", choices=["daily", "monthly"], default="daily")
    parser.add_argument("--provider", choices=["auto", "fdr", "yfinance", "pykrx"], default="auto")
    parser.add_argument("--adjusted", action="store_true", default=False)
    parser.add_argument("--output", required=True, help="Output file path (.csv or .parquet)")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    req = FetchRequest(
        market=args.market,
        symbol=args.symbol,
        start=args.start,
        end=args.end,
        freq=args.freq,
        provider=args.provider,
        adjusted=args.adjusted,
    )

    df = fetch_ohlcv(req)
    save_dataframe(df, args.output)
    print(f"Saved {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
