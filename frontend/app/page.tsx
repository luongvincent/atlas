"use client";

import { useEffect, useState } from "react";

import { TickerCard } from "@/components/TickerCard";
import { ApiError, getTickers } from "@/lib/api";
import type { TickerInfo } from "@/lib/types";

export default function HomePage() {
  const [tickers, setTickers] = useState<TickerInfo[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTickers()
      .then((res) => setTickers(res.tickers))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load tickers"));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900">Supported tickers</h1>
      <p className="mt-1 text-sm text-slate-600">
        Plain-language explanations of the latest earnings call for each ticker. Pick one to read it.
      </p>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}

      {!tickers && !error && <p className="mt-6 text-sm text-slate-500">Loading tickers...</p>}

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
