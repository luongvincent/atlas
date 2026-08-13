from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import OnboardingRequest, OnboardingResponse
from core.auth import AuthContext, get_current_user_required
from core.risk_profile import derive_risk_profile
from core.supabase_client import get_request_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/onboarding", response_model=OnboardingResponse)
async def onboarding(
    payload: OnboardingRequest,
    user: AuthContext = Depends(get_current_user_required),
) -> OnboardingResponse:
    risk_profile = derive_risk_profile(
        investing_experience=payload.investing_experience,
        time_horizon=payload.time_horizon,
        risk_comfort=payload.risk_comfort,
        goals=payload.goals,
    )

    # authenticated-role client bound to the caller's own JWT, so the
    # risk_profiles RLS policies (user_id = auth.uid()) apply.
    client = get_request_client(access_token=user.access_token)
    row = {
        "user_id": user.user_id,
        "investing_experience": payload.investing_experience,
        "time_horizon": payload.time_horizon,
        "risk_comfort": payload.risk_comfort,
        "portfolio_size_range": payload.portfolio_size_range,
        "goals": payload.goals,
        "risk_profile": risk_profile,
    }
    try:
        client.table("risk_profiles").upsert(row, on_conflict="user_id").execute()
    except Exception:
        logger.exception("Failed to upsert risk profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save onboarding responses",
        )

    return OnboardingResponse(risk_profile=risk_profile)

@router.get("/onboarding", response_model=OnboardingResponse)
async def get_onboarding(
    user: AuthContext = Depends(get_current_user_required),
) -> OnboardingResponse:
    client = get_request_client(access_token=user.access_token)

    try:
        result = (
            client.table("risk_profiles")
            .select("risk_profile")
            .eq("user_id", user.user_id)
            .maybe_single()
            .execute()
        )
    except Exception:
        logger.exception("Failed to fetch risk profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch risk profile",
        )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk profile not found",
        )

    return OnboardingResponse(
        risk_profile=result.data["risk_profile"]
    )