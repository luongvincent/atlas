"use client";

import { useEffect, useState } from "react";

import { Skeleton } from "@/components/Skeleton";
import { TickerCard } from "@/components/TickerCard";
import { ApiError, getTickers } from "@/lib/api";
import type { TickerInfo } from "@/lib/types";

export default function TickersPage() {
  const [tickers, setTickers] = useState<TickerInfo[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTickers()
      .then((res) => setTickers(res.tickers))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load tickers"));
  }, []);

  return (
    <div>
      <h1 className="font-serif text-4xl font-semibold tracking-tight text-slate-900">Top 15 US stocks</h1>
      <p className="mt-3 max-w-[65ch] font-serif text-lg leading-8 text-slate-700">
        The companies people trade most, each with a plain-language explanation of its latest earnings
        call: what happened, what management said, and why it matters.
      </p>

      {error && (
        <p className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
      )}

      {!tickers && !error && (
        <div className="mt-8 divide-y divide-slate-200 border-y border-slate-200">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 px-2 py-5">
              <Skeleton className="h-10 w-10 rounded-lg" />
              <div>
                <Skeleton className="h-5 w-48" />
                <Skeleton className="mt-2 h-4 w-64" />
              </div>
            </div>
          ))}
        </div>
      )}

      {tickers && (
        <ul className="mt-8 divide-y divide-slate-200 border-y border-slate-200">
          {tickers.map((t) => (
            <TickerCard key={t.ticker} ticker={t} />
          ))}
        </ul>
      )}
    </div>
  );
}
