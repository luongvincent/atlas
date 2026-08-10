from __future__ import annotations

import logging

from fastapi import APIRouter

from api.schemas import TickerResponse, TickersListResponse
from config.tickers import SUPPORTED_TICKERS
from core.supabase_client import get_request_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/tickers", response_model=TickersListResponse)
async def list_tickers() -> TickersListResponse:
    client = get_request_client()
    try:
        result = (
            client.table("tickers")
            .select("ticker, latest_quarter, latest_call_date")
            .execute()
        )
        latest_by_ticker = {row["ticker"]: row for row in result.data}
    except Exception:
        logger.exception("Failed to load latest call metadata from Supabase")
        latest_by_ticker = {}

    tickers = [
        TickerResponse(
            ticker=t.ticker,
            company_name=t.company_name,
            avg_daily_volume=t.avg_daily_volume,
            exchange=t.exchange,
            latest_quarter=latest_by_ticker.get(t.ticker, {}).get("latest_quarter"),
            latest_call_date=latest_by_ticker.get(t.ticker, {}).get("latest_call_date"),
        )
        for t in SUPPORTED_TICKERS
    ]
    return TickersListResponse(tickers=tickers)
