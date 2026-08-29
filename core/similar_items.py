"""Content-based "similar items" recommender for tickers and ETFs.

Simple rule-based scoring, not a learned model or collaborative filtering -
right-sized for this app's small, static universe (15 stocks + 15 US ETFs +
15 CA ETFs), same "explainable over clever" philosophy as
core/strategy_overview.py and frontend/lib/insights.ts's experience-based
article ranking. Every match can be explained in one sentence to the user.

Stocks and ETFs use different taxonomies (sector/industry vs. fund
category), so a stock is only ever compared against other stocks, and an
ETF only against other ETFs in the same regional roster (US ETFs vs. CA
ETFs) - mixing US and CA ETFs together would be comparing volume-ranked
lists that live on fundamentally different scales (see
config/etf_tickers_ca.py's docstring), and cross-comparing stocks to ETFs
has no shared attribute to score on at all.
"""

from __future__ import annotations

from pydantic import BaseModel

from config.etf_tickers import SUPPORTED_ETFS, EtfInfo
from config.etf_tickers_ca import SUPPORTED_ETFS_CA
from config.tickers import SUPPORTED_TICKERS, TickerInfo


class SimilarItem(BaseModel):
    ticker: str
    name: str
    kind: str  # "stock" | "etf"
    avg_daily_volume: int
    reason: str


def _similar_stocks(subject: TickerInfo, limit: int) -> list[SimilarItem]:
    scored: list[tuple[int, TickerInfo]] = []
    for candidate in SUPPORTED_TICKERS:
        if candidate.ticker == subject.ticker:
            continue
        if candidate.industry == subject.industry:
            scored.append((0, candidate))
        elif candidate.sector == subject.sector:
            scored.append((1, candidate))

    scored.sort(key=lambda pair: (pair[0], -pair[1].avg_daily_volume))
    return [
        SimilarItem(
            ticker=c.ticker,
            name=c.company_name,
            kind="stock",
            avg_daily_volume=c.avg_daily_volume,
            reason=f"Same industry: {c.industry}" if dist == 0 else f"Same sector: {c.sector}",
        )
        for dist, c in scored[:limit]
    ]


def _similar_etfs(subject: EtfInfo, roster: list[EtfInfo], limit: int) -> list[SimilarItem]:
    matches = [c for c in roster if c.ticker != subject.ticker and c.category == subject.category]
    matches.sort(key=lambda c: -c.avg_daily_volume)
    return [
        SimilarItem(
            ticker=c.ticker,
            name=c.name,
            kind="etf",
            avg_daily_volume=c.avg_daily_volume,
            reason=f"Same category: {c.category}",
        )
        for c in matches[:limit]
    ]


def get_similar_items(ticker: str, limit: int = 4) -> list[SimilarItem]:
    """Look up `ticker` across the stock and both ETF rosters and return
    the most similar other supported items, or an empty list if `ticker`
    isn't supported or has no close match in its own roster."""
    upper = ticker.upper()

    for t in SUPPORTED_TICKERS:
        if t.ticker == upper:
            return _similar_stocks(t, limit)

    for e in SUPPORTED_ETFS:
        if e.ticker == upper:
            return _similar_etfs(e, SUPPORTED_ETFS, limit)

    for e in SUPPORTED_ETFS_CA:
        if e.ticker == upper:
            return _similar_etfs(e, SUPPORTED_ETFS_CA, limit)

    return []
