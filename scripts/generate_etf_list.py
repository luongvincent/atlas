"""One-off setup script: determine the top 15 US ETFs by average daily
trading volume, and print a hardcoded Python list to paste into
config/etf_tickers.py.

Deliberately excludes leveraged/inverse "trading" products (2x/3x bull or
bear ETFs, daily-target funds) - Yahoo tags these with a category starting
"Trading--" (e.g. "Trading--Leveraged Equity"). Raw volume rankings are
dominated by these (TSLL, TQQQ, SQQQ, etc.), which are daily-reset
derivatives unsuitable for buy-and-hold - the opposite of this app's
family/retirement-planning focus. Same spirit as excluding SPCX from the
individual-stock roster in generate_ticker_list.py.

This is NOT run at request time - the app imports the static result from
config/etf_tickers.py. Re-run manually if the roster needs refreshing.

Usage:
    python scripts/generate_etf_list.py
"""

from __future__ import annotations

import sys

import yfinance as yf
from yfinance import ETFQuery

TARGET_COUNT = 15
CANDIDATE_POOL_SIZE = 60
EXCLUDED_CATEGORY_PREFIX = "Trading--"
# Yahoo's `category` field isn't reliably populated for every fund (e.g.
# "Defiance Daily Target 2X Short" came back with an empty category) - this
# is a second line of defense, matching on the fund name itself for the
# vocabulary leveraged/inverse/single-stock-daily products consistently use.
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
)


def fetch_etf_candidates(pool_size: int) -> list[str]:
    """Pull a candidate pool of US ETFs ranked by day volume from Yahoo's screener."""
    query = ETFQuery("and", [ETFQuery("eq", ["region", "us"]), ETFQuery("gt", ["intradayprice", 1])])
    result = yf.screen(query, sortField="dayvolume", sortAsc=False, size=pool_size)
    quotes = result.get("quotes", [])
    return [q["symbol"] for q in quotes if "symbol" in q]


def filter_mainstream_etfs(symbols: list[str]) -> list[dict]:
    """Keep only non-leveraged/non-inverse ETFs, ranked by average volume."""
    results = []
    tickers = yf.Tickers(" ".join(symbols))
    for symbol in symbols:
        try:
            info = tickers.tickers[symbol].info
        except Exception as exc:  # noqa: BLE001 - best effort during setup
            print(f"  skip {symbol}: {exc}", file=sys.stderr)
            continue

        category = info.get("category") or ""
        name = info.get("shortName") or info.get("longName") or symbol
        name_lower = f" {name.lower()} "

        if category.startswith(EXCLUDED_CATEGORY_PREFIX):
            print(f"  skip {symbol}: leveraged/inverse trading product (category={category!r})", file=sys.stderr)
            continue
        if any(pattern in name_lower for pattern in EXCLUDED_NAME_PATTERNS):
            print(f"  skip {symbol}: leveraged/inverse trading product (name={name!r})", file=sys.stderr)
            continue

        avg_volume = info.get("averageDailyVolume10Day") or info.get("averageVolume")
        if not avg_volume:
            continue

        results.append(
            {
                "ticker": symbol,
                "name": info.get("shortName") or info.get("longName") or symbol,
                "avg_daily_volume": int(avg_volume),
                "exchange": info.get("exchange", ""),
                "category": category,
            }
        )

    results.sort(key=lambda r: r["avg_daily_volume"], reverse=True)
    return results


def main() -> None:
    print("Fetching ETF candidate pool by day volume from Yahoo Finance...")
    candidates = fetch_etf_candidates(CANDIDATE_POOL_SIZE)
    print(f"  {len(candidates)} candidates: {candidates}")

    print("Filtering out leveraged/inverse trading products...")
    ranked = filter_mainstream_etfs(candidates)
    top = ranked[:TARGET_COUNT]

    print(f"\nTop {len(top)} mainstream ETFs by average daily volume:\n")
    for row in top:
        print(f"  {row['ticker']:<6} {row['avg_daily_volume']:>15,}  {row['name']} ({row['category']})")

    print("\n--- Paste into config/etf_tickers.py ---\n")
    print("SUPPORTED_ETFS: list[EtfInfo] = [")
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
