from core.explainer_chain import ExplanationSections
from core.explanation_adapter import adapt_sections, find_jargon
from core.risk_profile import RiskProfileContext

SECTIONS = ExplanationSections(
    what_happened="Revenue grew 10% year-over-year to $5B, beating guidance.",
    what_management_said="Management gave cautious guidance, citing headwinds in EPS growth.",
    what_analysts_pushed_back_on="Analysts pushed back on gross margin softness.",
    why_it_matters="This quarter shows steady growth.",
)


def test_find_jargon_works_for_everyone_without_risk_context():
    terms = {entry.term for entry in find_jargon(SECTIONS)}
    assert {"revenue", "year-over-year", "guidance", "headwinds", "eps", "gross margin"} <= terms
    assert "churn" not in terms


def test_no_risk_context_returns_sections_unchanged():
    adapted, glossary = adapt_sections(SECTIONS, None)
    assert adapted == SECTIONS
    assert glossary == []


def test_beginner_gets_glossary_and_tone_note():
    ctx = RiskProfileContext(investing_experience="beginner", risk_profile="conservative")
    adapted, glossary = adapt_sections(SECTIONS, ctx)
    terms = {entry.term for entry in glossary}
    assert "revenue" in terms
    assert "year-over-year" in terms
    assert "eps" in terms  # "EPS growth" appears in what_management_said
    assert "gross margin" in terms
    assert "headwinds" in terms
    assert adapted.why_it_matters.startswith(SECTIONS.why_it_matters)
    assert "play it safe" in adapted.why_it_matters


def test_experienced_gets_no_glossary_but_still_gets_tone_note():
    ctx = RiskProfileContext(investing_experience="experienced", risk_profile="aggressive")
    adapted, glossary = adapt_sections(SECTIONS, ctx)
    assert glossary == []
    assert "growth story" in adapted.why_it_matters


def test_original_sections_object_not_mutated():
    ctx = RiskProfileContext(investing_experience="beginner", risk_profile="moderate")
    original_why = SECTIONS.why_it_matters
    adapt_sections(SECTIONS, ctx)
    assert SECTIONS.why_it_matters == original_why
