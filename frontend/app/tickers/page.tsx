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
      <h1 className="text-2xl font-bold tracking-tight text-slate-900">Supported tickers</h1>
      <p className="mt-1 text-sm text-slate-600">
        Plain-language explanations of the latest earnings call for each ticker. Pick one to read it.
      </p>

      {error && (
        <p className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
      )}

      {!tickers && !error && (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
              <Skeleton className="h-5 w-16" />
              <Skeleton className="mt-2 h-4 w-32" />
              <Skeleton className="mt-4 h-3 w-40" />
              <Skeleton className="mt-3 h-5 w-24 rounded-full" />
            </div>
          ))}
        </div>
      )}

      {tickers && (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
          {tickers.map((t) => (
            <TickerCard key={t.ticker} ticker={t} />
          ))}
        </div>
      )}
    </div>
  );
}
