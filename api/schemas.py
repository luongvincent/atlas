from __future__ import annotations

from pydantic import BaseModel, Field

from core.explainer_chain import Citation, ExplanationSections
from core.explanation_adapter import GlossaryEntry
from core.market_data import ChartPoint
from core.risk_profile import (
    Goal,
    InvestingExperience,
    PortfolioSizeRange,
    RiskProfileLabel,
    TimeHorizon,
)


class TickerResponse(BaseModel):
    ticker: str
    company_name: str
    avg_daily_volume: int
    exchange: str
    latest_quarter: str | None
    latest_call_date: str | None


class TickersListResponse(BaseModel):
    tickers: list[TickerResponse]


class ExplainResponse(BaseModel):
    ticker: str
    company_name: str
    quarter: str
    sections: ExplanationSections
    citations: list[Citation]
    cached: bool
    generated_at: str | None = None
    # Populated only when the caller is authenticated, has completed the
    # onboarding pereferences form, and investing_experience is beginner-level - see
    # core/explanation_adapter.py.
    glossary: list[GlossaryEntry] = Field(default_factory=list)


class OnboardingRequest(BaseModel):
    investing_experience: InvestingExperience
    time_horizon: TimeHorizon
    risk_comfort: int = Field(ge=1, le=5, description="1 (very risk-averse) to 5 (very risk-tolerant)")
    portfolio_size_range: PortfolioSizeRange
    goals: Goal


class OnboardingResponse(OnboardingRequest):
    risk_profile: RiskProfileLabel


class ChartResponse(BaseModel):
    ticker: str
    range: str
    interval: str
    points: list[ChartPoint]


class EtfResponse(BaseModel):
    ticker: str
    name: str
    avg_daily_volume: int
    exchange: str
    category: str


class EtfsListResponse(BaseModel):
    etfs: list[EtfResponse]
