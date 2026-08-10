from ingestion.chunking import CHUNK_SIZE, transcript_to_documents
from ingestion.models import Transcript, TranscriptTurn


def _make_transcript(turns: list[TranscriptTurn]) -> Transcript:
    return Transcript(
        ticker="EX",
        company_name="Example Co",
        quarter="Q2 2026",
        call_date="Monday, January 5, 2026",
        source_url="https://example.com/x",
        participants={"Jane Smith": "CEO"},
        turns=turns,
    )


def test_short_turn_becomes_one_chunk_with_speaker_metadata():
    transcript = _make_transcript(
        [TranscriptTurn(speaker="Jane Smith", title="CEO", section="prepared_remarks", text="We had a great quarter.")]
    )
    docs = transcript_to_documents(transcript)

    assert len(docs) == 1
    assert docs[0].metadata["speaker"] == "Jane Smith"
    assert docs[0].metadata["section"] == "prepared_remarks"
    assert docs[0].metadata["ticker"] == "EX"
    assert docs[0].metadata["chunk_index"] == 0
    assert docs[0].page_content.startswith("Jane Smith (CEO): ")


def test_long_turn_splits_into_multiple_chunks_same_speaker():
    long_text = "This is a sentence about the quarter. " * 100  # well past CHUNK_SIZE
    assert len(long_text) > CHUNK_SIZE
    transcript = _make_transcript(
        [TranscriptTurn(speaker="Jane Smith", title="CEO", section="qa", text=long_text)]
    )
    docs = transcript_to_documents(transcript)

    assert len(docs) > 1
    assert all(d.metadata["speaker"] == "Jane Smith" for d in docs)
    assert all(d.metadata["section"] == "qa" for d in docs)
    assert [d.metadata["chunk_index"] for d in docs] == list(range(len(docs)))
    assert all(len(d.page_content) <= CHUNK_SIZE + 100 for d in docs)  # speaker prefix + overlap slack


def test_empty_turn_produces_no_chunks():
    transcript = _make_transcript(
        [TranscriptTurn(speaker="Operator", section="qa", text="   ")]
    )
    docs = transcript_to_documents(transcript)
    assert docs == []


def test_chunk_ids_are_stable_and_unique():
    transcript = _make_transcript(
        [
            TranscriptTurn(speaker="Jane Smith", section="prepared_remarks", text="First turn."),
            TranscriptTurn(speaker="John Doe", section="prepared_remarks", text="Second turn."),
        ]
    )
    docs = transcript_to_documents(transcript)
    ids = [d.id for d in docs]
    assert len(ids) == len(set(ids))
    assert ids == ["EX:Q2 2026:0:0", "EX:Q2 2026:1:0"]
