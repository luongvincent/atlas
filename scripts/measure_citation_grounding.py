"""Measure how often the LLM's raw citations fail verification.

For each ingested ticker, builds the same prompt as /explain, samples the
model, and checks every citation it emits with the production verifier
(core.explainer_chain._resolve_citations). Reports how many citations would
have been shown unverified without that check - the "before" number. The
"after" number is 0 by construction: unverified citations are dropped.

Costs one Groq call per ticker per sample (~7-8k tokens each), so a full run
of 11 tickers uses a large share of the free-tier daily token budget.

Usage:
    python scripts/measure_citation_grounding.py [--samples N] [TICKER ...]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.tickers import SUPPORTED_TICKERS, TICKERS_BY_SYMBOL
from core import explainer_chain as chain
from core.supabase_client import get_request_client


def build_prompt(ticker: str, quarter: str) -> tuple[str, dict]:
    # Mirrors generate_explanation's prompt assembly so we measure what /explain sends.
    prepared_docs, qa_docs = chain.retrieve_context(ticker, quarter)
    prepared = chain._label_docs(prepared_docs, "P")
    qa = chain._label_docs(qa_docs, "Q")
    prompt = chain.SYSTEM_PROMPT.format(
        company_name=TICKERS_BY_SYMBOL[ticker].company_name,
        ticker=ticker,
        quarter=quarter,
        prepared_remarks_context=chain._format_docs(prepared),
        qa_context=chain._format_docs(qa),
    )
    return prompt, {**prepared, **qa}


def classify(draft, labelled: dict) -> str:
    """'verified', 'bad_label' (cites an excerpt that wasn't provided) or 'quote_mismatch'."""
    if chain._resolve_citations([draft], labelled):
        return "verified"
    if draft.excerpt_label.strip().strip("[]").upper() not in labelled:
        return "bad_label"
    return "quote_mismatch"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tickers", nargs="*")
    parser.add_argument("--samples", type=int, default=1, help="model calls per ticker")
    args = parser.parse_args()

    rows = get_request_client().table("tickers").select("ticker, latest_quarter").execute().data
    quarters = {r["ticker"]: r["latest_quarter"] for r in rows if r["latest_quarter"]}
    tickers = [t.upper() for t in args.tickers] or [t.ticker for t in SUPPORTED_TICKERS if t.ticker in quarters]

    totals = {"verified": 0, "bad_label": 0, "quote_mismatch": 0}
    calls = calls_with_none_verified = 0
    print(f"{'ticker':<6} {'quarter':<10} {'cited':>5} {'ok':>4} {'label':>6} {'quote':>6}")
    for ticker in tickers:
        if ticker not in quarters:
            print(f"{ticker:<6} not ingested, skipped")
            continue
        prompt, labelled = build_prompt(ticker, quarters[ticker])
        if not labelled:
            print(f"{ticker:<6} no chunks retrieved, skipped")
            continue
        for _ in range(args.samples):
            try:
                draft = chain._invoke_structured(prompt)
            except Exception as exc:  # one failed call shouldn't lose the rest of the run
                print(f"{ticker:<6} LLM call failed: {exc}")
                continue
            counts = {"verified": 0, "bad_label": 0, "quote_mismatch": 0}
            for d in draft.citations:
                counts[classify(d, labelled)] += 1
            for k in totals:
                totals[k] += counts[k]
            calls += 1
            calls_with_none_verified += counts["verified"] == 0
            print(
                f"{ticker:<6} {quarters[ticker]:<10} {len(draft.citations):>5} {counts['verified']:>4} "
                f"{counts['bad_label']:>6} {counts['quote_mismatch']:>6}"
            )

    cited = sum(totals.values())
    if not cited:
        print("\nNo citations collected.")
        return
    failed = cited - totals["verified"]
    print(
        f"\n{calls} model calls, {cited} citations emitted."
        f"\nFailed verification: {failed}/{cited} = {failed / cited:.1%}"
        f"  (bad excerpt label: {totals['bad_label']}, quote not in excerpt: {totals['quote_mismatch']})"
        f"\nCalls where no citation verified (would trigger the retry): {calls_with_none_verified}/{calls}"
        f"\nShown to users with verification on: 0 unverified citations."
    )


if __name__ == "__main__":
    main()
