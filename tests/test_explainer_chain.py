import pytest
from langchain_core.documents import Document

from core import explainer_chain as chain
from core.explainer_chain import ExplanationSections, NoGroundedCitationsError, _CitationDraft, _LLMExplanation

SECTIONS = ExplanationSections(
    what_happened="Revenue grew.",
    what_management_said="Cautious.",
    what_analysts_pushed_back_on="Margins.",
    why_it_matters="Steady.",
)


def _doc(id, text, section, speaker):
    return Document(id=id, page_content=text, metadata={"section": section, "speaker": speaker})


PREPARED = [_doc("AAPL:Q1 2026:0:0", "Jane Doe (CFO): Revenue grew  12% to\n$5B.", "prepared_remarks", "Jane Doe")]
QA = [_doc("AAPL:Q1 2026:7:0", "Bob (Analyst): Why are margins shrinking?", "qa", "Bob")]


def _run(monkeypatch, drafts):
    monkeypatch.setattr(chain, "retrieve_context", lambda t, q: (PREPARED, QA))
    monkeypatch.setattr(chain, "_invoke_structured", lambda prompt: _LLMExplanation(sections=SECTIONS, citations=drafts))
    return chain.generate_explanation("AAPL", "Q1 2026", "Apple")


def test_valid_citation_takes_speaker_section_and_id_from_the_chunk(monkeypatch):
    # Whitespace/case differences in the quote are tolerated; the model-supplied label is the only trust input.
    result = _run(monkeypatch, [_CitationDraft(claim="Sales up", excerpt_label="p1", quote="revenue grew 12% to $5B.")])
    (c,) = result.citations
    assert (c.chunk_id, c.speaker, c.section) == ("AAPL:Q1 2026:0:0", "Jane Doe", "prepared_remarks")


def test_invented_quote_or_label_is_dropped(monkeypatch):
    drafts = [
        _CitationDraft(claim="ok", excerpt_label="Q1", quote="why are margins shrinking?"),
        _CitationDraft(claim="made up", excerpt_label="Q1", quote="profits tripled"),
        _CitationDraft(claim="bad label", excerpt_label="P9", quote="revenue grew"),
    ]
    result = _run(monkeypatch, drafts)
    assert [c.claim for c in result.citations] == ["ok"]


def test_no_verifiable_citations_raises(monkeypatch):
    with pytest.raises(NoGroundedCitationsError):
        _run(monkeypatch, [_CitationDraft(claim="x", excerpt_label="P1", quote="not in the transcript")])


def _run_sequence(monkeypatch, attempts):
    calls = iter(attempts)
    monkeypatch.setattr(chain, "retrieve_context", lambda t, q: (PREPARED, QA))
    monkeypatch.setattr(
        chain, "_invoke_structured", lambda prompt: _LLMExplanation(sections=SECTIONS, citations=next(calls))
    )
    return chain.generate_explanation("AAPL", "Q1 2026", "Apple")


BAD = [_CitationDraft(claim="x", excerpt_label="P1", quote="not in the transcript")]
GOOD = [_CitationDraft(claim="ok", excerpt_label="Q1", quote="why are margins shrinking?")]


def test_one_bad_attempt_is_retried(monkeypatch):
    assert [c.claim for c in _run_sequence(monkeypatch, [BAD, GOOD]).citations] == ["ok"]


def test_two_bad_attempts_still_raise(monkeypatch):
    with pytest.raises(NoGroundedCitationsError):
        _run_sequence(monkeypatch, [BAD, BAD])


def test_quote_shortened_with_ellipsis_verifies_only_when_every_piece_is_verbatim_and_in_order():
    from core.explainer_chain import _quote_in

    text = "Concerns with asset quality will always remain and they should remain. Credit risk is first in our priority list."
    assert _quote_in("concerns with asset quality will always remain... credit risk is first in our priority list.", text)
    assert _quote_in("Concerns with asset quality will always remain … Credit risk is first", text)
    assert not _quote_in("credit risk is first in our ... concerns with asset quality will always", text)  # wrong order
    assert not _quote_in("concerns with asset quality will always remain... profits tripled this year", text)  # invented piece
    assert not _quote_in("asset quality... first", text)  # fragments too short to stitch
    assert not _quote_in("...", text)
