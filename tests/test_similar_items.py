from config.etf_tickers import SUPPORTED_ETFS
from config.etf_tickers_ca import SUPPORTED_ETFS_CA
from config.tickers import SUPPORTED_TICKERS
from core.similar_items import get_similar_items


def test_unsupported_ticker_returns_empty():
    assert get_similar_items("NOTREAL") == []


def test_stock_prefers_same_industry_over_same_sector_only():
    # NVDA and INTC are both Technology/Semiconductors; AAPL is Technology
    # but Consumer Electronics - same-industry match should outrank
    # same-sector-only.
    items = get_similar_items("NVDA")
    tickers = [i.ticker for i in items]
    assert "INTC" in tickers
    assert tickers.index("INTC") < (tickers.index("AAPL") if "AAPL" in tickers else len(tickers))


def test_stock_never_recommends_itself():
    items = get_similar_items("AAPL")
    assert "AAPL" not in [i.ticker for i in items]
    assert all(i.kind == "stock" for i in items)


def test_us_etf_matches_stay_within_us_roster():
    items = get_similar_items("BITO")  # Digital Assets, along with IBIT/ETHA
    tickers = {i.ticker for i in items}
    assert tickers.issubset({e.ticker for e in SUPPORTED_ETFS})
    assert "IBIT" in tickers or "ETHA" in tickers
    assert all(i.kind == "etf" for i in items)


def test_ca_etf_matches_stay_within_ca_roster():
    items = get_similar_items("XIU.TO")
    tickers = {i.ticker for i in items}
    assert tickers.issubset({e.ticker for e in SUPPORTED_ETFS_CA})


def test_every_supported_item_is_lookupable_without_error():
    for t in SUPPORTED_TICKERS:
        get_similar_items(t.ticker)
    for e in SUPPORTED_ETFS + SUPPORTED_ETFS_CA:
        get_similar_items(e.ticker)
