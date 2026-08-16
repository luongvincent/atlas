from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from core.ticker_stats import _safe_float, fetch_ticker_stats


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        (float("nan"), None),
        ("not-a-number", None),
        (2.5, 2.5),
        ("3.1", 3.1),
    ],
)
def test_safe_float(value, expected):
    assert _safe_float(value) == expected


@patch("core.ticker_stats._risk_free_rate", return_value=0.04)
@patch("core.ticker_stats.yf.Ticker")
def test_fetch_ticker_stats_pulls_fundamentals_from_info(mock_ticker_cls, _mock_rf):
    stock = MagicMock()
    stock.info = {
        "trailingPE": 35.0,
        "priceToBook": 41.5,
        "trailingPegRatio": 2.47,
        "dividendYield": 0.35,
        "beta": 1.1,
    }
    index = pd.date_range("2026-01-01", periods=40, freq="D")
    # Oscillating-but-net-upward series so there are real down days too -
    # Sortino needs at least some downside volatility to be defined.
    stock_closes = [100 + i * 0.2 + (1.5 if i % 3 == 0 else -0.8) for i in range(40)]
    stock.history.return_value = pd.DataFrame({"Close": stock_closes}, index=index)

    benchmark = MagicMock()
    bench_closes = [4000 + i + (5 if i % 4 == 0 else -3) for i in range(40)]
    benchmark.history.return_value = pd.DataFrame({"Close": bench_closes}, index=index)

    def ticker_side_effect(symbol):
        return benchmark if symbol == "^GSPC" else stock

    mock_ticker_cls.side_effect = ticker_side_effect

    stats = fetch_ticker_stats("AAPL")

    assert stats.pe_ratio == 35.0
    assert stats.pb_ratio == 41.5
    assert stats.peg_ratio == 2.47
    assert stats.dividend_yield == 0.35
    assert stats.beta == 1.1
    assert stats.sharpe_ratio is not None
    assert stats.sortino_ratio is not None
    assert stats.alpha is not None


@patch("core.ticker_stats._risk_free_rate", return_value=0.04)
@patch("core.ticker_stats.yf.Ticker")
def test_fetch_ticker_stats_handles_missing_fundamentals(mock_ticker_cls, _mock_rf):
    stock = MagicMock()
    stock.info = {}  # nothing available for this ticker
    stock.history.return_value = pd.DataFrame({"Close": []})

    mock_ticker_cls.return_value = stock

    stats = fetch_ticker_stats("ZZZZ")

    assert stats.pe_ratio is None
    assert stats.pb_ratio is None
    assert stats.peg_ratio is None
    assert stats.dividend_yield is None
    assert stats.beta is None
    assert stats.sharpe_ratio is None
    assert stats.sortino_ratio is None
    assert stats.alpha is None
