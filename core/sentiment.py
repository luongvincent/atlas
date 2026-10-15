"""Sentiment of the latest ingested earnings call, scored per chunk with VADER.

shortcut: VADER is a general-purpose lexicon, not finance-tuned - it reads
corporate-speak as mildly positive and misses context ("headwinds"). Scores
are only meaningful relative to other tickers/sections. Upgrade to FinBERT
or a Groq scorer if they need to be trusted.
shortcut: computed on first request and cached in-process (lost on restart);
move to a Supabase table written at ingestion time if that gets slow.
"""

from __future__ import annotations

from functools import lru_cache
from statistics import mean

from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import get_settings
from core.vector_store import _pinecone_client


class SentimentResult(BaseModel):
    ticker: str
    quarter: str
    chunk_count: int
    overall: float  # VADER compound average, -1 to +1
    prepared_remarks: float | None
    qa: float | None


def fetch_chunks(index, ticker: str) -> list[dict]:
    """All stored chunks for a ticker. Ids are '<ticker>:<quarter>:<turn>:<chunk>'."""
    ids = [i for page in index.list(prefix=f"{ticker}:") for i in page]
    chunks = []
    for start in range(0, len(ids), 100):
        fetched = index.fetch(ids=ids[start : start + 100])
        chunks.extend(v.metadata for v in fetched.vectors.values())
    return chunks


def _quarter_key(quarter: str) -> tuple[int, int]:
    """'Q2 2027' -> (2027, 2), so max() picks the most recent quarter."""
    q, year = quarter.split()
    return int(year), int(q[1:])


def score_chunks(ticker: str, chunks: list[dict]) -> SentimentResult | None:
    """Scores only the most recent quarter - older calls can linger in Pinecone."""
    if not chunks:
        return None
    latest = max((c["quarter"] for c in chunks), key=_quarter_key)
    analyzer = SentimentIntensityAnalyzer()
    scores: dict[str, list[float]] = {"prepared_remarks": [], "qa": []}
    for c in chunks:
        if c["quarter"] == latest:
            scores[c["section"]].append(analyzer.polarity_scores(c["text"])["compound"])

    all_scores = scores["prepared_remarks"] + scores["qa"]
    return SentimentResult(
        ticker=ticker,
        quarter=latest,
        chunk_count=len(all_scores),
        overall=round(mean(all_scores), 3),
        prepared_remarks=round(mean(scores["prepared_remarks"]), 3) if scores["prepared_remarks"] else None,
        qa=round(mean(scores["qa"]), 3) if scores["qa"] else None,
    )


@lru_cache(maxsize=64)
def get_sentiment(ticker: str) -> SentimentResult | None:
    index = _pinecone_client().Index(get_settings().pinecone_index_name)
    return score_chunks(ticker, fetch_chunks(index, ticker))
