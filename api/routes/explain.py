from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from api.schemas import ExplainResponse
from config.tickers import TICKERS_BY_SYMBOL
from core.auth import AuthContext, get_current_user_optional
from core.explainer_chain import Explanation, ExplanationSections, NoTranscriptDataError, generate_explanation
from core.explanation_adapter import adapt_sections
from core.llm import MODEL_NAME
from core.rate_limit import limiter
from core.risk_profile import RiskProfileContext
from core.supabase_client import get_request_client

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_latest_quarter(client, ticker: str) -> tuple[str, str] | None:
    result = (
        client.table("tickers")
        .select("latest_quarter, latest_call_date")
        .eq("ticker", ticker)
        .limit(1)
        .execute()
    )
    if not result.data or not result.data[0].get("latest_quarter"):
        return None
    row = result.data[0]
    return row["latest_quarter"], row["latest_call_date"]


def _load_cached(client, ticker: str, quarter: str) -> dict | None:
    result = (
        client.table("cached_explanations")
        .select("sections, citations, model, generated_at")
        .eq("ticker", ticker)
        .eq("quarter", quarter)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _store_cache(client, ticker: str, quarter: str, explanation: Explanation) -> None:
    payload = {
        "ticker": ticker,
        "quarter": quarter,
        "sections": explanation.sections.model_dump(),
        "citations": [c.model_dump() for c in explanation.citations],
        "model": MODEL_NAME,
    }
    client.table("cached_explanations").upsert(payload, on_conflict="ticker,quarter").execute()


def _load_risk_profile_context(client, user: AuthContext | None) -> RiskProfileContext | None:
    if user is None:
        return None
    result = (
        client.table("risk_profiles")
        .select("investing_experience, risk_profile")
        .eq("user_id", user.user_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    row = result.data[0]
    return RiskProfileContext(investing_experience=row["investing_experience"], risk_profile=row["risk_profile"])


def _log_request(client, user: AuthContext | None, ticker: str, status_code: int, latency_ms: int) -> None:
    try:
        client.table("request_logs").insert(
            {
                "user_id": user.user_id if user else None,
                "endpoint": "/explain/{ticker}",
                "ticker": ticker,
                "status_code": status_code,
                "latency_ms": latency_ms,
            },
            # Skip Postgrest's default read-back of the inserted row: anon
            # deliberately has no SELECT policy on request_logs (it can
            # log a request but never read any back), so the default
            # "return=representation" insert would fail for anon callers.
            returning="minimal",
        ).execute()
    except Exception:
        logger.exception("Failed to write request log for %s", ticker)


@router.get("/explain/{ticker}", response_model=ExplainResponse)
@limiter.limit("10/minute")  # stricter than the app-wide default - this endpoint burns Groq quota
async def explain(
    request: Request,
    response: Response,
    ticker: str,
    user: AuthContext | None = Depends(get_current_user_optional),
) -> ExplainResponse:
    start = time.monotonic()
    ticker = ticker.upper()
    ticker_info = TICKERS_BY_SYMBOL.get(ticker)
    if ticker_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"We don't have an explanation for {ticker} yet.")

    client = get_request_client(access_token=user.access_token if user else None)

    latest = _get_latest_quarter(client, ticker)
    if latest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ingested transcript for {ticker} yet",
        )
    quarter, _call_date = latest
    # Cheap, deterministic per-request adaptation (no extra LLM call) - see
    # core/explanation_adapter.py. None whenever the caller is anonymous or
    # hasn't completed the onboarding pereferences form, in which case sections pass
    # through unchanged.
    risk_ctx = _load_risk_profile_context(client, user)

    cached = _load_cached(client, ticker, quarter)
    if cached:
        latency_ms = int((time.monotonic() - start) * 1000)
        _log_request(client, user, ticker, status.HTTP_200_OK, latency_ms)
        adapted_sections, glossary = adapt_sections(
            ExplanationSections.model_validate(cached["sections"]), risk_ctx
        )
        return ExplainResponse(
            ticker=ticker,
            company_name=ticker_info.company_name,
            quarter=quarter,
            sections=adapted_sections,
            citations=cached["citations"],
            cached=True,
            generated_at=cached["generated_at"],
            glossary=glossary,
        )

    if user is None:
        # Cache writes require auth (see migrations/006_cached_explanations.sql) -
        # this is a deliberate trade-off, not a bug: anonymous callers can read
        # any already-cached explanation for free, but generating a new one
        # (which burns Groq quota) requires signing in.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "This explanation hasn't been generated yet. Sign in to generate it "
                "(already-generated explanations are free to read without an account)."
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        explanation = generate_explanation(ticker, quarter, ticker_info.company_name)
    except NoTranscriptDataError as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        _log_request(client, user, ticker, status.HTTP_404_NOT_FOUND, latency_ms)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        # An unhandled error here becomes a bare 500 with no CORS headers, which
        # the browser reports as a network failure instead of a readable message.
        logger.exception("Explanation generation failed for %s %s", ticker, quarter)
        latency_ms = int((time.monotonic() - start) * 1000)
        _log_request(client, user, ticker, status.HTTP_502_BAD_GATEWAY, latency_ms)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="We couldn't generate this explanation right now. Please try again in a few minutes.",
        ) from exc

    latency_ms = int((time.monotonic() - start) * 1000)
    logger.info("Generated explanation for %s %s in %dms", ticker, quarter, latency_ms)

    try:
        _store_cache(client, ticker, quarter, explanation)
    except Exception:
        logger.exception("Failed to cache explanation for %s %s", ticker, quarter)

    _log_request(client, user, ticker, status.HTTP_200_OK, latency_ms)

    adapted_sections, glossary = adapt_sections(explanation.sections, risk_ctx)
    return ExplainResponse(
        ticker=ticker,
        company_name=ticker_info.company_name,
        quarter=quarter,
        sections=adapted_sections,
        citations=explanation.citations,
        cached=False,
        generated_at=None,
        glossary=glossary,
    )
