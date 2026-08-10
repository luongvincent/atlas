"""Turn a scraped Transcript into embeddable LangChain Documents.

Chunking is done per turn, not by blindly splitting the whole transcript,
so every chunk keeps exactly one speaker/section in its metadata - the
explainer (step 5) needs to say "management said X" or "an analyst pushed
back with Y" and cite where it came from, which only works if a chunk
never blends two speakers together. Turns longer than CHUNK_SIZE (a few
executives ramble well past that) are split further with
RecursiveCharacterTextSplitter, and each resulting sub-chunk keeps the
same speaker/section metadata plus a chunk_index.
"""

from __future__ import annotations

import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ingestion.models import Transcript, TranscriptTurn

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

_NON_BREAKING_SPACE = " "
_ZERO_WIDTH_SPACE = "​"

_WHITESPACE_RE = re.compile(r"[ \t]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    text = text.replace(_NON_BREAKING_SPACE, " ").replace(_ZERO_WIDTH_SPACE, "")
    text = _WHITESPACE_RE.sub(" ", text)
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def _turn_id(transcript: Transcript, turn_index: int, chunk_index: int) -> str:
    return f"{transcript.ticker}:{transcript.quarter}:{turn_index}:{chunk_index}"


def _turn_to_documents(transcript: Transcript, turn: TranscriptTurn, turn_index: int) -> list[Document]:
    text = clean_text(turn.text)
    if not text:
        return []

    base_metadata = {
        "ticker": transcript.ticker,
        "quarter": transcript.quarter,
        "company_name": transcript.company_name,
        "call_date": transcript.call_date,
        "source_url": transcript.source_url,
        "section": turn.section,
        "speaker": turn.speaker,
        "title": turn.title or "",
    }

    if len(text) <= CHUNK_SIZE:
        pieces = [text]
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        pieces = splitter.split_text(text)

    documents = []
    for chunk_index, piece in enumerate(pieces):
        speaker_prefix = f"{turn.speaker} ({turn.title}): " if turn.title else f"{turn.speaker}: "
        documents.append(
            Document(
                id=_turn_id(transcript, turn_index, chunk_index),
                page_content=f"{speaker_prefix}{piece}",
                metadata={**base_metadata, "chunk_index": chunk_index},
            )
        )
    return documents


def transcript_to_documents(transcript: Transcript) -> list[Document]:
    documents: list[Document] = []
    for turn_index, turn in enumerate(transcript.turns):
        documents.extend(_turn_to_documents(transcript, turn, turn_index))
    return documents
