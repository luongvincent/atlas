from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from core.ask_chain import ChatTurn
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
from core.similar_items import SimilarItem
from core.strategy_overview import StrategyOverviewSections


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
    # Jargon found in the text, for every caller - the UI underlines each term
    # inline and shows its definition on tap (see core/explanation_adapter.py).
    definitions: list[GlossaryEntry] = Field(default_factory=list)


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


class SearchResult(BaseModel):
    ticker: str
    company_name: str
    exchange: str
    kind: Literal["stock", "etf"]
    # True when the ticker is on Atlas's curated lists (stocks: has an
    # explanation; ETFs: has a category).
    supported: bool
    # ETFs only: leveraged or inverse fund (name-based heuristic).
    leveraged: bool = False


class SearchResponse(BaseModel):
    results: list[SearchResult]
    # Matches of the other kind (e.g. an ETF found while searching stocks), so
    # the UI can say "SPY is an ETF" instead of showing nothing.
    other_matches: list[SearchResult] = Field(default_factory=list)


class ExplanationRequestBody(BaseModel):
    ticker: str = Field(min_length=1, max_length=7)


class ExplanationRequestResponse(BaseModel):
    ticker: str


class EtfResponse(BaseModel):
    ticker: str
    name: str
    avg_daily_volume: int
    exchange: str
    category: str


class EtfsListResponse(BaseModel):
    etfs: list[EtfResponse]


class StrategyOverviewResponse(BaseModel):
    risk_profile: RiskProfileLabel
    investing_experience: InvestingExperience
    sections: StrategyOverviewSections
    cached: bool
    generated_at: str | None = None
    disclaimer: str = (
        "This is a general, AI-generated overview of common investing patterns - not personalized "
        "financial advice. It never names specific stocks or funds to buy. Talk to a licensed "
        "financial advisor before making real decisions with your money."
    )


class SimilarItemsResponse(BaseModel):
    ticker: str
    items: list[SimilarItem]


class AskRequest(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    # Only the last few turns: each one is resent to Groq on every question.
    history: list[ChatTurn] = Field(default_factory=list, max_length=6)


class AskResponse(BaseModel):
    ticker: str
    quarter: str
    answer: str
    citations: list[Citation]
