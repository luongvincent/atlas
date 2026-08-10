from ingestion.motley_fool_source import MotleyFoolSource

SAMPLE_HTML = """
<html><body>
<h1>Example Co (EX) Q2 2026 Earnings Call Transcript</h1>
<div class="article-body">
<h2>DATE</h2>
<p>Monday, January 5, 2026 at 5:00 p.m. ET</p>
<h2>CALL PARTICIPANTS</h2>
<ul>
<li>Chief Executive Officer - Jane Smith</li>
<li>Chief Financial Officer — John Doe</li>
</ul>
<h2>Full Conference Call Transcript</h2>
<p><strong>Jane Smith:</strong> Good afternoon, thanks for joining.</p>
<p>We had a great quarter across the board.</p>
<p><strong>John Doe:</strong> Thanks Jane. Revenue was up 10%.</p>
<p><strong>Operator:</strong> We will now take our first question from Alex Analyst.</p>
<p><strong>Alex Analyst:</strong> Can you walk through the margin trend?</p>
<p><strong>Jane Smith:</strong> Sure, happy to.</p>
</div>
</body></html>
"""


def test_parses_participants_turns_and_qa_boundary():
    source = MotleyFoolSource()
    transcript = source._parse_transcript(ticker="EX", url="https://example.com/x", html=SAMPLE_HTML)

    assert transcript.company_name == "Example Co"
    assert transcript.quarter == "Q2 2026"
    assert transcript.participants == {
        "Jane Smith": "Chief Executive Officer",
        "John Doe": "Chief Financial Officer",
    }

    assert len(transcript.turns) == 5
    assert transcript.turns[0].speaker == "Jane Smith"
    assert transcript.turns[0].section == "prepared_remarks"
    # Continuation paragraph (no <strong>) merges into the previous turn.
    assert "great quarter" in transcript.turns[0].text

    assert transcript.turns[1].speaker == "John Doe"
    assert transcript.turns[1].section == "prepared_remarks"
    assert transcript.turns[1].title == "Chief Financial Officer"

    # Operator turn mentioning "question" after a non-operator speaker
    # marks the qa boundary; everything from here on is qa.
    assert transcript.turns[2].speaker == "Operator"
    assert transcript.turns[2].section == "qa"
    assert transcript.turns[3].section == "qa"
    assert transcript.turns[4].section == "qa"


def test_ticker_only_title_falls_back_to_config_company_name():
    html = SAMPLE_HTML.replace(
        "<h1>Example Co (EX) Q2 2026 Earnings Call Transcript</h1>",
        "<h1>AAPL Q2 2026 Earnings Transcript</h1>",
    )
    source = MotleyFoolSource()
    transcript = source._parse_transcript(ticker="AAPL", url="https://example.com/x", html=html)

    assert transcript.company_name == "Apple Inc."
    assert transcript.quarter == "Q2 2026"
