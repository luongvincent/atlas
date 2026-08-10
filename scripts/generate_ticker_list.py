"""One-off setup script: determine the top 10-15 US tickers by average daily
trading volume, individual companies only (no ETFs / index funds / trusts),
and print a hardcoded Python list to paste into config/tickers.py.

This is NOT run at request time - the app imports the static result from
config/tickers.py. Re-run manually if the roster needs refreshing.

Usage:
    python scripts/generate_ticker_list.py
"""

from __future__ import annotations

import sys

import yfinance as yf

# Excluded quoteTypes: ETF, MUTUALFUND, INDEX, CRYPTOCURRENCY, CURRENCY.
# Only EQUITY (individual operating companies) is kept.
ALLOWED_QUOTE_TYPES = {"EQUITY"}

TARGET_COUNT = 15
CANDIDATE_POOL_SIZE = 60


def fetch_most_active_candidates(pool_size: int) -> list[str]:
    """Pull a candidate pool ranked by volume from Yahoo's screener."""
    screen_result = yf.screen("most_actives", count=pool_size)
    quotes = screen_result.get("quotes", [])
    return [q["symbol"] for q in quotes if "symbol" in q]


def filter_individual_companies(symbols: list[str]) -> list[dict]:
    """Keep only individual operating companies, ranked by average volume."""
    results = []
    tickers = yf.Tickers(" ".join(symbols))
    for symbol in symbols:
        try:
            info = tickers.tickers[symbol].info
        except Exception as exc:  # noqa: BLE001 - best effort during setup
            print(f"  skip {symbol}: {exc}", file=sys.stderr)
            continue

        quote_type = info.get("quoteType")
        if quote_type not in ALLOWED_QUOTE_TYPES:
            continue

        avg_volume = info.get("averageDailyVolume10Day") or info.get("averageVolume")
        if not avg_volume:
            continue

        results.append(
            {
                "ticker": symbol,
                "company_name": info.get("shortName") or info.get("longName") or symbol,
                "avg_daily_volume": int(avg_volume),
                "exchange": info.get("exchange", ""),
            }
        )

    results.sort(key=lambda r: r["avg_daily_volume"], reverse=True)
    return results


def main() -> None:
    print("Fetching most-active candidate pool from Yahoo Finance...")
    candidates = fetch_most_active_candidates(CANDIDATE_POOL_SIZE)
    print(f"  {len(candidates)} candidates: {candidates}")

    print("Filtering to individual companies (quoteType == EQUITY)...")
    ranked = filter_individual_companies(candidates)
    top = ranked[:TARGET_COUNT]

    print(f"\nTop {len(top)} individual-company tickers by average daily volume:\n")
    for row in top:
        print(f"  {row['ticker']:<6} {row['avg_daily_volume']:>15,}  {row['company_name']}")

    print("\n--- Paste into config/tickers.py ---\n")
    print("SUPPORTED_TICKERS: list[TickerInfo] = [")
    for row in top:
        print(
            "    TickerInfo("
            f'ticker="{row["ticker"]}", '
            f'company_name={row["company_name"]!r}, '
            f'avg_daily_volume={row["avg_daily_volume"]}, '
            f'exchange="{row["exchange"]}"'
            "),"
        )
    print("]")


if __name__ == "__main__":
    main()
