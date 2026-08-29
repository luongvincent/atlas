"""Static roster of supported tickers.

Generated via scripts/generate_ticker_list.py on 2026-08-08 using yfinance's
"most_actives" screener, filtered to quoteType == EQUITY (individual
operating companies; ETFs/index funds/trusts excluded) and ranked by average
daily volume.

One screener result, SPCX ("Space Exploration Technologies Corp." /
SpaceX), was manually excluded despite passing the EQUITY filter: SpaceX is
privately held and has no public quarterly earnings calls, which this
product depends on for every ticker. The next-ranked candidate (SNAP)
backfilled its slot. Re-run the generator script to refresh this list, and
re-check for the same false-positive pattern (privately held companies with
speculative/gray-market quotes) before pasting results in.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TickerInfo:
    ticker: str
    company_name: str
    avg_daily_volume: int
    exchange: str
    sector: str
    industry: str


# sector/industry fetched live via yfinance's Ticker.info on 2026-08-23 -
# see the "similar tickers" recommender in core/similar_items.py, which
# groups stocks by sector the same way ETFs are grouped by category.
SUPPORTED_TICKERS: list[TickerInfo] = [
    TickerInfo(ticker="NVDA", company_name="NVIDIA Corporation", avg_daily_volume=134_604_800, exchange="NMS", sector="Technology", industry="Semiconductors"),
    TickerInfo(ticker="INTC", company_name="Intel Corporation", avg_daily_volume=115_042_580, exchange="NMS", sector="Technology", industry="Semiconductors"),
    TickerInfo(ticker="NOK", company_name="Nokia Corporation Sponsored", avg_daily_volume=82_459_360, exchange="NYQ", sector="Technology", industry="Communication Equipment"),
    TickerInfo(ticker="SOFI", company_name="SoFi Technologies, Inc.", avg_daily_volume=78_231_800, exchange="NMS", sector="Financial Services", industry="Credit Services"),
    TickerInfo(ticker="ONDS", company_name="Ondas Holdings Inc.", avg_daily_volume=68_263_700, exchange="NCM", sector="Technology", industry="Communication Equipment"),
    TickerInfo(ticker="AAPL", company_name="Apple Inc.", avg_daily_volume=63_789_980, exchange="NMS", sector="Technology", industry="Consumer Electronics"),
    TickerInfo(ticker="AMZN", company_name="Amazon.com, Inc.", avg_daily_volume=62_557_750, exchange="NMS", sector="Consumer Cyclical", industry="Internet Retail"),
    TickerInfo(ticker="PATH", company_name="UiPath, Inc.", avg_daily_volume=60_232_610, exchange="NYQ", sector="Technology", industry="Software - Infrastructure"),
    TickerInfo(ticker="PLTR", company_name="Palantir Technologies Inc.", avg_daily_volume=59_936_790, exchange="NMS", sector="Technology", industry="Software - Infrastructure"),
    TickerInfo(ticker="AAL", company_name="American Airlines Group, Inc.", avg_daily_volume=59_708_230, exchange="NMS", sector="Industrials", industry="Airlines"),
    TickerInfo(ticker="F", company_name="Ford Motor Company", avg_daily_volume=58_094_880, exchange="NYQ", sector="Consumer Cyclical", industry="Auto Manufacturers"),
    TickerInfo(ticker="T", company_name="AT&T Inc.", avg_daily_volume=57_586_980, exchange="NYQ", sector="Communication Services", industry="Telecom Services"),
    TickerInfo(ticker="PLUG", company_name="Plug Power, Inc.", avg_daily_volume=53_147_610, exchange="NCM", sector="Industrials", industry="Electrical Equipment & Parts"),
    TickerInfo(ticker="NU", company_name="Nu Holdings Ltd.", avg_daily_volume=52_306_160, exchange="NYQ", sector="Financial Services", industry="Banks - Regional"),
    TickerInfo(ticker="SNAP", company_name="Snap Inc.", avg_daily_volume=48_889_480, exchange="NYQ", sector="Communication Services", industry="Internet Content & Information"),
]

TICKERS_BY_SYMBOL: dict[str, TickerInfo] = {t.ticker: t for t in SUPPORTED_TICKERS}
