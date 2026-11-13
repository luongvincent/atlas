# RAG vs CAG on Atlas /ask (24 answerable + 6 out-of-scope questions, 5 companies)

Generator claude-subagent (Claude Code, Opus 5.5) (both arms, blind) · judge openai/gpt-oss-120b · single run · input tokens estimated as chars/4

| Arm | Correctness | Cites gold evidence | Citations verified | Refusals (answerable) | Abstention (out-of-scope) | Input tokens / q | Latency p50 |
|---|---|---|---|---|---|---|---|
| rag | 0.625 (n=24) | 14/24 | 67/67 (100%) | 0/24 | 6/6 | 1,947 | n/a |
| cag | 0.938 (n=24) | 23/24 | 86/86 (100%) | 0/24 | 6/6 | 11,777 | n/a |

## CAG − RAG, paired over answerable questions (95% bootstrap CI, 10k resamples)

| Metric | Δ mean | 95% CI | paired n |
|---|---|---|---|
| Correctness | +0.312 * | [+0.125, +0.521] | 24 |
| Cites gold evidence | +0.375 * | [+0.208, +0.583] | 24 |

## By question type (correctness)

| Type | RAG | CAG | n |
|---|---|---|---|
| fact | 0.50 | 1.00 | 10 |
| guidance | 0.80 | 1.00 | 5 |
| hedge | 0.62 | 0.75 | 4 |
| qa | 0.70 | 0.90 | 5 |

\* CI excludes 0. Correctness and abstention are LLM-judged; evidence hits and citation verification are exact checks.
