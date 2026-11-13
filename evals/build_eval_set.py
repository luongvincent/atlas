"""Writes evals/atlas_eval_set.json and checks every evidence quote is verbatim in its cited chunk.

References are written from the transcript text only (never from model output). Transcripts are read
from Pinecone, so this needs PINECONE_API_KEY; it makes no LLM calls.
Usage: ./venv/Scripts/python.exe evals/build_eval_set.py
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv

load_dotenv()
from pinecone import Pinecone

OUT = Path(__file__).resolve().parent / "atlas_eval_set.json"
INDEX = "earnings-call-transcripts"
QUARTERS = {"AAPL": "Q3 2026", "NVDA": "Q2 2027", "INTC": "Q1 2026", "F": "Q1 2026", "PLTR": "Q2 2026"}

# (ticker, type, question, reference, [(chunk "turn.chunk", verbatim evidence)])
ITEMS = [
    ("AAPL", "fact", "How much revenue did Apple report this quarter?",
     "Apple reported $109.4 billion in revenue, up 16% year over year and a June quarter record.",
     [("2.0", "Our revenue of $109.4 billion was up 16% year-over-year, a June quarter revenue record")]),
    ("AAPL", "fact", "What was Apple's gross margin, and was anything unusual in it?",
     "Gross margin was 50.1%. It included about two percentage points of benefit from tariff refunds; without that, it would have been at the midpoint of the prior guidance range.",
     [("2.1", "Company gross margin was 50.1%"), ("2.1", "a favorable impact of approximately two percentage points")]),
    ("AAPL", "guidance", "What revenue growth does Apple expect next quarter, and why is it lower?",
     "Apple expects September quarter revenue to grow 9% to 11% year over year, held back by a foreign exchange headwind of about two and a half percentage points and supply constraints that are expected to increase significantly.",
     [("2.11", "we expect our September quarter total company revenue to grow between 9%-11% year-over-year"),
      ("2.10", "we expect the impact from supply constraints to increase significantly sequentially")]),
    ("AAPL", "qa", "What did analysts push back on about Apple's supply constraints?",
     "Ben Reitzes of Melius Research asked about the supply constraints, noting the Street had expected 12% growth for the September quarter versus roughly 10% guided, and a deceleration to 8%-9% in the December quarter.",
     [("22.0", "I wanted to ask about the supply constraints again"), ("22.0", "the Street had you at 12% growth for the quarter")]),
    ("AAPL", "hedge", "What did Tim Cook say caused the supply constraints?",
     "Tim Cook said the main constraint is the advanced chip-making nodes Apple's SoCs run on, and that the root cause was a demand forecasting issue: iPhone and Mac sold much better than expected (iPhone up 22%, Mac up 29%).",
     [("23.0", "the primary issue is advanced nodes that we run our SoCs on"), ("23.0", "It's a demand forecast issue, to be candid")]),
    ("NVDA", "fact", "How much revenue did NVIDIA report this quarter?",
     "NVIDIA reported total revenue of $96 billion, more than double the prior year, with data center revenue of $89 billion, up 18% from the previous quarter.",
     [("2.0", "Total revenue of $96 billion more than doubled year-over-year"),
      ("2.0", "Q2 data center revenue increased 18% quarter-over-quarter to $89 billion")]),
    ("NVDA", "guidance", "What revenue growth does NVIDIA expect for fiscal 2028?",
     "NVIDIA expects fiscal 2028 revenue to grow about 70%. It called this a supply-constrained outlook and expects supply to remain a bottleneck at least through the end of fiscal 2028.",
     [("2.0", "We expect to grow revenue by approximately 70% in fiscal 2028. This is a supply-constrained outlook"),
      ("2.21", "we expect supply to remain a bottleneck, at least through the end of fiscal year '28")]),
    ("NVDA", "hedge", "What did NVIDIA say about gross margins going forward?",
     "Because memory prices have risen more than expected, NVIDIA reset expectations: Q3 gross margin of 74% plus or minus 50 basis points, bottoming at 71% to 72% in Q4, then settling at 72% to 73% in fiscal 2028.",
     [("2.21", "we are experiencing extreme pricing conditions in memory"),
      ("2.21", "we expect GAAP and non-GAAP gross margins to be 74% plus or minus 50 basis points"),
      ("2.22", "We expect margins to bottom in Q4 in the 71% to 72% range before settling at 72% to 73% in fiscal year '28")]),
    ("NVDA", "qa", "What did Joseph Moore from Morgan Stanley ask about?",
     "Joseph Moore asked what gives NVIDIA confidence to guide 70% growth a full year out, what constraint separates that from 100% demand growth, and whether that gap can close over time.",
     [("4.0", "what gives you the confidence to guide a full year out"),
      ("4.0", "What is the kind of key constraint that separates those numbers?")]),
    ("NVDA", "fact", "Why did NVIDIA's inventory go up?",
     "Inventory increased to $32 billion as NVIDIA prepared for the Vera Rubin launch.",
     [("2.20", "inventory increased to $32 billion as we prepared for the Vera Rubin launch")]),
    ("INTC", "fact", "What was Intel's revenue this quarter?",
     "Intel's first-quarter revenue was $13.6 billion, $1.4 billion above the midpoint of its guidance, and would have been higher if supply had kept up with demand.",
     [("1.0", "First-quarter revenue was $13.6 billion, $1.4 billion above the midpoint of our guide")]),
    ("INTC", "fact", "How did Intel's gross margin compare with its guidance?",
     "Non-GAAP gross margin was 41%, about 650 basis points ahead of guidance, helped by higher volume (including previously reserved inventory), mix and pricing.",
     [("1.1", "Non-GAAP gross margin came in at 41%, approximately 650 basis points ahead of guidance")]),
    ("INTC", "guidance", "What is Intel's outlook for next quarter?",
     "At the midpoint of $14.3 billion in revenue, Intel forecasts a non-GAAP gross margin of 39%, an 11% tax rate and EPS of $0.20. The margin dips because of a larger contribution from the early Intel 18A ramp and Q1 inventory benefits that won't repeat.",
     [("1.9", "At the midpoint of $14.3 billion, we forecast a gross margin of 39%, a tax rate of 11%, and EPS of $0.20")]),
    ("INTC", "hedge", "What risks did Intel flag for the second half of the year?",
     "Intel said rising prices for components like memory, wafers and substrates could hurt demand at some point in the year. It is planning for PC demand to weaken in the second half and expects the full-year PC unit market to be down a low double-digit percent.",
     [("1.8", "could impact demand for our product at some point in the year"),
      ("1.8", "We are prudently planning for PC demand to weaken in the second half of the year")]),
    ("INTC", "qa", "What did analysts ask about Intel's Google deal?",
     "Benjamin Reitzes asked Intel to talk about the Google deal and the other long-term agreements (LTAs) mentioned in the release.",
     [("4.0", "Could you just talk about the Google deal")]),
    ("F", "fact", "What were Ford's revenue and adjusted EBIT this quarter?",
     "Ford reported $43.3 billion in revenue and $3.5 billion in adjusted EBIT.",
     [("2.0", "$43.3 billion in revenue and $3.5 billion in adjusted EBIT")]),
    ("F", "guidance", "Did Ford change its full-year guidance?",
     "Yes. Ford raised full-year adjusted EBIT guidance to $8.5 billion to $10.5 billion, and expects adjusted free cash flow of $5 billion to $6 billion and capital expenditures of $9.5 billion to $10.5 billion.",
     [("2.0", "we are raising our full-year adjusted EBIT guidance to between $8.5 billion and $10.5 billion"),
      ("3.8", "adjusted free cash flow of $5 billion to $6 billion")]),
    ("F", "fact", "How much of Ford's adjusted EBIT came from the IEPA benefit?",
     "Adjusted EBIT was $3.5 billion, or $2.2 billion excluding the IEPA benefit, so the benefit was about $1.3 billion.",
     [("3.2", "We delivered adjusted EBIT of $3.5 billion, or $2.2 billion excluding the impact of the IEPA benefit")]),
    ("F", "hedge", "What does Ford's guidance leave out?",
     "Ford's guidance does not include the potential impact of a sustained conflict in the Middle East or a significant downturn in the U.S. economy, either of which could materially affect demand.",
     [("3.8", "Our guidance does not include the potential impacts of a sustained conflict in the Middle East or a significant downturn in the U.S. economy")]),
    ("F", "qa", "What did Joseph Spak ask Ford about?",
     "Joseph Spak asked about the roughly $1 billion commodity cost increase and what Ford was assuming, referencing its past description of an $8 billion steel and aluminum buy.",
     [("5.0", "to pick up on the commodity increase")]),
    ("PLTR", "fact", "How fast did Palantir's revenue grow?",
     "Palantir's revenue grew 93% year over year, its highest ever. U.S. revenue grew 115% and U.S. commercial revenue grew 149%.",
     [("1.0", "We delivered 93% year-over-year revenue growth, our highest ever"),
      ("1.0", "Our U.S. commercial revenue growth accelerated to 149% year-over-year")]),
    ("PLTR", "guidance", "What did Palantir raise its guidance to?",
     "Palantir raised its full-year 2026 revenue guidance midpoint to $8.154 billion (82% growth) and its U.S. commercial revenue guidance to more than $3.424 billion (at least 134% growth).",
     [("3.1", "raising our full year 2026 revenue guidance midpoint to $8.154 billion, representing 82% growth"),
      ("3.1", "in excess of $3.424 billion, representing a growth rate of at least 134%")]),
    ("PLTR", "fact", "What was Palantir's adjusted free cash flow?",
     "Adjusted free cash flow was $1.22 billion, its highest ever, a 63% margin and up 115% year over year.",
     [("3.0", "our highest ever adjusted free cash flow of $1.22 billion, representing a 63% margin and 115% growth year-over-year")]),
    ("PLTR", "qa", "What did Mariana Perez Mora from Bank of America ask?",
     "She asked why enterprises took about three years to realise that owning and learning from their own data matters, and why Palantir's earlier approach to AI wasn't recognised sooner.",
     [("11.0", "now everyone started to realize, owning my data")]),
    # Out of scope: each topic is checked absent from the transcript below.
    ("AAPL", "oos", "What did Apple say about layoffs?", "The call did not discuss layoffs.", []),
    ("NVDA", "oos", "What did NVIDIA say about Bitcoin or crypto mining demand?", "The call did not discuss Bitcoin or crypto mining.", []),
    ("NVDA", "oos", "Is NVIDIA planning a stock split?", "The call did not discuss a stock split.", []),
    ("INTC", "oos", "How much is Intel paying in dividends?", "The call did not discuss dividends.", []),
    ("F", "oos", "What did Ford say about its Formula 1 program?", "The call did not discuss Formula 1 or racing.", []),
    ("PLTR", "oos", "How much stock did Palantir buy back this quarter?", "The call did not discuss share buybacks.", []),
]
OOS_ABSENT = {
    "What did Apple say about layoffs?": r"layoff|headcount",
    "What did NVIDIA say about Bitcoin or crypto mining demand?": r"bitcoin|crypto",
    "Is NVIDIA planning a stock split?": r"split",
    "How much is Intel paying in dividends?": r"dividend",
    "What did Ford say about its Formula 1 program?": r"formula|racing|nascar",
    "How much stock did Palantir buy back this quarter?": r"buyback|buy back|repurchase",
}


def load_chunks(index, ticker, quarter):
    ids = [i for page in index.list(prefix=f"{ticker}:{quarter}:") for i in page]
    chunks = {}
    for i in range(0, len(ids), 100):
        for vid, v in index.fetch(ids=ids[i:i + 100]).vectors.items():
            _, _, turn, chunk = vid.rsplit(":", 3)
            chunks[f"{turn}.{chunk}"] = v.metadata["text"]
    return chunks


def main():
    index = Pinecone(api_key=os.environ["PINECONE_API_KEY"]).Index(INDEX)
    texts = {t: load_chunks(index, t, q) for t, q in QUARTERS.items()}
    rows, problems = [], []
    for n, (ticker, kind, question, reference, evidence) in enumerate(ITEMS):
        chunks = texts[ticker]
        for chunk, quote in evidence:
            if quote not in chunks.get(chunk, ""):
                problems.append(f"q{n} {ticker} {chunk}: evidence not verbatim: {quote[:60]!r}")
        if kind == "oos":
            hits = sum(bool(re.search(OOS_ABSENT[question], t, re.I)) for t in chunks.values())
            if hits:
                problems.append(f"q{n} {ticker}: out-of-scope topic appears in {hits} chunks")
        rows.append({
            "id": n, "ticker": ticker, "quarter": QUARTERS[ticker], "type": kind, "answerable": kind != "oos",
            "question": question, "reference": reference,
            "evidence": [{"chunk_id": f"{ticker}:{QUARTERS[ticker]}:{c.replace('.', ':')}", "quote": q} for c, q in evidence],
        })
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} items ({sum(r['answerable'] for r in rows)} answerable) to {OUT.name}; all evidence verified")


if __name__ == "__main__":
    main()
