"""RAG vs CAG ablation for Atlas's /ask chain, on evals/atlas_eval_set.json.

Both arms run the production `core.ask_chain.answer_question` unchanged (same prompt, same quote
verification, same resample-then-refuse). Only two things are swapped, here and not in app code:
  - the model call (`_invoke`) goes to Gemini, because a whole transcript (~15K tokens) exceeds
    Groq's free-tier 8K tokens/minute cap;
  - CAG only: retrieval (`_search`) returns the entire transcript in call order instead of top-k chunks.

Stages (resumable; each skips rows already saved in evals/results/):
  run    -> runs.jsonl    answer, verified citations, drafted-citation count, tokens, latency
  judge  -> judged.jsonl  correctness / abstention, graded by Groq gpt-oss-120b (different family from Gemini)
  report -> report.md     per-arm metrics + paired bootstrap CIs (CAG - RAG)

Usage: ./venv/Scripts/python.exe evals/rag_vs_cag.py [run|judge|report|all]
Needs GEMINI_API_KEY (run) and GROQ_API_KEY (judge) in .env.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv

load_dotenv()

import numpy as np

HERE = Path(__file__).resolve().parent
EVAL_SET = HERE / "atlas_eval_set.json"
RESULTS = HERE / "results"
RUNS, JUDGED, REPORT = RESULTS / "runs.jsonl", RESULTS / "judged.jsonl", RESULTS / "report.md"
ARMS = ["rag", "cag"]
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
JUDGE_MODEL = "openai/gpt-oss-120b"
GEMINI_MIN_INTERVAL = float(os.environ.get("GEMINI_MIN_INTERVAL", "6"))  # free-tier RPM pacing


class QuotaExhausted(Exception):
    pass


def _load(path: Path, key) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return {key(r): r for r in map(json.loads, f) if r}


def _append(path: Path, row: dict) -> None:
    RESULTS.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ── Stage 1: run both arms ───────────────────────────────────────────────────

def _transcript_docs(ticker: str, quarter: str):
    """Whole transcript as LangChain Documents in call order (same ids/metadata as retrieval returns)."""
    from langchain_core.documents import Document
    from pinecone import Pinecone

    index = Pinecone(api_key=os.environ["PINECONE_API_KEY"]).Index("earnings-call-transcripts")
    ids = [i for page in index.list(prefix=f"{ticker}:{quarter}:") for i in page]
    docs = []
    for i in range(0, len(ids), 100):
        for vid, v in index.fetch(ids=ids[i:i + 100]).vectors.items():
            meta = dict(v.metadata)
            docs.append(Document(id=vid, page_content=meta.pop("text"), metadata=meta))
    order = lambda d: tuple(int(x) for x in d.id.rsplit(":", 2)[1:])  # (turn, chunk)
    return sorted(docs, key=order)


def stage_run() -> None:
    from google import genai
    from google.genai import errors, types
    from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

    import core.ask_chain as ask

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    usage = {"in": 0, "out": 0, "calls": 0}
    last_call = [0.0]

    def _retryable(exc):
        if isinstance(exc, errors.APIError) and exc.code == 429:
            # The 429 body lists every quota (incl. per-day ones), so judge by the server's retryDelay instead.
            m = re.search(r"retryDelay'?\"?:\s*'?\"?(\d+)", str(exc))
            delay = int(m.group(1)) if m else 60
            if delay > 600:
                raise QuotaExhausted(f"retry in {delay}s: {str(exc)[:200]}")
            time.sleep(delay)
            return True
        return isinstance(exc, errors.APIError) and exc.code in (500, 503)

    @retry(retry=retry_if_exception(_retryable), wait=wait_exponential(min=10, max=90), stop=stop_after_attempt(6), reraise=True)
    def gemini_invoke(prompt: str):
        wait = GEMINI_MIN_INTERVAL - (time.monotonic() - last_call[0])
        if wait > 0:
            time.sleep(wait)
        last_call[0] = time.monotonic()
        resp = client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json",
                                               response_schema=ask._LLMAnswer))
        meta = resp.usage_metadata
        usage["in"] += meta.prompt_token_count or 0
        usage["out"] += meta.candidates_token_count or 0
        usage["calls"] += 1
        if resp.parsed is None:
            return ask._LLMAnswer.model_validate_json(resp.text)
        return resp.parsed

    drafts_seen = []
    real_resolve = ask._resolve_citations

    def counting_resolve(drafts, labelled):
        out = real_resolve(drafts, labelled)
        drafts_seen.append((len(drafts), len(out)))
        return out

    real_search = ask._search
    ask._invoke = gemini_invoke
    ask._resolve_citations = counting_resolve

    items = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    done = _load(RUNS, lambda r: (r["arm"], r["id"]))
    transcripts: dict = {}
    # Question-major order: with ~20 free requests/day, each day's quota yields complete RAG/CAG pairs.
    for it in items:
        for arm in ARMS:
            if (arm, it["id"]) in done:
                continue
            key = (it["ticker"], it["quarter"])
            if arm == "cag":
                if key not in transcripts:
                    transcripts[key] = _transcript_docs(*key)
                ask._search = lambda query, filter, limit, _docs=transcripts[key]: list(_docs)
            else:
                ask._search = real_search
            usage.update({"in": 0, "out": 0, "calls": 0})
            drafts_seen.clear()
            t0 = time.monotonic()
            from config.tickers import TICKERS_BY_SYMBOL
            ans = ask.answer_question(it["ticker"], it["quarter"], TICKERS_BY_SYMBOL[it["ticker"]].company_name,
                                      it["question"], [])
            row = {
                "arm": arm, "id": it["id"], "answer": ans.answer,
                "citations": [c.model_dump() for c in ans.citations],
                "drafted_citations": sum(d for d, _ in drafts_seen),
                "verified_citations": sum(v for _, v in drafts_seen),
                "attempts": len(drafts_seen), "refused": ans.answer == ask.UNGROUNDED_FALLBACK,
                "input_tokens": usage["in"], "output_tokens": usage["out"],
                "seconds": round(time.monotonic() - t0, 2), "model": GEMINI_MODEL,
            }
            _append(RUNS, row)
            print(f"  {arm} q{it['id']:02d} cites={row['verified_citations']}/{row['drafted_citations']} "
                  f"in_tok={row['input_tokens']} {row['seconds']}s", flush=True)


# ── Stage 2: judge ───────────────────────────────────────────────────────────

JUDGE_PROMPT = """You grade an answer about a company's earnings call against a reference answer written from the transcript.

