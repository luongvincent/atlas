"""Sentiment analysis over the ingested earnings-call chunks in Pinecone.

Scores every chunk with VADER (compound score, -1 to +1) and reports the
average per ticker, split by prepared remarks vs Q&A, plus the most
positive/negative speakers. Writes per-chunk scores to sentiment_scores.csv.

shortcut: VADER is a general-purpose lexicon, not finance-tuned - it reads
corporate-speak as mildly positive and misses context (e.g. "headwinds").
Treat scores as relative between tickers/sections, not absolute. Upgrade
to FinBERT or a Groq-based scorer if this needs to be trusted.

Usage:
    python scripts/sentiment_analysis.py [TICKER ...]
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import get_settings
from config.tickers import SUPPORTED_TICKERS
from core.sentiment import fetch_chunks
from core.vector_store import get_pinecone_client

OUT_PATH = Path(__file__).resolve().parent.parent / "sentiment_scores.csv"


def main() -> None:
    tickers = [t.upper() for t in sys.argv[1:]] or [t.ticker for t in SUPPORTED_TICKERS]
    index = get_pinecone_client().Index(get_settings().pinecone_index_name)
    analyzer = SentimentIntensityAnalyzer()

    rows = []
    for ticker in tickers:
        for meta in fetch_chunks(index, ticker):
            score = analyzer.polarity_scores(meta["text"])["compound"]
            rows.append(
                {
                    "ticker": ticker,
                    "quarter": meta.get("quarter", ""),
                    "section": meta.get("section", ""),
                    "speaker": meta.get("speaker", ""),
                    "compound": round(score, 4),
                }
            )

    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticker", "quarter", "section", "speaker", "compound"])
        writer.writeheader()
        writer.writerows(rows)

    by_ticker: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    by_speaker: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in rows:
        by_ticker[r["ticker"]]["all"].append(r["compound"])
        by_ticker[r["ticker"]][r["section"]].append(r["compound"])
        by_speaker[(r["ticker"], r["speaker"])].append(r["compound"])

    def avg(values: list[float]) -> str:
        return f"{mean(values):+.3f}" if values else "   n/a"

    print(f"{'ticker':<6} {'quarter':<10} {'chunks':>6} {'overall':>8} {'prepared':>9} {'qa':>7}")
    quarters = {r["ticker"]: r["quarter"] for r in rows}
    for ticker in tickers:
        s = by_ticker.get(ticker)
        if not s:
            print(f"{ticker:<6} no chunks found")
            continue
        print(
            f"{ticker:<6} {quarters[ticker]:<10} {len(s['all']):>6} {avg(s['all']):>8} "
            f"{avg(s.get('prepared_remarks', [])):>9} {avg(s.get('qa', [])):>7}"
        )

    # Speakers with >= 3 chunks, so one lucky sentence doesn't top the list.
    speakers = sorted(
        ((k, mean(v), len(v)) for k, v in by_speaker.items() if len(v) >= 3), key=lambda x: x[1]
    )
    print("\nMost negative speakers:")
    for (t, sp), m, n in speakers[:5]:
        print(f"  {m:+.3f}  {t:<5} {sp} ({n} chunks)")
    print("Most positive speakers:")
    for (t, sp), m, n in speakers[-5:][::-1]:
        print(f"  {m:+.3f}  {t:<5} {sp} ({n} chunks)")
    print(f"\nPer-chunk scores: {OUT_PATH}")


if __name__ == "__main__":
    main()
