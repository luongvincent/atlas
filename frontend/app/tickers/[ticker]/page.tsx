"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { Badge } from "@/components/Badge";
import { PriceChart } from "@/components/PriceChart";
import { Skeleton } from "@/components/Skeleton";
import { StatsGrid } from "@/components/StatsGrid";
import { ApiError, getExplanation } from "@/lib/api";
import type { ExplainResponse } from "@/lib/types";

const SECTIONS: { key: keyof ExplainResponse["sections"]; label: string; step: string }[] = [
  { key: "what_happened", label: "What happened", step: "01" },
  { key: "what_management_said", label: "What management actually said", step: "02" },
  { key: "what_analysts_pushed_back_on", label: "What analysts pushed back on", step: "03" },
  { key: "why_it_matters", label: "Why it matters", step: "04" },
];

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
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">{ticker}</h1>

      <div className="mt-4">
        <PriceChart ticker={ticker} />
      </div>

      <StatsGrid ticker={ticker} />

      {loading && (
        <div className="mt-6 space-y-4">
          <Skeleton className="h-4 w-64" />
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
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
            <button
              onClick={load}
              className="mt-3 rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-brand-700"
            >
              Retry now that you're signed in
            </button>
          )}
        </div>
      )}

      {error && error.status === 404 && (
        <p className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
          {error.message}
        </p>
      )}

      {error && error.status !== 401 && error.status !== 404 && (
        <p className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error.message}
        </p>
      )}

      {data && (
        <div className="mt-6 space-y-6">
          <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
            <span className="font-semibold text-slate-900">{data.company_name}</span>
            <span className="text-slate-300">&middot;</span>
            <span>{data.quarter}</span>
            <Badge tone={data.cached ? "neutral" : "positive"}>
              {data.cached ? "cached" : "freshly generated"}
            </Badge>
          </div>

          {SECTIONS.map(({ key, label, step }) => (
            <section
              key={key}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card transition-shadow hover:shadow-card-hover"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-sm font-bold tabular-nums text-brand-700">
                  {step}
                </span>
                <h2 className="text-lg font-semibold tracking-tight text-slate-900">{label}</h2>
              </div>
              <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-slate-700">
                {data.sections[key]}
              </p>
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
            <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
              <h2 className="text-base font-semibold text-slate-900">Citations</h2>
              <ul className="mt-3 space-y-3">
                {data.citations.map((c, i) => (
                  <li key={i} className="flex gap-3 text-sm">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600">
                      {c.speaker[0]?.toUpperCase() ?? "?"}
                    </span>
                    <p className="text-slate-700">
                      <span className="font-medium text-slate-900">{c.speaker}</span>{" "}
                      <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
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
