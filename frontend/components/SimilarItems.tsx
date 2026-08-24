"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getSimilarItems } from "@/lib/api";
import type { SimilarItem } from "@/lib/types";
import { Skeleton } from "./Skeleton";

function formatVolume(volume: number): string {
  if (volume >= 1_000_000) return `${(volume / 1_000_000).toFixed(1)}M avg volume`;
  if (volume >= 1_000) return `${(volume / 1_000).toFixed(0)}K avg volume`;
  return `${volume} avg volume`;
}

export function SimilarItems({ ticker }: { ticker: string }) {
  const [items, setItems] = useState<SimilarItem[] | null>(null);

  useEffect(() => {
    setItems(null);
    getSimilarItems(ticker)
      .then((res) => setItems(res.items))
      .catch(() => setItems([]));
  }, [ticker]);

  if (items === null) {
    return (
      <div className="mt-6">
        <Skeleton className="h-4 w-40" />
        <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (items.length === 0) return null;

  return (
    <div className="mt-6">
      <h2 className="text-base font-semibold text-slate-900">Similar to {ticker}</h2>
      <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {items.map((item) => (
          <Link
            key={item.ticker}
            href={item.kind === "etf" ? `/etfs/${item.ticker}` : `/tickers/${item.ticker}`}
            className="group block rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-card transition-colors hover:border-brand-300 hover:bg-brand-50/40"
          >
            <div className="flex items-center justify-between gap-3">
              <span className="text-sm font-semibold text-slate-900 group-hover:text-brand-700">
                {item.ticker}
              </span>
              <span className="text-xs text-slate-400">{formatVolume(item.avg_daily_volume)}</span>
            </div>
            <p className="mt-0.5 truncate text-xs text-slate-500">{item.name}</p>
            <p className="mt-1 text-xs font-medium text-brand-600">{item.reason}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
