from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException, status

from config.tickers import TICKERS_BY_SYMBOL
from core.sentiment import SentimentResult, get_sentiment

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sentiment/{ticker}", response_model=SentimentResult)
async def get_ticker_sentiment(ticker: str) -> SentimentResult:
    ticker = ticker.upper()
    if ticker not in TICKERS_BY_SYMBOL:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unsupported ticker: {ticker}")

    try:
        result = await asyncio.to_thread(get_sentiment, ticker)
    except Exception as exc:
        logger.exception("Failed to compute sentiment for %s", ticker)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to compute sentiment"
        ) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No transcript ingested for {ticker}")
    return result
