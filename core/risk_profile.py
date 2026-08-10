"""Derives a risk_profile label from the 5-question onboarding quiz.

Pure and offline - no DB/network access here, so it's cheaply unit
testable. The literal types below intentionally mirror the check
constraints in migrations/004_risk_profiles.sql exactly; if that table's
allowed values ever change, update both places together.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

InvestingExperience = Literal["none", "beginner", "intermediate", "experienced"]
TimeHorizon = Literal["short_term", "medium_term", "long_term"]
PortfolioSizeRange = Literal["under_1k", "1k_10k", "10k_100k", "100k_1m", "over_1m"]
Goal = Literal["preserve_capital", "income", "growth", "speculation"]
RiskProfileLabel = Literal["conservative", "moderate", "aggressive"]

# Each factor is scored on a 0-2 "conservative -> aggressive" scale, then
# combined as a weighted average (risk_comfort counted twice - it's the
# quiz's most direct self-report of risk tolerance, the rest are proxies).
# portfolio_size_range is deliberately NOT scored: it's collected for
# suitability/context (and shown back to the user), but bigger or smaller
# balances don't reliably predict risk *tolerance* one way or the other.
_TIME_HORIZON_SCORE: dict[TimeHorizon, float] = {
    "short_term": 0.0,
    "medium_term": 1.0,
    "long_term": 2.0,
}
_GOAL_SCORE: dict[Goal, float] = {
    "preserve_capital": 0.0,
    "income": 1.0,
    "growth": 1.5,
    "speculation": 2.0,
}
_EXPERIENCE_SCORE: dict[InvestingExperience, float] = {
    "none": 0.0,
    "beginner": 0.5,
    "intermediate": 1.0,
    "experienced": 2.0,
}


def _risk_comfort_score(risk_comfort: int) -> float:
    # 1-5 -> 0-2
    return (risk_comfort - 1) / 2


def derive_risk_profile(
    *,
    investing_experience: InvestingExperience,
    time_horizon: TimeHorizon,
    risk_comfort: int,
    goals: Goal,
) -> RiskProfileLabel:
    weighted_sum = (
        _risk_comfort_score(risk_comfort) * 2
        + _TIME_HORIZON_SCORE[time_horizon]
        + _GOAL_SCORE[goals]
        + _EXPERIENCE_SCORE[investing_experience]
    )
    score = weighted_sum / 5  # weights: 2 + 1 + 1 + 1
    if score < 2 / 3:
        return "conservative"
    if score < 4 / 3:
        return "moderate"
    return "aggressive"


@dataclass
class RiskProfileContext:
    """What GET /explain needs to adapt its output - see core/explanation_adapter.py."""

    investing_experience: InvestingExperience
    risk_profile: RiskProfileLabel
