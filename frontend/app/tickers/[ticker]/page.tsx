"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { ApiError, getExplanation } from "@/lib/api";
import type { ExplainResponse } from "@/lib/types";

const SECTION_LABELS: Record<keyof ExplainResponse["sections"], string> = {
  what_happened: "What happened",
  what_management_said: "What management actually said",
  what_analysts_pushed_back_on: "What analysts pushed back on",
  why_it_matters: "Why it matters",
};

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
      <h1 className="text-2xl font-bold text-slate-900">{ticker}</h1>

      {loading && <p className="mt-6 text-sm text-slate-500">Loading explanation...</p>}

      {error && error.status === 401 && (
        <div className="mt-6 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <p className="text-sm text-amber-800">{error.message}</p>
          {!user && <p className="mt-2 text-sm text-amber-800">Sign in above, then come back to this page.</p>}
          {user && (
            <button
              onClick={load}
              className="mt-3 rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700"
            >
              Retry now that you're signed in
            </button>
          )}
        </div>
      )}

      {error && error.status === 404 && (
        <p className="mt-6 text-sm text-slate-600">{error.message}</p>
      )}

      {error && error.status !== 401 && error.status !== 404 && (
        <p className="mt-6 text-sm text-red-600">{error.message}</p>
      )}

      {data && (
        <div className="mt-6 space-y-6">
          <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
            <span className="font-medium text-slate-900">{data.company_name}</span>
            <span>&middot;</span>
            <span>{data.quarter}</span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs ${
                data.cached ? "bg-slate-100 text-slate-600" : "bg-green-100 text-green-700"
              }`}
            >
              {data.cached ? "cached" : "freshly generated"}
            </span>
          </div>

          {(Object.keys(SECTION_LABELS) as (keyof ExplainResponse["sections"])[]).map((key) => (
            <section key={key} className="rounded-lg border border-slate-200 bg-white p-5">
              <h2 className="text-lg font-semibold text-slate-900">{SECTION_LABELS[key]}</h2>
              <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-slate-700">
                {data.sections[key]}
              </p>
            </section>
          ))}

          {data.glossary.length > 0 && (
            <section className="rounded-lg border border-brand-100 bg-brand-50 p-5">
              <h2 className="text-lg font-semibold text-slate-900">Terms used in this explanation</h2>
              <dl className="mt-2 space-y-2">
                {data.glossary.map((g) => (
                  <div key={g.term} className="text-sm">
                    <dt className="inline font-medium capitalize text-slate-900">{g.term}: </dt>
                    <dd className="inline text-slate-700">{g.definition}</dd>
                  </div>
                ))}
              </dl>
            </section>
          )}

          {data.citations.length > 0 && (
            <section className="rounded-lg border border-slate-200 bg-white p-5">
              <h2 className="text-lg font-semibold text-slate-900">Citations</h2>
              <ul className="mt-2 space-y-2">
                {data.citations.map((c, i) => (
                  <li key={i} className="text-sm text-slate-700">
                    <span className="font-medium">{c.speaker}</span>{" "}
                    <span className="text-xs text-slate-500">
                      ({c.section === "qa" ? "Q&A" : "prepared remarks"})
                    </span>
                    : {c.claim}
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
