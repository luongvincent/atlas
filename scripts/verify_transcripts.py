"""Fetch the latest transcript for every ticker in config/tickers.py and
report basic quality stats (found/not-found, turn counts, prepared/qa
split). Useful for re-checking source health after fool.com layout
changes, or before scaling ingestion to a new ticker roster.

Usage:
    python scripts/verify_transcripts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.tickers import SUPPORTED_TICKERS
from ingestion.base import TranscriptNotFoundError
from ingestion.motley_fool_source import MotleyFoolSource


def main() -> None:
    source = MotleyFoolSource()
    print(f"{'ticker':<6} {'status':<10} {'quarter':<12} {'turns':>6} {'prepared':>9} {'qa':>5}")
    for ticker_info in SUPPORTED_TICKERS:
        ticker = ticker_info.ticker
        try:
            transcript = source.fetch_latest_transcript(ticker)
        except TranscriptNotFoundError as exc:
            print(f"{ticker:<6} {'NOT_FOUND':<10} {str(exc)[:12]:<12}")
            continue
        except Exception as exc:  # noqa: BLE001 - report and keep going
            print(f"{ticker:<6} {'ERROR':<10} {type(exc).__name__}: {exc}")
            continue

        prepared = sum(1 for t in transcript.turns if t.section == "prepared_remarks")
        qa = sum(1 for t in transcript.turns if t.section == "qa")
        flag = "  <-- check" if prepared == 0 or qa == 0 else ""
        print(
            f"{ticker:<6} {'OK':<10} {transcript.quarter:<12} "
            f"{len(transcript.turns):>6} {prepared:>9} {qa:>5}{flag}"
        )


if __name__ == "__main__":
    main()
