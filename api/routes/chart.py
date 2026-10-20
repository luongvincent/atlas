from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException, Query, status

from api.schemas import ChartResponse
from config.etf_tickers import ETFS_BY_SYMBOL
from config.etf_tickers_ca import ETFS_CA_BY_SYMBOL
from config.tickers import TICKERS_BY_SYMBOL
from core.market_data import ChartRange, NoChartDataError, fetch_chart_data
from core.symbols import is_valid_symbol

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/chart/{ticker}", response_model=ChartResponse)
async def get_chart(
    ticker: str,
    chart_range: ChartRange = Query("1M", alias="range"),
) -> ChartResponse:
    ticker = ticker.upper()
    known = ticker in TICKERS_BY_SYMBOL or ticker in ETFS_BY_SYMBOL or ticker in ETFS_CA_BY_SYMBOL
    # Any well-formed symbol is allowed so searched stocks outside the top 15 get a chart.
    if not known and not is_valid_symbol(ticker):
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
