"""One-off setup script: determine the top 15 Canadian (TSX/NEO) ETFs by
average daily trading volume, and print a hardcoded Python list to paste
into config/etf_tickers_ca.py.

Ranked WITHIN the Canadian market on its own terms - Canadian ETFs (even
huge index funds like XIU/XEQT/VFV) trade at a small fraction of US ETF
volume (XIU, the largest, still trades ~85x smaller than the smallest US
top-15 ETF), so a single combined US+CAD list by raw volume would just be
15 US ETFs. See generate_etf_list.py for that list.

Filtering here is name-pattern-only, NOT category-based: Yahoo's
`category` field is populated for essentially no Canadian-listed fund
(confirmed empirically - even VFV.TO/XEQT.TO/XIU.TO return category=None),
unlike the US screener where it's usually present. Excludes:
- Leveraged/inverse products (BetaPro, "2x"/"3x", "SavvyLong", etc.)
- Single-stock CDRs (Canadian Depositary Receipts, e.g. "MICRON CDR
  (CAD HEDGED)") - these wrap ONE company, not a diversified basket,
  despite showing up as quoteType ETF.

This is NOT run at request time - the app imports the static result from
config/etf_tickers_ca.py. Re-run manually if the roster needs refreshing.

Usage:
    python scripts/generate_etf_list_ca.py
"""

from __future__ import annotations

import sys

import yfinance as yf
from yfinance import ETFQuery

TARGET_COUNT = 15
CANDIDATE_POOL_SIZE = 80

EXCLUDED_NAME_PATTERNS = (
    "2x",
    "3x",
    "-1x",
    "ultrapro",
    "ultrashort",
    "daily target",
    "daily bull",
    "daily bear",
    " bull ",
    " bear ",
    "leveraged",
    "inverse",
    " short ",
    "lev daily",
    "lvgd",
    "betapro",
    "savvylong",
    "megashort",
    # Single-stock CDRs (Canadian Depositary Receipts) - one company
    # wrapped as a fund, not a diversified basket.
    "cdr",
)


def fetch_etf_candidates(pool_size: int) -> list[str]:
    """Pull a candidate pool of Canadian ETFs ranked by day volume from Yahoo's screener."""
    query = ETFQuery("and", [ETFQuery("eq", ["region", "ca"]), ETFQuery("gt", ["intradayprice", 1])])
    result = yf.screen(query, sortField="dayvolume", sortAsc=False, size=pool_size)
    quotes = result.get("quotes", [])
    return [q["symbol"] for q in quotes if "symbol" in q]


def filter_mainstream_etfs(symbols: list[str]) -> list[dict]:
    """Keep only diversified, non-leveraged/non-inverse ETFs, ranked by average volume."""
    results = []
    tickers = yf.Tickers(" ".join(symbols))
    for symbol in symbols:
        try:
            info = tickers.tickers[symbol].info
        except Exception as exc:  # noqa: BLE001 - best effort during setup
            print(f"  skip {symbol}: {exc}", file=sys.stderr)
            continue

        name = info.get("shortName") or info.get("longName") or symbol
        name_lower = f" {name.lower()} "

        if any(pattern in name_lower for pattern in EXCLUDED_NAME_PATTERNS):
            print(f"  skip {symbol}: leveraged/inverse/single-stock product (name={name!r})", file=sys.stderr)
            continue

        avg_volume = info.get("averageDailyVolume10Day") or info.get("averageVolume")
        if not avg_volume:
            continue

        results.append(
            {
                "ticker": symbol,
                "name": name,
                "avg_daily_volume": int(avg_volume),
                "exchange": info.get("exchange", ""),
                "category": info.get("category") or "",
            }
        )

    results.sort(key=lambda r: r["avg_daily_volume"], reverse=True)
    return results


def main() -> None:
    print("Fetching Canadian ETF candidate pool by day volume from Yahoo Finance...")
    candidates = fetch_etf_candidates(CANDIDATE_POOL_SIZE)
    print(f"  {len(candidates)} candidates: {candidates}")

    print("Filtering out leveraged/inverse/single-stock products...")
    ranked = filter_mainstream_etfs(candidates)
    top = ranked[:TARGET_COUNT]

    print(f"\nTop {len(top)} mainstream Canadian ETFs by average daily volume:\n")
    for row in top:
        print(f"  {row['ticker']:<10} {row['avg_daily_volume']:>12,}  {row['name']}")

    print("\n--- Paste into config/etf_tickers_ca.py ---\n")
    print("SUPPORTED_ETFS_CA: list[EtfInfo] = [")
    for row in top:
        print(
            "    EtfInfo("
            f'ticker="{row["ticker"]}", '
            f'name={row["name"]!r}, '
            f'avg_daily_volume={row["avg_daily_volume"]}, '
            f'exchange="{row["exchange"]}", '
            f'category={row["category"]!r}'
            "),"
        )
    print("]")


if __name__ == "__main__":
    main()
