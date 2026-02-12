from __future__ import annotations

import pandas as pd

from stock_fetcher.collector import aggregate_monthly_from_daily


def test_aggregate_monthly_from_daily_basic_ohlcv() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-31",
                    "2024-02-01",
                    "2024-02-29",
                ]
            ),
            "open": [10, 11, 12, 13, 14],
            "high": [12, 13, 14, 15, 16],
            "low": [9, 10, 11, 12, 13],
            "close": [11, 12, 13, 14, 15],
            "volume": [100, 110, 120, 130, 140],
            "market": ["US"] * 5,
            "symbol": ["AAPL"] * 5,
            "source": ["fdr"] * 5,
            "adjusted": [False] * 5,
        }
    )

    monthly = aggregate_monthly_from_daily(df)

    assert len(monthly) == 2

    jan = monthly[monthly["date"] == pd.Timestamp("2024-01-01")].iloc[0]
    feb = monthly[monthly["date"] == pd.Timestamp("2024-02-01")].iloc[0]

    assert jan["open"] == 10
    assert jan["high"] == 14
    assert jan["low"] == 9
    assert jan["close"] == 13
    assert jan["volume"] == 330

    assert feb["open"] == 13
    assert feb["high"] == 16
    assert feb["low"] == 12
    assert feb["close"] == 15
    assert feb["volume"] == 270
