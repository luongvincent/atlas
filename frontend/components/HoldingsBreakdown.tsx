"use client";

import { useEffect, useState } from "react";

import { ApiError, getEtfHoldings } from "@/lib/api";
import type { EtfHoldings } from "@/lib/types";
import { HoldingsDonut } from "./HoldingsDonut";
import { Skeleton } from "./Skeleton";

// Bar length beats pie-chart angle for comparing magnitudes - see
// .claude/skills/fintech-ui and the dataviz method it follows. Bars are
// scaled relative to the largest value in *this* list (not literally to
// 100%), since even the biggest single holding in a diversified fund is
// rarely more than ~10% - scaling to the max makes relative differences
// within the top 10 actually readable instead of all-tiny-slivers.
function BarRow({ label, sublabel, percent, maxPercent }: { label: string; sublabel?: string; percent: number; maxPercent: number }) {
  const widthPercent = maxPercent > 0 ? (percent / maxPercent) * 100 : 0;
  return (
    <div>
      <div className="flex items-baseline justify-between gap-2 text-sm">
        <span className="truncate font-medium text-slate-900">
          {label}
          {sublabel && <span className="ml-1.5 font-normal text-slate-400">{sublabel}</span>}
        </span>
        <span className="shrink-0 tabular-nums font-semibold text-slate-700">{percent.toFixed(2)}%</span>
      </div>
      <div className="mt-1 h-1.5 w-full rounded-full bg-slate-100">
        <div className="h-1.5 rounded-full bg-brand-500" style={{ width: `${widthPercent}%` }} />
      </div>
    </div>
  );
}

export function HoldingsBreakdown({ ticker }: { ticker: string }) {
  const [data, setData] = useState<EtfHoldings | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setData(null);
    setError(null);
    getEtfHoldings(ticker)
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load holdings"));
  }, [ticker]);

  if (error) {
    return (
      <p className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">{error}</p>
    );
  }

  const maxHoldingPercent = data ? Math.max(...data.top_holdings.map((h) => h.weight_percent), 0) : 0;
  const maxSectorPercent = data ? Math.max(...data.sector_weightings.map((s) => s.weight_percent), 0) : 0;

  return (
    <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
        <h3 className="text-sm font-semibold text-slate-700">Top Holdings</h3>
        <p className="mt-0.5 text-xs text-slate-400">What this fund actually owns, by weight.</p>

        {!data && (
          <div className="mt-4 flex items-center gap-4">
            <Skeleton className="h-36 w-36 shrink-0 rounded-full" />
            <div className="flex-1 space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-4 w-full" />
              ))}
            </div>
          </div>
        )}
        {data && data.top_holdings.length > 0 && (
          <div className="mt-4">
            <HoldingsDonut holdings={data.top_holdings} />
          </div>
        )}

        <div className="mt-5 space-y-3 border-t border-slate-100 pt-4">
          {!data &&
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i}>
                <Skeleton className="h-4 w-40" />
                <Skeleton className="mt-1.5 h-1.5 w-full rounded-full" />
              </div>
            ))}
          {data?.top_holdings.map((h) => (
            <BarRow key={h.ticker} label={h.ticker} sublabel={h.name} percent={h.weight_percent} maxPercent={maxHoldingPercent} />
          ))}
          {data && data.top_holdings.length === 0 && (
            <p className="text-sm text-slate-500">No holdings data available.</p>
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
        <h3 className="text-sm font-semibold text-slate-700">Sector Breakdown</h3>
        <p className="mt-0.5 text-xs text-slate-400">Which parts of the economy this fund is exposed to.</p>
        <div className="mt-4 space-y-3">
          {!data &&
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i}>
                <Skeleton className="h-4 w-32" />
                <Skeleton className="mt-1.5 h-1.5 w-full rounded-full" />
              </div>
            ))}
          {data?.sector_weightings.map((s) => (
            <BarRow key={s.sector} label={s.sector} percent={s.weight_percent} maxPercent={maxSectorPercent} />
          ))}
          {data && data.sector_weightings.length === 0 && (
            <p className="text-sm text-slate-500">No sector data available.</p>
          )}
        </div>
      </div>
    </div>
  );
}
