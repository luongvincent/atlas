from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException, status

from api.schemas import EtfResponse, EtfsListResponse
from config.etf_tickers import ETFS_BY_SYMBOL, SUPPORTED_ETFS
from config.etf_tickers_ca import ETFS_CA_BY_SYMBOL, SUPPORTED_ETFS_CA
from core.etf_holdings import EtfHoldings, NoHoldingsDataError, fetch_holdings

logger = logging.getLogger(__name__)
router = APIRouter()


def _to_response(e) -> EtfResponse:
    return EtfResponse(
        ticker=e.ticker,
        name=e.name,
        avg_daily_volume=e.avg_daily_volume,
        exchange=e.exchange,
        category=e.category,
    )


@router.get("/etfs", response_model=EtfsListResponse)
async def list_etfs() -> EtfsListResponse:
    return EtfsListResponse(etfs=[_to_response(e) for e in SUPPORTED_ETFS])


@router.get("/etfs/ca", response_model=EtfsListResponse)
async def list_etfs_ca() -> EtfsListResponse:
    return EtfsListResponse(etfs=[_to_response(e) for e in SUPPORTED_ETFS_CA])


@router.get("/etfs/{ticker}/holdings", response_model=EtfHoldings)
async def get_etf_holdings(ticker: str) -> EtfHoldings:
    ticker = ticker.upper()
    if ticker not in ETFS_BY_SYMBOL and ticker not in ETFS_CA_BY_SYMBOL:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unsupported ETF: {ticker}")

    try:
        return await asyncio.to_thread(fetch_holdings, ticker)
    except NoHoldingsDataError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to fetch holdings for %s", ticker)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch ETF holdings"
        ) from exc
