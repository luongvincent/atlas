from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException, status

from config.etf_tickers import ETFS_BY_SYMBOL
from config.etf_tickers_ca import ETFS_CA_BY_SYMBOL
from config.tickers import TICKERS_BY_SYMBOL
from core.symbols import is_valid_symbol
from core.ticker_stats import TickerStats, fetch_ticker_stats

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats/{ticker}", response_model=TickerStats)
async def get_stats(ticker: str) -> TickerStats:
    ticker = ticker.upper()
    known = ticker in TICKERS_BY_SYMBOL or ticker in ETFS_BY_SYMBOL or ticker in ETFS_CA_BY_SYMBOL
    # Any well-formed symbol is allowed so searched stocks outside the top 15 get stats.
    if not known and not is_valid_symbol(ticker):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unsupported ticker: {ticker}")

    try:
        return await asyncio.to_thread(fetch_ticker_stats, ticker)
    except Exception as exc:
        logger.exception("Failed to fetch stats for %s", ticker)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch ticker stats"
        ) from exc
