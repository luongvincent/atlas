from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from yfinance.exceptions import YFDataException

from core.etf_holdings import NoHoldingsDataError, fetch_holdings


@patch("core.etf_holdings.yf.Ticker")
def test_fetch_holdings_returns_top_holdings_and_sectors(mock_ticker_cls):
    funds_data = MagicMock()
    funds_data.top_holdings = pd.DataFrame(
        {"Name": ["NVIDIA Corp", "Apple Inc"], "Holding Percent": [0.0755, 0.0704]},
        index=pd.Index(["NVDA", "AAPL"], name="Symbol"),
    )
    funds_data.sector_weightings = {"technology": 0.374, "financial_services": 0.1224, "energy": 0.0}
    mock_ticker_cls.return_value.funds_data = funds_data

    holdings = fetch_holdings("SPY")

    assert holdings.ticker == "SPY"
    assert len(holdings.top_holdings) == 2
    assert holdings.top_holdings[0].ticker == "NVDA"
    assert holdings.top_holdings[0].weight_percent == 7.55
    # sectors sorted descending by weight, zero-weight sectors dropped
    assert [s.sector for s in holdings.sector_weightings] == ["Technology", "Financial Services"]


@patch("core.etf_holdings.yf.Ticker")
def test_fetch_holdings_caps_at_max_holdings(mock_ticker_cls):
    funds_data = MagicMock()
    funds_data.top_holdings = pd.DataFrame(
        {"Name": [f"Company {i}" for i in range(20)], "Holding Percent": [0.01] * 20},
        index=pd.Index([f"SYM{i}" for i in range(20)], name="Symbol"),
    )
    funds_data.sector_weightings = {}
    mock_ticker_cls.return_value.funds_data = funds_data

    holdings = fetch_holdings("QQQ")

    assert len(holdings.top_holdings) == 10


@patch("core.etf_holdings.yf.Ticker")
def test_fetch_holdings_raises_for_non_fund_ticker(mock_ticker_cls):
    funds_data = MagicMock()
    type(funds_data).top_holdings = property(
        lambda self: (_ for _ in ()).throw(YFDataException("AAPL: No Fund data found."))
    )
    mock_ticker_cls.return_value.funds_data = funds_data

    with pytest.raises(NoHoldingsDataError):
        fetch_holdings("AAPL")
