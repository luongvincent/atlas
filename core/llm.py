"""Groq LLM client with retry/backoff for free-tier rate limits.

Free-tier Groq accounts hit 429s under normal load, not just abuse - the
retry policy below is a normal part of operating within that tier, not a
fallback for exceptional failures.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache

from groq import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError
from langchain_core.exceptions import OutputParserException
from langchain_groq import ChatGroq
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import get_settings

logger = logging.getLogger(__name__)

# llama-3.3-70b-versatile (the brief's pick) was removed from Groq's catalog (404 model_not_found);
# openai/gpt-oss-120b replaces it and supports .with_structured_output(). If this 404s again,
# re-check `Groq().models.list()`.
MODEL_NAME = "openai/gpt-oss-120b"

# OutputParserException: gpt-oss occasionally emits malformed JSON for structured output; a resample fixes it.
RETRYABLE_ERRORS = (
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OutputParserException,
)


@lru_cache
def get_llm() -> ChatGroq:
    settings = get_settings()
    # gpt-oss spends completion tokens on reasoning before the JSON; Groq's default cap
    # sometimes runs out first (400 json_validate_failed), so set it explicitly.
    return ChatGroq(api_key=settings.groq_api_key, model=MODEL_NAME, temperature=0.2, max_tokens=16384)


def invoke_structured(schema: type[BaseModel], prompt: str):
    """Structured output via json_schema (gpt-oss often ignores tool calling).

    gpt-oss sometimes wraps the object in a one-element list; unwrap that
    instead of failing. Anything else unparseable still raises
    OutputParserException, which groq_retry resamples.
    """
    result = get_llm().with_structured_output(schema, method="json_schema", include_raw=True).invoke(prompt)
    if result["parsed"] is not None:
        return result["parsed"]
    try:
        data = json.loads(result["raw"].content)
        if isinstance(data, list) and len(data) == 1:
            return schema.model_validate(data[0])
    except (ValueError, ValidationError):
        pass
    raise OutputParserException(f"Could not parse {schema.__name__}: {result['parsing_error']}")


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
