from core.risk_profile import derive_risk_profile


def test_conservative_profile():
    assert (
        derive_risk_profile(
            investing_experience="none",
            time_horizon="short_term",
            risk_comfort=1,
            goals="preserve_capital",
        )
        == "conservative"
    )


def test_aggressive_profile():
    assert (
        derive_risk_profile(
            investing_experience="experienced",
            time_horizon="long_term",
            risk_comfort=5,
            goals="speculation",
        )
        == "aggressive"
    )


def test_moderate_profile():
    assert (
        derive_risk_profile(
            investing_experience="intermediate",
            time_horizon="medium_term",
            risk_comfort=3,
            goals="income",
        )
        == "moderate"
    )


def test_risk_comfort_dominates_weighting():
    # Same everything else, only risk_comfort swings low vs high - since it's
    # weighted double, it should be able to move the bucket on its own.
    low = derive_risk_profile(
        investing_experience="intermediate",
        time_horizon="medium_term",
        risk_comfort=1,
        goals="income",
    )
    high = derive_risk_profile(
        investing_experience="intermediate",
        time_horizon="medium_term",
        risk_comfort=5,
        goals="income",
    )
    assert low != high


def test_result_is_always_valid_label():
    experiences = ["none", "beginner", "intermediate", "experienced"]
    horizons = ["short_term", "medium_term", "long_term"]
    goals = ["preserve_capital", "income", "growth", "speculation"]
    for exp in experiences:
        for horizon in horizons:
            for goal in goals:
                for comfort in range(1, 6):
                    result = derive_risk_profile(
                        investing_experience=exp,
                        time_horizon=horizon,
                        risk_comfort=comfort,
                        goals=goal,
                    )
                    assert result in {"conservative", "moderate", "aggressive"}
