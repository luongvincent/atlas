from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import ExplanationRequestBody, ExplanationRequestResponse
from config.tickers import TICKERS_BY_SYMBOL
from core.auth import AuthContext, get_current_user_required
from core.supabase_client import get_request_client
from core.symbols import is_us_symbol

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/explanation-requests", response_model=ExplanationRequestResponse)
async def request_explanation(
    payload: ExplanationRequestBody,
    user: AuthContext = Depends(get_current_user_required),
) -> ExplanationRequestResponse:
    ticker = payload.ticker.strip().upper()
    if not is_us_symbol(ticker):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid stock symbol")
    if ticker in TICKERS_BY_SYMBOL:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"{ticker} is already covered - no request needed"
        )

    client = get_request_client(access_token=user.access_token)
    try:
        # Same row twice is a no-op (unique user_id+ticker), so re-clicking is harmless.
        client.table("explanation_requests").upsert(
            {"user_id": user.user_id, "ticker": ticker},
            on_conflict="user_id,ticker",
            ignore_duplicates=True,
            returning="minimal",
        ).execute()
    except Exception as exc:
        logger.exception("Failed to save explanation request for %s", ticker)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save your request"
        ) from exc

    return ExplanationRequestResponse(ticker=ticker)
