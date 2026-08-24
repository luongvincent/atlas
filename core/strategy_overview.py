"""Groq chain that generates a GENERAL, educational overview of what a
given risk profile + experience level commonly means in practice.

Deliberately NOT personalized investment advice and NOT grounded in any
retrieval (no RAG here, unlike explainer_chain.py) - this is general
financial education, the same "explain, don't recommend" principle the
rest of the app follows for earnings-call explanations. See CLAUDE.md for
the product-direction discussion behind this: a version of this feature
that named specific tickers/recommended trades tied to an individual's
answers would be a meaningful step toward regulated "investment advice,"
which this project deliberately stays clear of.

Cached per (risk_profile, investing_experience) - not per user - see
migrations/009_cached_strategy_overviews.sql. Only 12 possible
combinations exist, so this is generated at most 12 times, ever.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from core.llm import get_llm, groq_retry
from core.risk_profile import InvestingExperience, RiskProfileLabel

_EXPERIENCE_LABELS: dict[InvestingExperience, str] = {
    "none": "has never invested before",
    "beginner": "has a little investing experience",
    "intermediate": "is fairly comfortable with investing",
    "experienced": "is an experienced investor",
}

_RISK_PROFILE_LABELS: dict[RiskProfileLabel, str] = {
    "conservative": "conservative (prioritizes protecting what they have over growth)",
    "moderate": "moderate (comfortable balancing growth and risk)",
    "aggressive": "aggressive (comfortable with larger swings in pursuit of growth)",
}


class StrategyOverviewSections(BaseModel):
    what_this_profile_means: str = Field(
        description="2-3 sentences on what this risk profile commonly means in practice for someone with this experience level."
    )
    common_approaches: str = Field(
        description=(
            "General, descriptive overview of investing approaches commonly associated with this "
            "profile - asset classes, sectors, or strategies described in GENERAL terms (e.g. "
            "'growth-oriented sectors like technology' is fine; a specific company or ticker symbol "
            "is NOT). Explain the reasoning, not just the pattern. Third person / descriptive framing "
            "only ('investors with this profile often...'), never a direct instruction to the reader."
        )
    )
    tradeoffs_to_watch: str = Field(
        description="The tradeoffs and risks that come with the approaches just described - never present one style as strictly better with no downside."
    )
    closing_note: str = Field(
        description=(
            "A brief closing reminder that this is general education about common patterns, not "
            "personalized financial advice, and that a licensed financial advisor is the right "
            "resource for actual personal decisions."
        )
    )


class StrategyOverview(BaseModel):
    sections: StrategyOverviewSections


SYSTEM_PROMPT = """You are explaining, to someone with zero finance background, what investing \
approaches are COMMONLY ASSOCIATED with a given risk profile and experience level. This is general \
financial education about patterns and reasoning - not personalized advice for this specific reader.

Ground rules (non-negotiable):
- NEVER name a specific stock, ETF, fund, or ticker symbol. Speak only in general terms (e.g. \
"growth-oriented sectors," "broad market index funds," "dividend-paying companies") - never a proper \
name or symbol a reader could go buy.
- NEVER say "you should" do anything. Every sentence describing an approach must be framed as what \
investors with this profile commonly do or consider, not an instruction to the reader.
- Every approach you describe must be paired with its tradeoff or risk in the same response - never \
present one style as simply better with no downside.
- Write at a reading level a curious teenager could follow. Short sentences. Define any unavoidable \
financial term inline the first time you use it.
- End by being explicit that this is general education, not personalized financial advice, and that \
a licensed financial advisor is the right resource for actual personal decisions.

This reader's profile:
- Risk profile: {risk_profile_label}
- Investing experience: {experience_label}
"""


@groq_retry
def _invoke_structured(prompt: str) -> StrategyOverview:
    structured_llm = get_llm().with_structured_output(StrategyOverview)
    return structured_llm.invoke(prompt)


def generate_strategy_overview(
    risk_profile: RiskProfileLabel, investing_experience: InvestingExperience
) -> StrategyOverview:
    prompt = SYSTEM_PROMPT.format(
        risk_profile_label=_RISK_PROFILE_LABELS[risk_profile],
        experience_label=_EXPERIENCE_LABELS[investing_experience],
    )
    return _invoke_structured(prompt)
