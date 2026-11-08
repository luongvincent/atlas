"""RAG chain that turns retrieved transcript chunks into a plain-language
explanation, grounded and cited.
"""

from __future__ import annotations

import logging
import re
from typing import Literal

from langchain_core.documents import Document
from pydantic import BaseModel, Field

from core.llm import groq_retry, invoke_structured
from core.vector_store import get_vector_store

logger = logging.getLogger(__name__)

PREPARED_REMARKS_QUERY = "financial results revenue earnings per share guidance outlook margins growth"
QA_QUERY = "analyst question concern risk challenge skepticism pushback"
CHUNKS_PER_SECTION = 8
# Bump whenever SYSTEM_PROMPT, the retrieval queries/k, or the output schema
# change: cached explanations made under a different version are regenerated.
PROMPT_VERSION = "v2"


class NoTranscriptDataError(Exception):
    """Raised when no ingested chunks exist for a ticker/quarter."""


class NoGroundedCitationsError(Exception):
    """Raised when none of the model's citations can be verified against the retrieved chunks."""


class Citation(BaseModel):
    claim: str = Field(description="Short paraphrase of the specific claim this cites")
    speaker: str
    section: Literal["prepared_remarks", "qa"]
    # Optional so explanations cached before grounding checks existed still validate.
    chunk_id: str | None = None
    quote: str | None = None


class _CitationDraft(BaseModel):
    """What the LLM emits; resolved into a verified Citation by _resolve_citations."""

    claim: str = Field(description="Short paraphrase of the specific claim this cites")
    excerpt_label: str = Field(description="Label of the excerpt it came from, exactly as shown, e.g. P3 or Q2")
    quote: str = Field(description="A short passage (under 200 characters) copied word for word from that excerpt")


class ExplanationSections(BaseModel):
    what_happened: str = Field(
        description="Headline numbers in plain English (revenue, profit, growth, etc.), 2-4 sentences."
    )
    what_management_said: str = Field(
        description=(
            "What management said about guidance and outlook, in plain English. "
            "Explicitly flag hedged or cautious language (e.g. 'we expect' vs 'we are confident')."
        )
    )
    what_analysts_pushed_back_on: str = Field(
        description="What analysts challenged, questioned, or were skeptical about during Q&A."
    )
    why_it_matters: str = Field(
        description="Plain-language takeaway for a regular investor with zero finance background. No jargon."
    )


class Explanation(BaseModel):
    sections: ExplanationSections
    citations: list[Citation]


class _LLMExplanation(BaseModel):
    sections: ExplanationSections
    citations: list[_CitationDraft] = Field(
        description="3 to 8 citations mapping specific claims in the sections above to their transcript source."
    )


SYSTEM_PROMPT = """You are explaining a public company's quarterly earnings call to someone \
with zero finance background - a regular consumer, not an investor or analyst.

Ground rules:
- Use ONLY the transcript excerpts provided below as your source of truth. Never invent numbers, \
guidance, or claims that are not present in them.
- Write at a reading level a curious teenager could follow. Short sentences. No jargon left undefined.
- If you must use an unavoidable financial term (e.g. "gross margin", "guidance", "EPS"), define it \
inline in plain words the first time you use it.
- Explicitly flag hedged or cautious management language (e.g. "we expect", "we remain confident", \
"headwinds") as hedged, and say plainly what that means for how much to trust the claim.
- For every notable claim you make in the four sections, add a citation giving the label of the excerpt \
it came from (e.g. P3 or Q2) and a short quote copied word for word from that excerpt, so a reader can \
verify it against the transcript. Only cite labels that appear below.
- Do not editorialize or give investment advice ("you should buy/sell"). Explain, don't recommend.

Company: {company_name} ({ticker})
Quarter: {quarter}

Transcript excerpts (prepared remarks):
{prepared_remarks_context}

Transcript excerpts (Q&A):
{qa_context}
"""


def _label_docs(docs: list[Document], prefix: str) -> dict[str, Document]:
    return {f"{prefix}{i}": doc for i, doc in enumerate(docs, start=1)}


