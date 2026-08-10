"""Scraper interface. Every transcript source (Motley Fool today, company IR
pages or something else later) implements this so the rest of the pipeline
(chunking/embedding, step 4) never depends on where the text came from.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ingestion.models import Transcript


class TranscriptNotFoundError(Exception):
    """Raised when no transcript could be located for a ticker."""


class TranscriptSource(ABC):
    @abstractmethod
    def fetch_latest_transcript(self, ticker: str) -> Transcript:
        """Return the most recent earnings call transcript for `ticker`.

        Raises TranscriptNotFoundError if none can be located.
        """