Question: {question}
Reference answer: {reference}
Answer to grade: {answer}

{rubric}
Reply with JSON only: {{"score": <1, 0.5 or 0>, "reason": "<one sentence>"}}"""

RUBRIC_ANSWERABLE = """Score 1 if the answer states the reference's key facts (numbers, names, direction of change) correctly and contradicts none of them.
Score 0.5 if it is partly correct: some key facts are missing, but nothing stated contradicts the reference.
Score 0 if it contradicts the reference, gives wrong numbers, or says the call did not cover it.
Extra detail beyond the reference is fine unless it contradicts the reference."""

RUBRIC_OOS = """The call did NOT cover this topic. Score 1 if the answer says the call did not cover it (or that it can't find it) and does not invent any statement about the topic.
Score 0 if the answer asserts anything about the topic as if the call said it."""


def stage_judge() -> None:
    from groq import Groq, RateLimitError
    from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

    client = Groq()

    @retry(retry=retry_if_exception_type(RateLimitError), wait=wait_exponential(min=5, max=90),
           stop=stop_after_attempt(8), reraise=True)
    def grade(prompt: str) -> dict:
        resp = client.chat.completions.create(
            model=JUDGE_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0,
            reasoning_effort="low", response_format={"type": "json_object"}, max_completion_tokens=1024)
        return json.loads(resp.choices[0].message.content)

    items = {it["id"]: it for it in json.loads(EVAL_SET.read_text(encoding="utf-8"))}
    runs = _load(RUNS, lambda r: (r["arm"], r["id"]))
    judged = _load(JUDGED, lambda r: (r["arm"], r["id"]))
    for (arm, qid), r in sorted(runs.items(), key=lambda kv: (kv[0][1], kv[0][0])):  # interleave arms per question
        if (arm, qid) in judged:
            continue
        it = items[qid]
        prompt = JUDGE_PROMPT.format(question=it["question"], reference=it["reference"], answer=r["answer"],
                                     rubric=RUBRIC_ANSWERABLE if it["answerable"] else RUBRIC_OOS)
        try:
            verdict = grade(prompt)
        except RateLimitError as exc:
            if "per day" in str(exc).lower():
                raise QuotaExhausted(str(exc)[:300]) from exc
            raise
        score = verdict.get("score")
        score = float(score) if score in (0, 0.5, 1, "0", "0.5", "1") else None
        _append(JUDGED, {"arm": arm, "id": qid, "score": score, "reason": verdict.get("reason", "")})
        print(f"  judge {arm} q{qid:02d} = {score}", flush=True)


# ── Stage 3: report ──────────────────────────────────────────────────────────

def _paired_ci(a: list, b: list, iters: int = 10_000, seed: int = 0):
    d = np.array([x - y for x, y in zip(a, b) if x is not None and y is not None], dtype=float)
    if len(d) < 2:
        return float("nan"), float("nan"), float("nan"), len(d)
    boots = np.random.default_rng(seed).choice(d, (iters, len(d))).mean(axis=1)
    return d.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5), len(d)


def stage_report() -> None:
    items = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    runs = _load(RUNS, lambda r: (r["arm"], r["id"]))
    judged = _load(JUDGED, lambda r: (r["arm"], r["id"]))
    ans = [it for it in items if it["answerable"]]
    oos = [it for it in items if not it["answerable"]]

    def evidence_hit(arm, it):
        r = runs.get((arm, it["id"]))
        if r is None:
            return None
        gold = {e["chunk_id"] for e in it["evidence"]}
        return float(any(c["chunk_id"] in gold for c in r["citations"]))

    def score(arm, it):
        return (judged.get((arm, it["id"])) or {}).get("score")

    lines = [f"# RAG vs CAG on Atlas /ask ({len(ans)} answerable + {len(oos)} out-of-scope questions, 5 companies)", "",
             f"Generator {next(iter(runs.values()))['model'] if runs else '–'} (both arms, blind) · judge {JUDGE_MODEL}"
             f" · single run{' · input tokens estimated as chars/4' if any(r.get('tokens_estimated') for r in runs.values()) else ''}", "",
             "| Arm | Correctness | Cites gold evidence | Citations verified | Refusals (answerable) | Abstention (out-of-scope) | Input tokens / q | Latency p50 |",
             "|---|---|---|---|---|---|---|---|"]
    for arm in ARMS:
        rs = [runs[(arm, it["id"])] for it in items if (arm, it["id"]) in runs]
        corr = [s for it in ans if (s := score(arm, it)) is not None]
        hits = [h for it in ans if (h := evidence_hit(arm, it)) is not None]
        drafted = sum(r["drafted_citations"] for r in rs)
        verified = sum(r["verified_citations"] for r in rs)
        refused = sum(runs[(arm, it["id"])]["refused"] for it in ans if (arm, it["id"]) in runs)
        abst = [s for it in oos if (s := score(arm, it)) is not None]
        tokens = statistics.mean(r["input_tokens"] for r in rs) if rs else float("nan")
        secs = [r["seconds"] for r in rs if r.get("seconds") is not None]  # None for subagent-generated runs
        p50 = f"{statistics.median(secs):.1f}s" if secs else "n/a"
        lines.append(
            f"| {arm} | {np.mean(corr):.3f} (n={len(corr)}) | {sum(hits):.0f}/{len(hits)} | "
            f"{verified}/{drafted} ({verified / drafted:.0%}) | {refused}/{len(ans)} | {sum(abst):.0f}/{len(abst)} | "
            f"{tokens:,.0f} | {p50} |" if corr and drafted else f"| {arm} | – | – | – | – | – | – | – |")

    lines += ["", "## CAG − RAG, paired over answerable questions (95% bootstrap CI, 10k resamples)", "",
              "| Metric | Δ mean | 95% CI | paired n |", "|---|---|---|---|"]
    for name, fn in [("Correctness", score), ("Cites gold evidence", evidence_hit)]:
        d, lo, hi, n = _paired_ci([fn("cag", it) for it in ans], [fn("rag", it) for it in ans])
        flag = " *" if lo > 0 or hi < 0 else ""
        lines.append(f"| {name} | {d:+.3f}{flag} | [{lo:+.3f}, {hi:+.3f}] | {n} |")

    lines += ["", "## By question type (correctness)", "", "| Type | RAG | CAG | n |", "|---|---|---|---|"]
    for kind in ["fact", "guidance", "hedge", "qa"]:
        sub = [it for it in ans if it["type"] == kind]
        cell = lambda arm: (lambda v: f"{np.mean(v):.2f}" if v else "–")([s for it in sub if (s := score(arm, it)) is not None])
        lines.append(f"| {kind} | {cell('rag')} | {cell('cag')} | {len(sub)} |")
    lines += ["", "\\* CI excludes 0. Correctness and abstention are LLM-judged; evidence hits and citation verification are exact checks."]

    RESULTS.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", nargs="?", default="all", choices=["run", "judge", "report", "all"])
    args = ap.parse_args()
    try:
        if args.stage in ("run", "all"):
            stage_run()
        if args.stage in ("judge", "all"):
            stage_judge()
        if args.stage in ("report", "all"):
            stage_report()
    except QuotaExhausted as exc:
        print(f"\nSTOPPED: daily quota hit, progress saved. Re-run the same command after reset.\n{exc}")
        sys.exit(2)
