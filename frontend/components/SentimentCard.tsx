"use client";

import { useEffect, useState } from "react";

import { getSentiment } from "@/lib/api";
import type { SentimentResult } from "@/lib/types";
import { Skeleton } from "./Skeleton";

// Scores are VADER compound averages (-1 to +1). VADER reads nearly all
// corporate language as positive, so the bar shows the raw score and the
// card says it's a rough gauge - never a buy/sell signal.
function label(score: number): string {
  if (score >= 0.6) return "Very positive";
  if (score >= 0.3) return "Positive";
  if (score > -0.3) return "Neutral";
  return "Negative";
}

function Meter({ name, score }: { name: string; score: number | null }) {
  if (score === null) return null;
  return (
    <div>
      <div className="flex items-baseline justify-between text-sm">
        <span className="font-medium text-slate-900">{name}</span>
        <span className="tabular-nums text-slate-600">
          {label(score)} ({score > 0 ? "+" : ""}
          {score.toFixed(2)})
        </span>
      </div>
      <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-brand-600" style={{ width: `${((score + 1) / 2) * 100}%` }} />
      </div>
    </div>
  );
}

export function SentimentCard({ ticker }: { ticker: string }) {
  const [data, setData] = useState<SentimentResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getSentiment(ticker)
      .then(setData)
      .catch(() => setData(null)) // optional extra - just hide the card if unavailable
      .finally(() => setLoading(false));
  }, [ticker]);

  if (loading) return <Skeleton className="mt-6 h-40 w-full rounded-2xl" />;
  if (!data) return null;

  return (
    <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
      <h2 className="text-lg font-semibold tracking-tight text-slate-900">
        Tone of the earnings call <span className="text-sm font-normal text-slate-400">· {data.quarter}</span>
      </h2>
      <p className="mt-1 text-xs text-slate-500">
        How positive or negative the language was, from -1 to +1. Prepared remarks are scripted; Q&amp;A is
        unscripted, so a gap between them can be telling.
      </p>
      <div className="mt-4 space-y-4">
        <Meter name="Overall" score={data.overall} />
        <Meter name="Prepared remarks" score={data.prepared_remarks} />
        <Meter name="Q&A" score={data.qa} />
      </div>
      <p className="mt-4 text-xs text-slate-400">
        A rough automated gauge based on word choice - it can miss context and isn&apos;t financial advice.
      </p>
    </section>
  );
}
