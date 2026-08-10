"""Admin script: upsert config/tickers.py into the public.tickers table.

Uses the service role key - run manually, server-side, never as part of a
request handler.

Usage:
    python scripts/seed_tickers.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.tickers import SUPPORTED_TICKERS
from core.supabase_client import get_admin_client


def main() -> None:
    client = get_admin_client()
    rows = [
        {
            "ticker": t.ticker,
            "company_name": t.company_name,
            "avg_daily_volume": t.avg_daily_volume,
            "exchange": t.exchange,
        }
        for t in SUPPORTED_TICKERS
    ]
    result = client.table("tickers").upsert(rows, on_conflict="ticker").execute()
    print(f"Upserted {len(result.data)} tickers.")


if __name__ == "__main__":
    main()
