"use client";

import { useEffect, useState } from "react";

import { SearchSection } from "@/components/SearchSection";
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
      <h1 className="font-serif text-4xl font-semibold tracking-tight text-slate-900">Stocks</h1>
      <p className="mt-3 max-w-[65ch] font-serif text-lg leading-8 text-slate-700">
        Look up any US stock for its price and key numbers. The 15 most traded companies also come with a
        plain-language explanation of their latest earnings call.
      </p>

      <SearchSection kind="stock">
        <h2 className="mt-10 font-serif text-2xl font-semibold tracking-tight text-slate-900">
          The 15 most traded
        </h2>

        {error && (
          <p className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
        )}

        {!tickers && !error && (
          <div className="mt-4 divide-y divide-slate-200 border-y border-slate-200">
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
          <ul className="mt-4 divide-y divide-slate-200 border-y border-slate-200">
            {tickers.map((t) => (
              <TickerCard key={t.ticker} ticker={t} />
            ))}
          </ul>
        )}
      </SearchSection>
    </div>
  );
}
