from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException, Query, status

from api.schemas import ChartResponse
from config.etf_tickers import ETFS_BY_SYMBOL
from config.etf_tickers_ca import ETFS_CA_BY_SYMBOL
from config.tickers import TICKERS_BY_SYMBOL
from core.market_data import ChartRange, NoChartDataError, fetch_chart_data

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/chart/{ticker}", response_model=ChartResponse)
async def get_chart(
    ticker: str,
    chart_range: ChartRange = Query("1M", alias="range"),
) -> ChartResponse:
    ticker = ticker.upper()
    if ticker not in TICKERS_BY_SYMBOL and ticker not in ETFS_BY_SYMBOL and ticker not in ETFS_CA_BY_SYMBOL:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unsupported ticker: {ticker}")

    try:
        points, interval = await asyncio.to_thread(fetch_chart_data, ticker, chart_range)
    except NoChartDataError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to fetch chart data for %s (%s)", ticker, chart_range)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch price data"
        ) from exc

    return ChartResponse(ticker=ticker, range=chart_range, interval=interval, points=points)
