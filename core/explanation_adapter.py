"""Cheap, deterministic tone/depth adaptation for GET /explain.

No second LLM call - see CLAUDE.md step 6 for why. This runs per-request
on the already-generated-or-cached base explanation; it never touches
what's written to cached_explanations, so the expensive RAG+Groq step
still only happens once per (ticker, quarter).
"""

from __future__ import annotations

import re

from pydantic import BaseModel

from core.explainer_chain import ExplanationSections
from core.risk_profile import InvestingExperience, RiskProfileContext, RiskProfileLabel


class GlossaryEntry(BaseModel):
    term: str
    definition: str


# Small, hand-picked list of the jargon most likely to show up in earnings
# call explanations. This is a skimmable second pass for beginners - the
# base explanation (core/explainer_chain.py's system prompt) already
# defines jargon inline the first time it's used, so this isn't exhaustive.
_GLOSSARY: dict[str, str] = {
    "guidance": "management's own forecast of how the business will perform going forward.",
    "gross margin": "the percentage of revenue left after subtracting the direct cost of making the product or service.",
    "operating margin": "the percentage of revenue left after subtracting both production costs and day-to-day running costs.",
    "eps": "earnings per share - the company's profit divided by the number of shares outstanding.",
    "earnings per share": "the company's profit divided by the number of shares outstanding.",
    "revenue": "total money the company brought in from sales, before any costs are subtracted.",
    "free cash flow": "cash left over after the company pays for its normal operations and equipment.",
    "year-over-year": "compared to the same period one year ago.",
    "yoy": "short for 'year-over-year' - compared to the same period one year ago.",
    "headwinds": "factors working against the business, such as rising costs or weak demand.",
    "tailwinds": "factors helping the business, such as falling costs or strong demand.",
    "buyback": "the company using its own cash to repurchase its own shares, which can boost the stock price.",
    "backlog": "orders a company has received but hasn't yet fulfilled or booked as revenue.",
    "churn": "the rate at which customers stop using the product or service.",
    "ebitda": "profit before subtracting interest, taxes, and non-cash accounting charges - a rough proxy for core operating profit.",
    "capex": "capital expenditure - money spent on long-term physical assets like equipment or facilities.",
}

_TONE_NOTES: dict[RiskProfileLabel, str] = {
    "conservative": (
        "Since you've told us you prefer to play it safe, focus on whether this quarter makes the "
        "company's finances more or less stable - not on short-term stock price swings."
    ),
    "moderate": (
        "Given your moderate risk comfort, weigh both the growth story and the risks management "
        "flagged above before deciding what this means for you."
    ),
    "aggressive": (
        "Since you're comfortable with higher risk, the bigger question for you is whether the "
        "growth story here is accelerating or slowing - short-term wobbles matter less."
    ),
}

# Depth: only beginners get the glossary appendix. Intermediate/experienced
# callers already get the base (zero-finance-background) explanation and
# don't need it repeated.
_SHOW_GLOSSARY_FOR: frozenset[InvestingExperience] = frozenset({"none", "beginner"})


def _detect_glossary_terms(text: str) -> list[GlossaryEntry]:
    lowered = text.lower()
    entries: list[GlossaryEntry] = []
    for term, definition in _GLOSSARY.items():
        if re.search(r"\b" + re.escape(term) + r"\b", lowered):
            entries.append(GlossaryEntry(term=term, definition=definition))
    return entries


def adapt_sections(
    sections: ExplanationSections,
    risk_ctx: RiskProfileContext | None,
) -> tuple[ExplanationSections, list[GlossaryEntry]]:
    """Returns (possibly adapted) sections and a glossary list (may be empty).

    risk_ctx is None whenever the caller is anonymous or hasn't completed
    the onboarding quiz - in that case the base explanation is returned
    unchanged.
    """
    if risk_ctx is None:
        return sections, []

    glossary: list[GlossaryEntry] = []
    if risk_ctx.investing_experience in _SHOW_GLOSSARY_FOR:
        combined_text = " ".join(
            [
                sections.what_happened,
                sections.what_management_said,
                sections.what_analysts_pushed_back_on,
                sections.why_it_matters,
            ]
        )
        glossary = _detect_glossary_terms(combined_text)

    tone_note = _TONE_NOTES[risk_ctx.risk_profile]
    adapted = sections.model_copy(update={"why_it_matters": f"{sections.why_it_matters} {tone_note}"})
    return adapted, glossary
