from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from core.market_data import _RANGE_TO_YFINANCE, ChartRange, NoChartDataError, fetch_chart_data


def test_every_chart_range_has_a_yfinance_mapping():
    # ChartRange is a Literal - keep this in sync manually if it changes.
    all_ranges: tuple[ChartRange, ...] = ("1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "ALL")
    for r in all_ranges:
        assert r in _RANGE_TO_YFINANCE
        period, interval = _RANGE_TO_YFINANCE[r]
        assert period and interval


@patch("core.market_data.yf.Ticker")
def test_fetch_chart_data_returns_points(mock_ticker_cls):
    index = pd.to_datetime(["2026-01-02", "2026-01-03"])
    history = pd.DataFrame({"Close": [100.123456, 101.5]}, index=index)
    mock_ticker_cls.return_value.history.return_value = history

    points, interval = fetch_chart_data("AAPL", "1M")

    assert interval == "1d"
    assert len(points) == 2
    assert points[0].close == 100.1235  # rounded to 4 decimal places
    mock_ticker_cls.return_value.history.assert_called_once_with(period="1mo", interval="1d")


@patch("core.market_data.yf.Ticker")
def test_fetch_chart_data_drops_nan_rows(mock_ticker_cls):
    index = pd.to_datetime(["2026-01-02", "2026-01-03"])
    history = pd.DataFrame({"Close": [100.0, float("nan")]}, index=index)
    mock_ticker_cls.return_value.history.return_value = history

    points, _ = fetch_chart_data("AAPL", "1D")

    assert len(points) == 1
    assert points[0].close == 100.0


@patch("core.market_data.yf.Ticker")
def test_fetch_chart_data_raises_when_empty(mock_ticker_cls):
    mock_ticker_cls.return_value.history.return_value = pd.DataFrame({"Close": []})

    with pytest.raises(NoChartDataError):
        fetch_chart_data("ZZZZ", "1Y")
