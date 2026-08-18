"""Static roster of supported ETFs.

Generated via scripts/generate_etf_list.py using a custom yfinance
ETFQuery (US region, ranked by day volume), then filtered to exclude
leveraged/inverse "trading" products (2x/3x bull or bear funds, daily
target funds) - these are daily-reset derivatives meant for short-term
trading, not buy-and-hold, which cuts against this app's family/
retirement-planning focus. Filtered on both Yahoo's `category` field
(e.g. "Trading--Leveraged Equity") and the fund name itself, since
category isn't reliably populated for every fund - see the generator
script for the specific case (DAMD) that slipped through category-only
filtering and needed the name-based fallback.

Re-run the generator script to refresh this list, and re-check the raw
(unfiltered) candidate pool it prints for new leveraged/inverse products
that might need adding to the name-pattern exclusion list.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EtfInfo:
    ticker: str
    name: str
    avg_daily_volume: int
    exchange: str
    category: str


SUPPORTED_ETFS: list[EtfInfo] = [
    EtfInfo(ticker="BITO", name="ProShares Bitcoin ETF", avg_daily_volume=67_747_870, exchange="PCX", category="Digital Assets"),
    EtfInfo(ticker="DRAM", name="Roundhill Memory ETF", avg_daily_volume=52_823_220, exchange="BTS", category="Technology"),
    EtfInfo(ticker="SPY", name="State Street SPDR S&P 500 ETF Trust", avg_daily_volume=43_191_080, exchange="PCX", category="Large Blend"),
    EtfInfo(ticker="TLT", name="iShares 20+ Year Treasury Bond ETF", avg_daily_volume=36_335_710, exchange="NGM", category="Long Government"),
    EtfInfo(ticker="QQQ", name="Invesco QQQ Trust", avg_daily_volume=34_233_320, exchange="NGM", category="Large Growth"),
    EtfInfo(ticker="IBIT", name="iShares Bitcoin Trust ETF", avg_daily_volume=31_805_830, exchange="NGM", category="Digital Assets"),
    EtfInfo(ticker="HYG", name="iShares iBoxx $ High Yield Corporate Bond ETF", avg_daily_volume=28_122_630, exchange="PCX", category="High Yield Bond"),
    EtfInfo(ticker="LQD", name="iShares iBoxx $ Investment Grade Corporate Bond ETF", avg_daily_volume=26_860_440, exchange="PCX", category="Corporate Bond"),
    EtfInfo(ticker="XLE", name="State Street Energy Select Sector SPDR ETF", avg_daily_volume=26_521_640, exchange="PCX", category="Equity Energy"),
    EtfInfo(ticker="XLF", name="State Street Financial Select Sector SPDR ETF", avg_daily_volume=26_100_260, exchange="PCX", category="Financial"),
    EtfInfo(ticker="GDX", name="VanEck Gold Miners ETF", avg_daily_volume=25_341_510, exchange="PCX", category="Equity Precious Metals"),
    EtfInfo(ticker="ETHA", name="iShares Ethereum Trust ETF", avg_daily_volume=23_111_900, exchange="NGM", category="Digital Assets"),
    EtfInfo(ticker="EWZ", name="iShares MSCI Brazil ETF", avg_daily_volume=22_603_430, exchange="PCX", category="Focused Region"),
    EtfInfo(ticker="SCHD", name="Schwab U.S. Dividend Equity ETF", avg_daily_volume=22_259_780, exchange="PCX", category="Large Value"),
    EtfInfo(ticker="XLU", name="State Street Utilities Select Sector SPDR ETF", avg_daily_volume=22_052_690, exchange="PCX", category="Utilities"),
]

ETFS_BY_SYMBOL: dict[str, EtfInfo] = {e.ticker: e for e in SUPPORTED_ETFS}
