from __future__ import annotations

import asyncio
import logging
import re
from typing import Literal

import yfinance as yf
from fastapi import APIRouter, HTTPException, Query, status

from api.schemas import SearchResponse, SearchResult
from config.etf_tickers import ETFS_BY_SYMBOL
from config.etf_tickers_ca import ETFS_CA_BY_SYMBOL
from config.tickers import TICKERS_BY_SYMBOL
from core.symbols import is_us_symbol, is_valid_symbol

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_RESULTS = 8
MAX_OTHER_MATCHES = 3

# shortcut: name-based guess at leveraged/inverse funds - it will miss odd names
# and could flag a normal fund. Upgrade to a curated list if that matters.
# "Ultra-Short Bond" funds are NOT leveraged, hence the lookaheads.
LEVERAGED_NAME = re.compile(
    r"\b[-+]?[123]x\b|\binverse\b|\bleveraged\b|\bultrapro\b|\bultrashort\b"
    r"|\bultra\s+(?!short)\w|\bproshares\s+short\b",
    re.IGNORECASE,
)

QUOTE_KINDS = {"EQUITY": "stock", "ETF": "etf"}


def _to_result(quote: dict) -> SearchResult | None:
    kind = QUOTE_KINDS.get(quote.get("quoteType"))
    symbol = quote.get("symbol", "")
    if kind is None:
        return None
    # Stocks: US-style symbols only (drops listings like TSLA.TO that Atlas
    # can't explain). ETFs: Canadian listings are fine, they only get market data.
    if not (is_us_symbol(symbol) if kind == "stock" else is_valid_symbol(symbol)):
        return None
    name = quote.get("longname") or quote.get("shortname") or symbol
    return SearchResult(
        ticker=symbol,
        company_name=name,
        exchange=quote.get("exchDisp") or "",
        kind=kind,
        supported=symbol in TICKERS_BY_SYMBOL if kind == "stock" else symbol in ETFS_BY_SYMBOL or symbol in ETFS_CA_BY_SYMBOL,
        leveraged=kind == "etf" and LEVERAGED_NAME.search(name) is not None,
    )


def _search(query: str, kind: str) -> SearchResponse:
    quotes = yf.Search(query, max_results=MAX_RESULTS, news_count=0, enable_fuzzy_query=False).quotes
    all_results = [r for r in (_to_result(q) for q in quotes) if r is not None]
    return SearchResponse(
        results=[r for r in all_results if r.kind == kind],
        other_matches=[r for r in all_results if r.kind != kind][:MAX_OTHER_MATCHES],
    )


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=1, max_length=50),
    kind: Literal["stock", "etf"] = Query("stock", alias="type"),
) -> SearchResponse:
    query = q.strip()
    if not query:
        return SearchResponse(results=[])
    try:
        return await asyncio.to_thread(_search, query, kind)
    except Exception as exc:
        logger.exception("Stock search failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Search is unavailable right now"
        ) from exc
