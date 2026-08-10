"""RAG chain that turns retrieved transcript chunks into a plain-language
explanation, grounded and cited.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.documents import Document
from pydantic import BaseModel, Field

from core.llm import get_llm, groq_retry
from core.vector_store import get_vector_store

PREPARED_REMARKS_QUERY = "financial results revenue earnings per share guidance outlook margins growth"
QA_QUERY = "analyst question concern risk challenge skepticism pushback"
CHUNKS_PER_SECTION = 8


class NoTranscriptDataError(Exception):
    """Raised when no ingested chunks exist for a ticker/quarter."""


class Citation(BaseModel):
    claim: str = Field(description="Short paraphrase of the specific claim this cites")
    speaker: str = Field(description="Exactly who said it, as given in the transcript excerpts")
    section: Literal["prepared_remarks", "qa"]


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
    citations: list[Citation] = Field(
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
- For every notable claim you make in the four sections, add a citation entry recording who said it \
and whether it was during prepared remarks or Q&A, so a reader can verify it against the transcript.
- Do not editorialize or give investment advice ("you should buy/sell"). Explain, don't recommend.

Company: {company_name} ({ticker})
Quarter: {quarter}

Transcript excerpts (prepared remarks):
{prepared_remarks_context}

Transcript excerpts (Q&A):
{qa_context}
"""


def _format_docs(docs: list[Document]) -> str:
    if not docs:
        return "(none retrieved)"
    lines = []
    for doc in docs:
        speaker = doc.metadata.get("speaker", "Unknown")
        lines.append(f"- ({speaker}) {doc.page_content}")
    return "\n".join(lines)


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
def _invoke_structured(prompt: str) -> Explanation:
    structured_llm = get_llm().with_structured_output(Explanation)
    return structured_llm.invoke(prompt)


def generate_explanation(ticker: str, quarter: str, company_name: str) -> Explanation:
    prepared_docs, qa_docs = retrieve_context(ticker, quarter)
    if not prepared_docs and not qa_docs:
        raise NoTranscriptDataError(f"No ingested transcript chunks found for {ticker} {quarter}")

    prompt = SYSTEM_PROMPT.format(
        company_name=company_name,
        ticker=ticker,
        quarter=quarter,
        prepared_remarks_context=_format_docs(prepared_docs),
        qa_context=_format_docs(qa_docs),
    )
    return _invoke_structured(prompt)
