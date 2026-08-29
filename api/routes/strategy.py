from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from api.schemas import StrategyOverviewResponse
from core.auth import AuthContext, get_current_user_required
from core.llm import MODEL_NAME
from core.rate_limit import limiter
from core.strategy_overview import StrategyOverview, generate_strategy_overview
from core.supabase_client import get_request_client

logger = logging.getLogger(__name__)
router = APIRouter()


def _load_risk_profile(client, user_id: str) -> tuple[str, str] | None:
    result = (
        client.table("risk_profiles")
        .select("risk_profile, investing_experience")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    row = result.data[0]
    return row["risk_profile"], row["investing_experience"]


def _load_cached(client, risk_profile: str, investing_experience: str) -> dict | None:
    result = (
        client.table("cached_strategy_overviews")
        .select("sections, model, generated_at")
        .eq("risk_profile", risk_profile)
        .eq("investing_experience", investing_experience)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _store_cache(client, risk_profile: str, investing_experience: str, overview: StrategyOverview) -> None:
    payload = {
        "risk_profile": risk_profile,
        "investing_experience": investing_experience,
        "sections": overview.sections.model_dump(),
        "model": MODEL_NAME,
    }
    client.table("cached_strategy_overviews").upsert(
        payload, on_conflict="risk_profile,investing_experience"
    ).execute()


@router.get("/strategy-overview", response_model=StrategyOverviewResponse)
@limiter.limit("10/minute")  # stricter than the app-wide default - can trigger a Groq call
async def get_strategy_overview(
    request: Request,
    response: Response,
    user: AuthContext = Depends(get_current_user_required),
) -> StrategyOverviewResponse:
    client = get_request_client(access_token=user.access_token)

    profile = _load_risk_profile(client, user.user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complete the risk profile quiz first (POST /onboarding).",
        )
    risk_profile, investing_experience = profile

    cached = _load_cached(client, risk_profile, investing_experience)
    if cached:
        return StrategyOverviewResponse(
            risk_profile=risk_profile,
            investing_experience=investing_experience,
            sections=cached["sections"],
            cached=True,
            generated_at=cached["generated_at"],
        )

    try:
        overview = await asyncio.to_thread(generate_strategy_overview, risk_profile, investing_experience)
    except Exception as exc:
        logger.exception(
            "Failed to generate strategy overview for %s/%s", risk_profile, investing_experience
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to generate strategy overview"
        ) from exc

    try:
        _store_cache(client, risk_profile, investing_experience, overview)
    except Exception:
        logger.exception("Failed to cache strategy overview for %s/%s", risk_profile, investing_experience)

    return StrategyOverviewResponse(
        risk_profile=risk_profile,
        investing_experience=investing_experience,
        sections=overview.sections,
        cached=False,
        generated_at=None,
    )
