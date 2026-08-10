"""Motley Fool transcript scraper.

Discovery: fool.com has no public per-ticker transcript API, and its
"/earnings-call-transcripts/" index page ignores its own ?page= parameter
(every page returns the same ~20 most-recent items - confirmed by
inspection, not documented anywhere), so it can only ever surface a
ticker's transcript if it was published in roughly the last day. Instead
we walk fool.com's monthly XML sitemaps (https://www.fool.com/sitemap/
YYYY/MM, discovered via robots.txt), which list every article published
that month including transcripts, and match the ticker against the URL
slug (e.g. ".../apple-aapl-q3-2026-earnings-call-transcript/"). Slugs vary
("...-earnings-call-transcript" vs "...-earnings-transcript", and the
ticker is sometimes the first slug segment with no company-name prefix at
all, e.g. "aal-q1-2026-earnings-transcript") so the pattern tolerates both.
Sitemap results are cached per source instance since a full run looks up
many tickers against the same handful of monthly sitemaps.

Parsing: transcript pages mark each turn as <p><strong>Speaker:</strong>
text...</p>; continuation paragraphs (no leading <strong>) are appended to
the previous turn. The prepared-remarks/Q&A boundary is the first turn
where the speaker is literally "Operator" - Motley Fool's operator always
introduces the first analyst question, which is a more reliable signal
than looking for a "Questions and Answers" heading (not every transcript
has one).
"""

from __future__ import annotations

import re
import time
from datetime import date

import requests
from bs4 import BeautifulSoup, Tag

from config.tickers import TICKERS_BY_SYMBOL
from ingestion.base import TranscriptNotFoundError, TranscriptSource
from ingestion.models import Transcript, TranscriptTurn

SITEMAP_URL_TEMPLATE = "https://www.fool.com/sitemap/{year}/{month:02d}"
SITEMAP_MONTHS_TO_SCAN = 6  # covers a full quarter of reporting with buffer
SITEMAP_LOC_RE = re.compile(r"<loc>(.*?)</loc>")

REQUEST_TIMEOUT = 20
USER_AGENT = "Mozilla/5.0 (compatible; EarningsCallExplainer/0.1)"

# Page <h1>/<title> text, e.g. "Apple (AAPL) Q3 2026 Earnings Call Transcript".
TITLE_RE = re.compile(
    r"^(?P<company>.+?)\s*\((?P<ticker>[A-Z.\-]{1,6})\)\s*"
    r"Q(?P<quarter>\d)\s*(?P<year>\d{4})\s*Earnings(?: Call)? Transcript",
    re.IGNORECASE,
)

# Fallback for tickers with no company-name prefix at all, e.g.
# "AAL Q1 2026 Earnings Transcript".
TITLE_RE_TICKER_ONLY = re.compile(
    r"^(?P<ticker>[A-Z.\-]{1,6})\s+Q(?P<quarter>\d)\s+(?P<year>\d{4})\s+Earnings(?: Call)? Transcript",
    re.IGNORECASE,
)

# Participant list separators seen in the wild: " - ", " – " (en dash), " — " (em dash).
PARTICIPANT_SEP_RE = re.compile(r"\s+[-–—]\s+")

# Phrases that signal a move from prepared remarks into Q&A, for transcripts
# with no live "Operator" turn (e.g. Palantir's investor-question format,
# where the IR host reads submitted questions instead).
QA_TRANSITION_RE = re.compile(
    r"first question"
    r"|go(?:ing)? to questions?"
    r"|open(?:ing)? (?:up )?(?:the )?(?:call|floor|lines?) (?:to|for) questions?"
    r"|open(?:ing)? (?:up )?(?:the )?lines?\b"
    r"|questions? and answers?"
    r"|q\s*&\s*a\b"
    r"|take (?:your|the) first question"
    r"|begin (?:the )?question",
    re.IGNORECASE,
)

