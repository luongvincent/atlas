"""Ingestion pipeline: fetch -> chunk -> embed -> upsert.

This is an offline/admin process (run manually via scripts/run_ingestion.py
or a scheduled job), never triggered by a client request - consistent with
the rest of the app's security posture, where writes to shared/reference
data stay out of request handlers.
"""

from __future__ import annotations

import logging

from ingestion.base import TranscriptNotFoundError, TranscriptSource
from ingestion.chunking import transcript_to_documents
from ingestion.models import Transcript
from core.supabase_client import get_admin_client
from core.vector_store import ensure_index_exists, get_vector_store

logger = logging.getLogger(__name__)

UPSERT_BATCH_SIZE = 100


def _record_latest_call_metadata(transcript: Transcript) -> None:
    """Update tickers.latest_quarter/latest_call_date so /explain and
    /tickers know what's been ingested, without querying Pinecone for it.
    Admin/service-role write - only ever called from this offline pipeline,
    never a request handler. Requires the ticker row to already exist
    (see scripts/seed_tickers.py).
    """
    client = get_admin_client()
    client.table("tickers").update(
        {"latest_quarter": transcript.quarter, "latest_call_date": transcript.call_date}
    ).eq("ticker", transcript.ticker).execute()


def ingest_transcript(transcript: Transcript) -> int:
    """Chunk + embed + upsert a single already-fetched transcript. Returns
    the number of chunks written.
    """
    documents = transcript_to_documents(transcript)
    if not documents:
        logger.warning("No chunks produced for %s %s", transcript.ticker, transcript.quarter)
        return 0

    vector_store = get_vector_store()
    for start in range(0, len(documents), UPSERT_BATCH_SIZE):
        batch = documents[start : start + UPSERT_BATCH_SIZE]
        vector_store.add_documents(batch, ids=[doc.id for doc in batch])

    _record_latest_call_metadata(transcript)

    return len(documents)


def ingest_ticker(ticker: str, source: TranscriptSource) -> int:
    """Fetch a ticker's latest transcript from `source` and ingest it."""
    transcript = source.fetch_latest_transcript(ticker)
    return ingest_transcript(transcript)


def ingest_all(tickers: list[str], source: TranscriptSource) -> dict[str, int | str]:
    """Ingest every ticker, continuing past individual failures. Returns a
    per-ticker result: chunk count on success, error message on failure.
    """
    ensure_index_exists()
    results: dict[str, int | str] = {}
    for ticker in tickers:
        try:
            results[ticker] = ingest_ticker(ticker, source)
            logger.info("Ingested %s: %d chunks", ticker, results[ticker])
        except TranscriptNotFoundError as exc:
            results[ticker] = f"not_found: {exc}"
            logger.warning("No transcript for %s: %s", ticker, exc)
        except Exception as exc:  # noqa: BLE001 - keep going for other tickers
            results[ticker] = f"error: {exc}"
            logger.exception("Failed to ingest %s", ticker)
    return results
