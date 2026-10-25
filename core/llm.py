"""Groq LLM client with retry/backoff for free-tier rate limits.

Free-tier Groq accounts hit 429s under normal load, not just abuse - the
retry policy below is a normal part of operating within that tier, not a
fallback for exceptional failures.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from groq import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError
from langchain_groq import ChatGroq
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import get_settings

logger = logging.getLogger(__name__)

# llama-3.3-70b-versatile (the original pick) was removed from Groq's catalog -
# calls returned 404 model_not_found. Re-check `Groq().models.list()` if this 404s again.
# The original brief specified llama-3.3-70b-versatile; Groq deprecated it
# at some point after this project was built (confirmed live: the model no
# longer appears in this account's /models list at all, and calls to it
# 404 with "model_not_found"). openai/gpt-oss-120b is the current
# replacement - verified it supports .with_structured_output() cleanly via
# a live call before switching, since not every hosted model handles
# structured/tool-call output the same way. Re-check Groq's available
# models if this ever breaks again the same way.
MODEL_NAME = "openai/gpt-oss-120b"

RETRYABLE_ERRORS = (RateLimitError, APIConnectionError, APITimeoutError, InternalServerError)


@lru_cache
def get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(api_key=settings.groq_api_key, model=MODEL_NAME, temperature=0.2)


def _log_retry(retry_state) -> None:
    exc = retry_state.outcome.exception()
    logger.warning(
        "Groq call failed (attempt %d), retrying: %s: %s",
        retry_state.attempt_number,
        type(exc).__name__,
        exc,
    )


groq_retry = retry(
    retry=retry_if_exception_type(RETRYABLE_ERRORS),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5),
    before_sleep=_log_retry,
    reraise=True,
)
