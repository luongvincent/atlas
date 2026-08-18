"""Static roster of supported Canadian (TSX/NEO) ETFs.

Generated via scripts/generate_etf_list_ca.py, ranked by volume WITHIN
the Canadian market on its own terms - Canadian ETFs (even huge index
funds like XIU/XEQT) trade at a small fraction of US ETF volume, so a
single combined US+CAD list by raw volume would just be 15 US ETFs. See
config/etf_tickers.py for that list.

Filtering is name-pattern-only (leveraged/inverse products, single-stock
CDRs), NOT category-based - Yahoo's `category` field is essentially
never populated for Canadian-listed funds, unlike the US screener. For
the same reason, `category` here is filled in BY HAND (not scraped) -
verified against each fund's actual top holdings via `funds_data` rather
than guessed from the name alone, since a couple of names are misleading
(e.g. "Hamilton Utilities Yield Maximizer" holds CN Rail and Waste
Connections alongside pipelines/utilities). Re-verify if the roster
changes.

Notable: VFV (Vanguard S&P 500 Index ETF), despite being one of the most
commonly recommended funds for Canadian retail investors, does NOT crack
this list - its average volume (~213k) falls just short of the #15 cutoff
(~443k). That's a real result of ranking by trading volume, not a bug:
VFV is more of a buy-and-hold-and-forget fund for most holders than a
heavily-traded one. Left out deliberately rather than manually inserted,
to keep this list's "top 15 by volume, determined programmatically"
premise consistent with the individual-stock roster's.

Re-run the generator script to refresh this list.
"""

from __future__ import annotations

from config.etf_tickers import EtfInfo

SUPPORTED_ETFS_CA: list[EtfInfo] = [
    EtfInfo(ticker="XIU.TO", name="iShares S&P/TSX 60 Index ETF", avg_daily_volume=3_350_300, exchange="TOR", category="Large Blend"),
    EtfInfo(ticker="XEG.TO", name="iShares S&P/TSX Capped Energy Index ETF", avg_daily_volume=2_024_330, exchange="TOR", category="Energy"),
    EtfInfo(ticker="DLR.TO", name="Global X U.S. Dollar Currency ETF", avg_daily_volume=1_246_650, exchange="TOR", category="Currency"),
    EtfInfo(ticker="MSTE.TO", name="Harvest Strategy Inc. Enhanced High Income Shares ETF", avg_daily_volume=1_120_810, exchange="TOR", category="Covered Call"),
    EtfInfo(ticker="ZEB.TO", name="BMO Equal Weight Banks Index ETF", avg_daily_volume=1_111_540, exchange="TOR", category="Financials"),
    EtfInfo(ticker="DLR-U.TO", name="Global X U.S. Dollar Currency ETF", avg_daily_volume=939_150, exchange="TOR", category="Currency"),
    EtfInfo(ticker="HHIS.TO", name="Harvest Diversified High Income Shares ETF", avg_daily_volume=803_860, exchange="TOR", category="Covered Call"),
    EtfInfo(ticker="UMAX.TO", name="Hamilton Utilities Yield Maximizer ETF", avg_daily_volume=679_860, exchange="TOR", category="Utilities"),
    EtfInfo(ticker="XEQT.TO", name="iShares Core Equity ETF Portfolio", avg_daily_volume=655_320, exchange="TOR", category="Global Equity"),
    EtfInfo(ticker="FBAL.NE", name="Fidelity All-in-One Balanced ETF", avg_daily_volume=640_426, exchange="NEO", category="Balanced"),
    EtfInfo(ticker="RING.TO", name="Global X Equal Weight Canadian Telecommunications Index ETF", avg_daily_volume=619_350, exchange="TOR", category="Telecom"),
    EtfInfo(ticker="XGD.TO", name="iShares S&P/TSX Global Gold Index ETF", avg_daily_volume=593_310, exchange="TOR", category="Gold Mining"),
    EtfInfo(ticker="UTES.TO", name="Evolve Canadian Utilities Enhanced Yield Index Fund", avg_daily_volume=593_250, exchange="TOR", category="Utilities"),
    EtfInfo(ticker="ZAG.TO", name="BMO Aggregate Bond Index ETF", avg_daily_volume=557_060, exchange="TOR", category="Fixed Income"),
    EtfInfo(ticker="BANK.TO", name="Evolve Canadian Banks and Lifecos Enhanced Yield Index Fund", avg_daily_volume=442_600, exchange="TOR", category="Financials"),
]

ETFS_CA_BY_SYMBOL: dict[str, EtfInfo] = {e.ticker: e for e in SUPPORTED_ETFS_CA}
