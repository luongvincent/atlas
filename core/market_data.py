"""Historical price data for the ticker chart, via yfinance.

yfinance has no async API - always called through asyncio.to_thread from
the request handler so a slow Yahoo Finance response doesn't block the
event loop, consistent with "async FastAPI throughout" elsewhere in this
app.
"""

from __future__ import annotations

from typing import Literal

import yfinance as yf
from pydantic import BaseModel

ChartRange = Literal["1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "ALL"]

# yfinance (period, interval) per range. Intraday granularity for the short
# ranges, coarsening to daily/weekly/monthly for longer ones so payloads
# stay small - a 5-year chart doesn't need minute-level detail.
_RANGE_TO_YFINANCE: dict[ChartRange, tuple[str, str]] = {
    "1D": ("1d", "5m"),
    "5D": ("5d", "15m"),
    "1M": ("1mo", "1d"),
    "6M": ("6mo", "1d"),
    "YTD": ("ytd", "1d"),
    "1Y": ("1y", "1d"),
    "5Y": ("5y", "1wk"),
    "ALL": ("max", "1mo"),
}


class ChartPoint(BaseModel):
    timestamp: str
    close: float


class NoChartDataError(Exception):
    """Raised when yfinance returns no rows for a ticker/range."""


def fetch_chart_data(ticker: str, chart_range: ChartRange) -> tuple[list[ChartPoint], str]:
    """Blocking - run via asyncio.to_thread from request handlers."""
    period, interval = _RANGE_TO_YFINANCE[chart_range]
    history = yf.Ticker(ticker).history(period=period, interval=interval)
    history = history.dropna(subset=["Close"])
    if history.empty:
        raise NoChartDataError(f"No price data available for {ticker}")

    points = [
        ChartPoint(timestamp=index.isoformat(), close=round(float(row["Close"]), 4))
        for index, row in history.iterrows()
    ]
    return points, interval
