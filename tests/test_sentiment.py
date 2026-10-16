from core.sentiment import score_chunks


def _chunk(quarter: str, section: str, text: str) -> dict:
    return {"quarter": quarter, "section": section, "text": text}


def test_scores_only_latest_quarter():
    chunks = [
        _chunk("Q1 2027", "prepared_remarks", "This was a terrible, disastrous quarter."),
        _chunk("Q2 2027", "prepared_remarks", "We had a wonderful, excellent quarter."),
        _chunk("Q2 2027", "qa", "Great question, we are very happy and optimistic."),
    ]
    result = score_chunks("TEST", chunks)
    assert result.quarter == "Q2 2027"
    assert result.chunk_count == 2
    assert result.overall > 0.5


def test_quarter_ordering_crosses_years():
    chunks = [_chunk("Q4 2026", "qa", "Good."), _chunk("Q1 2027", "qa", "Good.")]
    assert score_chunks("TEST", chunks).quarter == "Q1 2027"


def test_missing_section_is_none_and_empty_is_none():
    result = score_chunks("TEST", [_chunk("Q1 2026", "qa", "Great results.")])
    assert result.prepared_remarks is None and result.qa is not None
    assert score_chunks("TEST", []) is None
