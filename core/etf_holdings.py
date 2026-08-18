"""Top holdings + sector breakdown for an ETF, via yfinance's `funds_data`.

Not available for individual stocks - yfinance raises `YFDataException`
when you access fund-only fields on a non-fund ticker, which is exactly
how we distinguish "not an ETF" from a real failure (see fetch_holdings).
"""

from __future__ import annotations

import logging

import yfinance as yf
from pydantic import BaseModel
from yfinance.exceptions import YFDataException

logger = logging.getLogger(__name__)

MAX_HOLDINGS = 10


class HoldingEntry(BaseModel):
    ticker: str
    name: str
    weight_percent: float


class SectorWeight(BaseModel):
    sector: str
    weight_percent: float


class EtfHoldings(BaseModel):
    ticker: str
    top_holdings: list[HoldingEntry]
    sector_weightings: list[SectorWeight]


class NoHoldingsDataError(Exception):
    """Raised when yfinance has no fund data for this ticker (e.g. it's not an ETF)."""


_SECTOR_LABELS = {
    "realestate": "Real Estate",
    "consumer_cyclical": "Consumer Cyclical",
    "basic_materials": "Basic Materials",
    "consumer_defensive": "Consumer Defensive",
    "technology": "Technology",
    "communication_services": "Communication Services",
    "financial_services": "Financial Services",
    "utilities": "Utilities",
    "industrials": "Industrials",
    "energy": "Energy",
    "healthcare": "Healthcare",
}


def fetch_holdings(ticker: str) -> EtfHoldings:
    funds_data = yf.Ticker(ticker).funds_data

    try:
        top_holdings_df = funds_data.top_holdings
    except YFDataException as exc:
        raise NoHoldingsDataError(f"No fund holdings data available for {ticker}") from exc

    holdings = [
        HoldingEntry(
            ticker=str(symbol),
            name=str(row["Name"]),
            weight_percent=round(float(row["Holding Percent"]) * 100, 2),
        )
        for symbol, row in top_holdings_df.head(MAX_HOLDINGS).iterrows()
    ]

    sectors: list[SectorWeight] = []
    try:
        raw_sectors = funds_data.sector_weightings or {}
        sectors = sorted(
            (
                SectorWeight(sector=_SECTOR_LABELS.get(key, key.replace("_", " ").title()), weight_percent=round(value * 100, 2))
                for key, value in raw_sectors.items()
                if value
            ),
            key=lambda s: s.weight_percent,
            reverse=True,
        )
    except Exception:
        logger.exception("Failed to fetch sector weightings for %s", ticker)

    return EtfHoldings(ticker=ticker, top_holdings=holdings, sector_weightings=sectors)
