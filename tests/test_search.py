import pytest

from api.routes import search as search_module
from core.symbols import is_us_symbol, is_valid_symbol


def test_us_symbols():
    for ok in ["AMD", "TSLA", "F", "BRK-B"]:
        assert is_us_symbol(ok)
    for bad in ["", "tsla", "TSLA.TO", "AMD=X", "TOOLONG", "A B", "AMD;DROP", "../x", "BRK-BB"]:
        assert not is_us_symbol(bad)


def test_valid_symbols_also_allow_canadian_listings():
    for ok in ["AMD", "BRK-B", "XEQT.TO", "DLR-U.TO", "FBAL.NE", "ABC.V"]:
        assert is_valid_symbol(ok)
    for bad in ["", "xeqt.to", "XEQT.XX", "XEQT.", ".TO", "XEQT.TO.TO", "AMD=X", "AMD;DROP", "../x"]:
        assert not is_valid_symbol(bad)


@pytest.mark.parametrize(
    "name,expected",
    [
        ("ProShares UltraPro QQQ", True),
        ("ProShares UltraPro Short QQQ", True),
        ("ProShares Ultra S&P500", True),
        ("ProShares Short S&P500", True),
        ("T-Rex 2X Inverse Tesla Daily Target ETF", True),
        ("BetaPro 3x Nasdaq-100 Daily Leveraged Bull ETF", True),
        ("Vanguard Ultra-Short Bond ETF", False),
        ("iShares Short Maturity Bond ETF", False),
        ("SPDR S&P 500 ETF Trust", False),
        ("iShares 20+ Year Treasury Bond ETF", False),
    ],
)
def test_leveraged_name_heuristic(name, expected):
    assert (search_module.LEVERAGED_NAME.search(name) is not None) is expected


class FakeSearch:
    def __init__(self, *args, **kwargs):
        self.quotes = [
            {"symbol": "TSLA", "longname": "Tesla, Inc.", "quoteType": "EQUITY", "exchDisp": "NASDAQ"},
            {"symbol": "STSLA=F", "shortname": "Tesla futures", "quoteType": "FUTURE"},
            {"symbol": "TSLZ", "shortname": "T-Rex 2X Inverse Tesla", "quoteType": "ETF", "exchDisp": "BATS"},
            {"symbol": "TSLA.TO", "shortname": "TESLA CDR", "quoteType": "EQUITY", "exchDisp": "Toronto"},
            {"symbol": "XEQT.TO", "shortname": "iShares Core Equity ETF Portfolio", "quoteType": "ETF"},
            {"symbol": "AAPL", "shortname": "Apple Inc.", "quoteType": "EQUITY", "exchDisp": "NASDAQ"},
        ]


def test_stock_search_keeps_only_us_stocks_and_reports_etfs_separately(monkeypatch):
    monkeypatch.setattr(search_module.yf, "Search", FakeSearch)
    response = search_module._search("tesla", "stock")

    assert [r.ticker for r in response.results] == ["TSLA", "AAPL"]
    assert response.results[0].supported is False  # outside the top 15
    assert response.results[1].supported is True
    assert [r.ticker for r in response.other_matches] == ["TSLZ", "XEQT.TO"]


def test_etf_search_allows_canadian_listings_and_flags_leveraged(monkeypatch):
    monkeypatch.setattr(search_module.yf, "Search", FakeSearch)
    response = search_module._search("tesla", "etf")

    by_ticker = {r.ticker: r for r in response.results}
    assert list(by_ticker) == ["TSLZ", "XEQT.TO"]
    assert by_ticker["TSLZ"].leveraged is True
    assert by_ticker["XEQT.TO"].leveraged is False
    assert by_ticker["XEQT.TO"].supported is True  # on the curated Canadian list
    assert [r.ticker for r in response.other_matches] == ["TSLA", "AAPL"]
