# Stock Data Collector

Python project to fetch Korean and US stock OHLCV data in daily and monthly frequency.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

검증:

```bash
ruff check .
pytest
```

## CLI examples

Daily KR stock data:

```bash
stock-collector --market KR --symbol 005930 --start 2020-01-01 --end 2024-12-31 --freq daily --output output/005930_daily.parquet
```

Monthly US stock data:

```bash
stock-collector --market US --symbol AAPL --start 2018-01-01 --end 2024-12-31 --freq monthly --output output/AAPL_monthly.csv
```

BAA 2-year monthly adjusted-close matrix (date + assets as columns):

```bash
baa-export --years 2 --output output/baa_monthly_adjclose_2y.csv
```

## Notes

- Default provider mode is `auto`: first FinanceDataReader, then yfinance fallback.
- KR auto mode also tries `pykrx` between FDR and yfinance.
- Monthly candles are built from daily candles (`open=first`, `high=max`, `low=min`, `close=last`, `volume=sum`).
- Output supports `.csv` and `.parquet`.
