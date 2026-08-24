"use client";

import { useEffect, useState } from "react";

import { ApiError, getStrategyOverview } from "@/lib/api";
import type { StrategyOverviewResponse } from "@/lib/types";
import { Badge } from "./Badge";
import { Skeleton } from "./Skeleton";

const SECTIONS: { key: keyof StrategyOverviewResponse["sections"]; label: string; step: string }[] = [
  { key: "what_this_profile_means", label: "What this profile commonly means", step: "01" },
  { key: "common_approaches", label: "Common approaches, in general terms", step: "02" },
  { key: "tradeoffs_to_watch", label: "Tradeoffs to watch", step: "03" },
  { key: "closing_note", label: "One more thing", step: "04" },
];

export function StrategyOverview({ accessToken }: { accessToken: string }) {
  const [data, setData] = useState<StrategyOverviewResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    setData(null);
    setError(null);
    getStrategyOverview(accessToken)
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err : new ApiError(500, "Unknown error")))
      .finally(() => {});
  }, [accessToken]);

  if (error && error.status === 404) {
    // Shouldn't normally happen from this screen (only shown once a
    // profile is saved), but the backend requires a saved risk_profiles
    // row - surface it plainly rather than a generic error if it does.
    return (
      <p className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
        {error.message}
      </p>
    );
  }

  if (error) {
    return (
      <p className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        {error.message}
      </p>
    );
  }

  return (
    <div className="mt-6 space-y-4 text-left">
      {/* Static, always-rendered disclaimer - not dependent on the model
          remembering its own closing_note. See core/strategy_overview.py
          for the product-direction reasoning behind this whole feature
          staying general/educational rather than personalized advice. */}
      <div className="rounded-xl border border-brand-100 bg-brand-50 px-4 py-3">
        <p className="text-xs leading-relaxed text-brand-900">
          <span className="font-semibold">General education, not personalized financial advice.</span>{" "}
          {data?.disclaimer ??
            "This never names specific stocks or funds to buy - talk to a licensed financial advisor before making real decisions with your money."}
        </p>
      </div>

      {data && (
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Badge tone={data.risk_profile}>{data.risk_profile}</Badge>
          <Badge tone={data.cached ? "neutral" : "positive"}>
            {data.cached ? "cached" : "freshly generated"}
          </Badge>
        </div>
      )}

      {SECTIONS.map(({ key, label, step }) => (
        <section key={key} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-sm font-bold tabular-nums text-brand-700">
              {step}
            </span>
            <h3 className="text-base font-semibold tracking-tight text-slate-900">{label}</h3>
          </div>
          {data ? (
            <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-slate-700">
              {data.sections[key]}
            </p>
          ) : (
            <div className="mt-3 space-y-2">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-5/6" />
              <Skeleton className="h-3 w-2/3" />
            </div>
          )}
        </section>
      ))}
    </div>
  );
}
