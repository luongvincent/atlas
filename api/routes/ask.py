from __future__ import annotations

import asyncio
import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from api.routes.explain import _get_latest_quarter
from api.schemas import AskRequest, AskResponse
from config.tickers import TICKERS_BY_SYMBOL
from core.ask_chain import answer_question
from core.auth import AuthContext, get_current_user_required
from core.explainer_chain import NoTranscriptDataError
from core.rate_limit import limiter
from core.supabase_client import get_request_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ask/{ticker}", response_model=AskResponse)
@limiter.limit("5/minute")  # every question is a Groq call with no cache, so tighter than /explain
async def ask(
    request: Request,
    response: Response,
    ticker: str,
    body: AskRequest,
    user: AuthContext = Depends(get_current_user_required),
) -> AskResponse:
    start = time.monotonic()
    ticker = ticker.upper()
    ticker_info = TICKERS_BY_SYMBOL.get(ticker)
    if ticker_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"We can't answer questions about {ticker} yet.")

    latest = _get_latest_quarter(get_request_client(access_token=user.access_token), ticker)
    if latest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No ingested transcript for {ticker} yet")
    quarter, _call_date = latest

    try:
        # Blocking (embedding, Pinecone, Groq + retries), so off the event loop.
        answer = await asyncio.to_thread(
            answer_question, ticker, quarter, ticker_info.company_name, body.question, body.history
        )
    except NoTranscriptDataError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        # A bare 500 has no CORS headers, so the browser would show a network error instead.
        logger.exception("Answering a question failed for %s %s", ticker, quarter)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="We couldn't answer that right now. Please try again in a minute.",
        ) from exc

    logger.info("Answered a question for %s %s in %dms", ticker, quarter, int((time.monotonic() - start) * 1000))
    return AskResponse(ticker=ticker, quarter=quarter, answer=answer.answer, citations=answer.citations)
