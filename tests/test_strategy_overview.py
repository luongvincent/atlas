import pytest

from core.risk_profile import InvestingExperience, RiskProfileLabel
from core.strategy_overview import (
    SYSTEM_PROMPT,
    _EXPERIENCE_LABELS,
    _RISK_PROFILE_LABELS,
)

ALL_RISK_PROFILES: tuple[RiskProfileLabel, ...] = ("conservative", "moderate", "aggressive")
ALL_EXPERIENCES: tuple[InvestingExperience, ...] = ("none", "beginner", "intermediate", "experienced")


def test_every_risk_profile_has_a_label():
    for profile in ALL_RISK_PROFILES:
        assert profile in _RISK_PROFILE_LABELS
        assert _RISK_PROFILE_LABELS[profile]


def test_every_experience_has_a_label():
    for experience in ALL_EXPERIENCES:
        assert experience in _EXPERIENCE_LABELS
        assert _EXPERIENCE_LABELS[experience]


@pytest.mark.parametrize("risk_profile", ALL_RISK_PROFILES)
@pytest.mark.parametrize("investing_experience", ALL_EXPERIENCES)
def test_prompt_formats_for_every_combination(risk_profile, investing_experience):
    # All 12 (risk_profile, investing_experience) combinations must format
    # cleanly - this is the exact set migrations/009_cached_strategy_overviews.sql
    # can hold rows for, so a KeyError here would mean a live 500 for real users.
    prompt = SYSTEM_PROMPT.format(
        risk_profile_label=_RISK_PROFILE_LABELS[risk_profile],
        experience_label=_EXPERIENCE_LABELS[investing_experience],
    )
    assert _RISK_PROFILE_LABELS[risk_profile] in prompt
    assert _EXPERIENCE_LABELS[investing_experience] in prompt


def test_system_prompt_never_asks_for_ticker_recommendations():
    # Guard against a future edit accidentally softening the core
    # constraint this whole feature exists to enforce.
    lowered = SYSTEM_PROMPT.lower()
    assert "never name a specific stock" in lowered
    assert 'never say "you should"' in lowered
