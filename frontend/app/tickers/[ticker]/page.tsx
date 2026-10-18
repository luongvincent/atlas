"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { Badge } from "@/components/Badge";
import { Button } from "@/components/Button";
import { PriceChart } from "@/components/PriceChart";
import { Skeleton } from "@/components/Skeleton";
import { StatsGrid } from "@/components/StatsGrid";
import { ApiError, getExplanation } from "@/lib/api";
import type { ExplainResponse } from "@/lib/types";

const SECTIONS: { key: keyof ExplainResponse["sections"]; label: string }[] = [
  { key: "what_happened", label: "What happened" },
  { key: "what_management_said", label: "What management actually said" },
  { key: "what_analysts_pushed_back_on", label: "What analysts pushed back on" },
  { key: "why_it_matters", label: "Why it matters" },
];

// Words that signal a prediction rather than a promise. Underline as well as
// tint so the meaning doesn't rely on color alone.
const HEDGE_WORDS = /\b(expect(?:s|ed|ing)?|anticipate[sd]?|believe[sd]?|hope[sd]?|may|might|could|approximately|roughly)\b/i;

function highlightHedges(text: string) {
  // split() with a capture group puts the matched words at odd indexes.
  return text.split(new RegExp(HEDGE_WORDS.source, "gi")).map((part, i) =>
    i % 2 === 1 ? (
      <mark key={i} className="rounded-sm bg-moderate-100 px-0.5 text-slate-900 underline decoration-moderate-600 decoration-dotted underline-offset-4">
        {part}
      </mark>
    ) : (
      part
    ),
  );
}

function SectionBody({ sectionKey, text }: { sectionKey: string; text: string }) {
  if (sectionKey === "what_happened") {
    // Lead with the headline sentence, set large.
    const [lede, ...rest] = text.split(/(?<=[.!?])\s+/);
    return (
      <>
        <p className="mt-3 font-serif text-2xl font-semibold leading-snug text-slate-900">{lede}</p>
        {rest.length > 0 && (
          <p className="mt-4 whitespace-pre-line font-serif text-[1.0625rem] leading-8 text-slate-700">{rest.join(" ")}</p>
        )}
      </>
    );
  }
  const hedged = sectionKey === "what_management_said";
  return (
    <>
      <p className="mt-3 whitespace-pre-line font-serif text-[1.0625rem] leading-8 text-slate-700">
        {hedged ? highlightHedges(text) : text}
      </p>
      {hedged && (
        <p className="mt-3 font-sans text-sm text-slate-500">
          Highlighted words mean the company is predicting, not promising.
        </p>
      )}
    </>
  );
}

export default function TickerExplainPage({ params }: { params: { ticker: string } }) {
  const ticker = params.ticker.toUpperCase();
  const { session, user, loading: authLoading } = useAuth();

  const [data, setData] = useState<ExplainResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    getExplanation(ticker, session?.access_token)
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err : new ApiError(500, "Unknown error")))
      .finally(() => setLoading(false));
  }, [ticker, session?.access_token]);

  useEffect(() => {
    if (authLoading) return;
    load();
  }, [authLoading, load]);

  return (
    <div>
      <Link href="/tickers" className="text-sm font-medium text-brand-700 hover:underline">
        ← Back to tickers
      </Link>

      <h1 className="text-3xl font-bold tracking-tight text-slate-900">{ticker}</h1>

      {data && (
        <>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600">
            <span className="font-semibold text-slate-900">{data.company_name}</span>
            <span className="text-slate-300">&middot;</span>
            <span>{data.quarter}</span>
          </div>

          {data.generated_at && (
            <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
              <span>Generated {new Date(data.generated_at).toLocaleDateString()}</span>
              <Badge tone={data.cached ? "neutral" : "positive"}>{data.cached ? "Cached" : "Fresh"}</Badge>
            </div>
          )}

          <div className="mt-3 rounded-xl border border-brand-100 bg-brand-50 px-4 py-3">
            <p className="text-xs leading-relaxed text-brand-900">
              <span className="font-semibold">This is an AI-generated explanation, not financial advice.</span>{" "}
              Use it to understand what happened - not as a recommendation to buy, sell, or hold.
            </p>
          </div>
        </>
      )}

      <div className="mt-4">
        <PriceChart ticker={ticker} />
      </div>

      <StatsGrid ticker={ticker} />

      {loading && (
        <div className="mt-6 space-y-4">
          <Skeleton className="h-4 w-64" />
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="max-w-[65ch] border-t border-slate-200 pt-6">
              <Skeleton className="h-5 w-48" />
              <Skeleton className="mt-3 h-3 w-full" />
              <Skeleton className="mt-2 h-3 w-5/6" />
              <Skeleton className="mt-2 h-3 w-2/3" />
            </div>
          ))}
        </div>
      )}

      {error && error.status === 401 && (
        <div className="mt-6 rounded-2xl border border-moderate-100 bg-moderate-50 p-4">
          <p className="text-sm text-moderate-700">{error.message}</p>
          {!user && (
            <p className="mt-2 text-sm text-moderate-700">
              <Link href="/login" className="font-medium underline">
                Sign in
              </Link>{" "}
              then come back to this page.
            </p>
          )}
          {user && (
            <Button onClick={load} className="mt-3">
              Retry now that you're signed in
            </Button>
          )}
        </div>
      )}

      {error && error.status === 404 && (
        <p className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
          {error.message}
        </p>
      )}

      {error && error.status !== 401 && error.status !== 404 && (
        <div role="alert" className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-700">{error.message}</p>
          <Button onClick={load} className="mt-3">
            Try again
          </Button>
        </div>
      )}

      {data && (
        <div className="mt-10 max-w-[65ch] space-y-10">
          {SECTIONS.map(({ key, label }) => (
            <section key={key} className="border-t border-slate-200 pt-6">
              <h2 className="text-sm font-semibold text-brand-700">{label}</h2>
              <SectionBody sectionKey={key} text={data.sections[key]} />
            </section>
          ))}

          {data.glossary.length > 0 && (
            <section className="rounded-2xl border border-brand-100 bg-brand-50 p-5">
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-600 text-xs font-bold text-white">
                  Aa
                </span>
                <h2 className="text-base font-semibold text-slate-900">Terms used in this explanation</h2>
              </div>
              <dl className="mt-3 space-y-2.5">
                {data.glossary.map((g) => (
                  <div key={g.term} className="text-sm">
                    <dt className="inline font-semibold capitalize text-slate-900">{g.term}: </dt>
                    <dd className="inline text-slate-700">{g.definition}</dd>
                  </div>
                ))}
              </dl>
            </section>
          )}

          {data.citations.length > 0 && (
            <section className="border-t border-slate-200 pt-6">
              <h2 className="text-sm font-semibold text-brand-700">Citations</h2>
              <ul className="mt-3 space-y-3">
                {data.citations.map((c, i) => (
                  <li key={i} className="flex gap-3 text-sm">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600">
                      {c.speaker[0]?.toUpperCase() ?? "?"}
                    </span>
                    <p className="text-slate-700">
                      <span className="font-medium text-slate-900">{c.speaker}</span>{" "}
                      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
                        {c.section === "qa" ? "Q&A" : "Prepared remarks"}
                      </span>
                      <br />
                      {c.claim}
                    </p>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