def _format_docs(labelled: dict[str, Document]) -> str:
    if not labelled:
        return "(none retrieved)"
    return "\n".join(
        f"- [{label}] ({doc.metadata.get('speaker', 'Unknown')}) {doc.page_content}"
        for label, doc in labelled.items()
    )


def _normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


MIN_QUOTE_PIECE_WORDS = 4


def _quote_in(quote: str, text: str) -> bool:
    """True if the quote appears verbatim in text. Models shorten long quotes with "...", so
    each "..."-separated piece must appear verbatim, in order, and be at least
    MIN_QUOTE_PIECE_WORDS words, so tiny fragments can't be stitched into a misleading quote.
    """
    haystack = _normalize(text)
    pieces = [_normalize(p) for p in re.split(r"\.\.\.|…", quote) if p.strip()]
    if len(pieces) > 1 and any(len(p.split()) < MIN_QUOTE_PIECE_WORDS for p in pieces):
        return False
    pos = 0
    for piece in pieces:
        pos = haystack.find(piece, pos)
        if pos == -1:
            return False
        pos += len(piece)
    return bool(pieces)


def _resolve_citations(drafts: list[_CitationDraft], labelled: dict[str, Document]) -> list[Citation]:
    """Keep only citations whose label points at a retrieved chunk and whose
    quote really appears in it. Speaker/section come from the chunk's own
    metadata, never from the model.
    """
    citations = []
    for draft in drafts:
        doc = labelled.get(draft.excerpt_label.strip().strip("[]").upper())
        quote = draft.quote.strip()
        if doc is None or not quote or not _quote_in(quote, doc.page_content):
            logger.warning("Dropping ungrounded citation (label=%r)", draft.excerpt_label)
            continue
        citations.append(
            Citation(
                claim=draft.claim,
                speaker=doc.metadata.get("speaker", "Unknown"),
                section=doc.metadata["section"],
                chunk_id=doc.id,
                quote=quote,
            )
        )
    return citations


def retrieve_context(ticker: str, quarter: str) -> tuple[list[Document], list[Document]]:
    vector_store = get_vector_store()
    base_filter = {"ticker": ticker, "quarter": quarter}

    prepared_docs = vector_store.similarity_search(
        PREPARED_REMARKS_QUERY,
        k=CHUNKS_PER_SECTION,
        filter={**base_filter, "section": "prepared_remarks"},
    )
    qa_docs = vector_store.similarity_search(
        QA_QUERY,
        k=CHUNKS_PER_SECTION,
        filter={**base_filter, "section": "qa"},
    )
    return prepared_docs, qa_docs


@groq_retry
def _invoke_structured(prompt: str) -> _LLMExplanation:
    return invoke_structured(_LLMExplanation, prompt)


def generate_explanation(ticker: str, quarter: str, company_name: str) -> Explanation:
    prepared_docs, qa_docs = retrieve_context(ticker, quarter)
    if not prepared_docs and not qa_docs:
        raise NoTranscriptDataError(f"No ingested transcript chunks found for {ticker} {quarter}")

    prepared = _label_docs(prepared_docs, "P")
    qa = _label_docs(qa_docs, "Q")
    prompt = SYSTEM_PROMPT.format(
        company_name=company_name,
        ticker=ticker,
        quarter=quarter,
        prepared_remarks_context=_format_docs(prepared),
        qa_context=_format_docs(qa),
    )
    labelled = {**prepared, **qa}
    draft = _invoke_structured(prompt)
    citations = _resolve_citations(draft.citations, labelled)
    if not citations:
        # One retry: a single bad sample shouldn't become a 502.
        logger.warning("No grounded citations for %s %s; retrying once", ticker, quarter)
        draft = _invoke_structured(prompt)
        citations = _resolve_citations(draft.citations, labelled)
    if not citations:
        raise NoGroundedCitationsError(f"No verifiable citations for {ticker} {quarter}")
    return Explanation(sections=draft.sections, citations=citations)
