"""Admin script: list the most-requested tickers from public.explanation_requests.

Uses the service role key (it has to read every user's rows) - run manually,
server-side, never as part of a request handler. Prints counts only, never
user IDs.

Usage:
    python scripts/list_requests.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.supabase_client import get_admin_client


def main() -> None:
    client = get_admin_client()
    # shortcut: reads at most 1000 rows (Supabase's default page size), upgrade to paging if requests pass that.
    rows = client.table("explanation_requests").select("ticker, created_at").execute().data

    if not rows:
        print("No explanation requests yet.")
        return

    counts: dict[str, int] = defaultdict(int)
    latest: dict[str, str] = {}
    for row in rows:
        counts[row["ticker"]] += 1
        latest[row["ticker"]] = max(latest.get(row["ticker"], ""), row["created_at"])

    ranked = sorted(counts, key=lambda t: (-counts[t], t))
    print(f"{'TICKER':<8}{'REQUESTS':>9}  LATEST")
    for ticker in ranked:
        print(f"{ticker:<8}{counts[ticker]:>9}  {latest[ticker][:10]}")

    print(f"\n{len(ranked)} tickers, {len(rows)} requests. To add the top ones:")
    print(f"    python scripts/run_ingestion.py {' '.join(ranked[:3])}")


if __name__ == "__main__":
    main()
