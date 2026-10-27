from langchain_core.exceptions import OutputParserException

from core.llm import groq_retry


def test_malformed_model_output_is_retried():
    calls = []

    @groq_retry
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise OutputParserException("bad json")
        return "ok"

    flaky.retry.sleep = lambda _: None  # skip the real backoff
    assert flaky() == "ok"
    assert len(calls) == 3


def test_list_wrapped_object_is_unwrapped(monkeypatch):
    import json

    from pydantic import BaseModel

    from core import llm

    class Out(BaseModel):
        a: int

    class FakeLLM:
        def with_structured_output(self, *a, **k):
            return self

        def invoke(self, prompt):
            raw = type("M", (), {"content": json.dumps([{"a": 1}])})()
            return {"raw": raw, "parsed": None, "parsing_error": "list"}

    monkeypatch.setattr(llm, "get_llm", lambda: FakeLLM())
    assert llm.invoke_structured(Out, "p") == Out(a=1)