# URL slug, e.g. ".../apple-aapl-q3-2026-earnings-call-transcript/" or
# ".../aal-q1-2026-earnings-transcript/" (no company-name prefix).
def _transcript_url_pattern(ticker: str) -> re.Pattern[str]:
    return re.compile(
        rf"/(?:[a-z0-9]+-)*{re.escape(ticker.lower())}-q(\d)-(\d{{4}})"
        rf"-earnings(?:-call)?-transcript/?$"
    )


class MotleyFoolSource(TranscriptSource):
    def __init__(self, session: requests.Session | None = None, request_delay_seconds: float = 0.5):
        self._session = session or requests.Session()
        self._session.headers.setdefault("User-Agent", USER_AGENT)
        self._request_delay_seconds = request_delay_seconds
        self._sitemap_transcript_urls: list[str] | None = None

    def fetch_latest_transcript(self, ticker: str) -> Transcript:
        url = self._find_latest_transcript_url(ticker)
        if url is None:
            raise TranscriptNotFoundError(f"No Motley Fool transcript found for {ticker!r}")
        html = self._get(url)
        return self._parse_transcript(ticker=ticker, url=url, html=html)

    # -- discovery --

    def _find_latest_transcript_url(self, ticker: str) -> str | None:
        pattern = _transcript_url_pattern(ticker)
        best: tuple[int, int, str] | None = None  # (year, quarter, url)
        for url in self._recent_transcript_urls():
            match = pattern.search(url)
            if not match:
                continue
            year, quarter = int(match.group(2)), int(match.group(1))
            if best is None or (year, quarter) > (best[0], best[1]):
                best = (year, quarter, url)
        return best[2] if best else None

    def _recent_transcript_urls(self) -> list[str]:
        if self._sitemap_transcript_urls is not None:
            return self._sitemap_transcript_urls

        urls: list[str] = []
        today = date.today()
        year, month = today.year, today.month
        for _ in range(SITEMAP_MONTHS_TO_SCAN):
            xml = self._get(SITEMAP_URL_TEMPLATE.format(year=year, month=month))
            urls.extend(loc for loc in SITEMAP_LOC_RE.findall(xml) if "/earnings/call-transcripts/" in loc)
            month -= 1
            if month == 0:
                month, year = 12, year - 1

        self._sitemap_transcript_urls = urls
        return urls

    # -- fetching --

    def _get(self, url: str) -> str:
        time.sleep(self._request_delay_seconds)
        response = self._session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text

    # -- parsing --

    def _parse_transcript(self, ticker: str, url: str, html: str) -> Transcript:
        soup = BeautifulSoup(html, "lxml")
        h1 = soup.find("h1")
        header_text = h1.get_text(strip=True) if h1 else ""
        match = TITLE_RE.match(header_text)
        if match:
            company_name = match.group("company").strip()
            quarter = f"Q{match.group('quarter')} {match.group('year')}"
        else:
            ticker_only_match = TITLE_RE_TICKER_ONLY.match(header_text)
            if ticker_only_match:
                quarter = f"Q{ticker_only_match.group('quarter')} {ticker_only_match.group('year')}"
            else:
                quarter = "unknown"
            ticker_info = TICKERS_BY_SYMBOL.get(ticker.upper())
            company_name = ticker_info.company_name if ticker_info else ticker.upper()

        body = soup.select_one("div.article-body")
        if body is None:
            raise TranscriptNotFoundError(f"Could not locate article body for {url}")

        call_date = self._extract_section_text(body, "DATE") or ""
        participants = self._extract_participants(body)
        turns = self._extract_turns(body, participants)

        if not turns:
            raise TranscriptNotFoundError(f"Parsed 0 transcript turns from {url}")

        return Transcript(
            ticker=ticker.upper(),
            company_name=company_name,
            quarter=quarter,
            call_date=call_date,
            source_url=url,
            participants=participants,
            turns=turns,
        )

    @staticmethod
    def _extract_section_text(body: Tag, heading: str) -> str | None:
        h2 = body.find("h2", string=lambda s: bool(s) and s.strip().upper() == heading)
        if h2 is None:
            return None
        sibling = h2.find_next_sibling()
        return sibling.get_text(" ", strip=True) if sibling else None

    @staticmethod
    def _extract_participants(body: Tag) -> dict[str, str]:
        h2 = body.find("h2", string=lambda s: bool(s) and s.strip().upper() == "CALL PARTICIPANTS")
        if h2 is None:
            return {}
        ul = h2.find_next_sibling("ul")
        if ul is None:
            return {}
        participants: dict[str, str] = {}
        for li in ul.find_all("li"):
            text = li.get_text(" ", strip=True)
            parts = PARTICIPANT_SEP_RE.split(text)
            if len(parts) >= 2:
                title, name = parts[0], parts[-1]
                participants[name.strip()] = title.strip()
        return participants

    @staticmethod
    def _extract_turns(body: Tag, participants: dict[str, str]) -> list[TranscriptTurn]:
        transcript_heading = body.find(
            "h2", string=lambda s: bool(s) and "transcript" in s.strip().lower()
        )
        paragraphs = (
            transcript_heading.find_next_siblings("p")
            if transcript_heading is not None
            else body.find_all("p")
        )

        # Pass 1: turn boundaries only (speaker, text), no section yet -
        # the Q&A boundary depends on the whole sequence, not just what's
        # been seen so far (see pass 2 below).
        raw_turns: list[tuple[str, str]] = []
        for p in paragraphs:
            strong = p.find("strong")
            full_text = p.get_text(" ", strip=True)
            speaker_label = strong.get_text(strip=True) if strong else ""

            is_speaker_turn = (
                strong is not None
                and speaker_label.endswith(":")
                and full_text.startswith(speaker_label)
            )
            if is_speaker_turn:
                speaker = speaker_label.rstrip(":").strip()
                text = full_text[len(speaker_label):].strip()
                raw_turns.append((speaker, text))
            elif raw_turns:
                # Continuation paragraph of the previous speaker's turn.
                prev_speaker, prev_text = raw_turns[-1]
                raw_turns[-1] = (prev_speaker, f"{prev_text}\n\n{full_text}")
            # else: stray paragraph before any speaker turn (e.g. legal
            # disclaimers) - not attributable to a speaker, so skip it.

        # Pass 2: find the Q&A boundary index.
        #
        # Preferred signal: the first "Operator" turn, after at least one
        # non-operator speaker, whose own text mentions "question" - some
        # calls open with the operator's boilerplate ("Good morning, I
        # will be your conference operator today...") before any executive
        # speaks, and others have the operator hand off to each executive
        # by name throughout the prepared remarks too, so neither "first
        # Operator turn" nor "any later Operator turn" alone is reliable;
        # requiring the operator to actually be talking about questions is.
        qa_start_index: int | None = None
        seen_non_operator_speaker = False
        for i, (speaker, text) in enumerate(raw_turns):
            if (
                speaker.lower() == "operator"
                and seen_non_operator_speaker
                and re.search(r"\bquestion", text, re.IGNORECASE)
            ):
                qa_start_index = i
                break
            if speaker.lower() != "operator":
                seen_non_operator_speaker = True

        # Fallback: transcripts with no live "Operator" turn at all (e.g.
        # Palantir's, where the IR host relays investor questions
        # directly) - look for a transition phrase instead. Turn 0 is
        # skipped: it's almost always the moderator's intro, which often
        # previews the Q&A format ("we'll open the call to questions")
        # without that being the actual transition.
        if qa_start_index is None:
            for i, (_speaker, text) in enumerate(raw_turns):
                if i > 0 and QA_TRANSITION_RE.search(text):
                    qa_start_index = i + 1
                    break

        turns = [
            TranscriptTurn(
                speaker=speaker,
                title=participants.get(speaker),
                section="qa" if qa_start_index is not None and i >= qa_start_index else "prepared_remarks",
                text=text,
            )
            for i, (speaker, text) in enumerate(raw_turns)
        ]
        return turns
