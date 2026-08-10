from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Section = Literal["prepared_remarks", "qa"]


class TranscriptTurn(BaseModel):
    speaker: str
    title: str | None = None
    section: Section
    text: str


class Transcript(BaseModel):
    ticker: str
    company_name: str
    quarter: str
    call_date: str
    source_url: str
    participants: dict[str, str]
    turns: list[TranscriptTurn]
