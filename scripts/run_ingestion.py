"""Admin script: ingest the latest transcript for every supported ticker
into Pinecone. Offline/manual - never called from a request handler.

Usage:
    python scripts/run_ingestion.py
    python scripts/run_ingestion.py AAPL NVDA   # subset, for testing
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.tickers import SUPPORTED_TICKERS
from ingestion.motley_fool_source import MotleyFoolSource
from ingestion.pipeline import ingest_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    requested = sys.argv[1:]
    tickers = [t.upper() for t in requested] if requested else [t.ticker for t in SUPPORTED_TICKERS]

    source = MotleyFoolSource()
    results = ingest_all(tickers, source)

    print(f"\n{'ticker':<6} {'result':<40}")
    for ticker, result in results.items():
        print(f"{ticker:<6} {result}")


if __name__ == "__main__":
    main()
