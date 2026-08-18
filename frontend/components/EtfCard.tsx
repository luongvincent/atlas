"use client";

import Link from "next/link";
import { useState } from "react";

import type { EtfInfo } from "@/lib/types";
import { Badge } from "./Badge";

export function EtfCard({ etf }: { etf: EtfInfo }) {
  const [logoFailed, setLogoFailed] = useState(false);
  // Same pattern/location convention as the stock tickers'
  // frontend/public/tickers/{ticker}.jpeg - drop files at
  // frontend/public/etfs/{ticker-lowercased}.jpeg (dots/hyphens in
  // CAD tickers like "xiu.to.jpeg" or "dlr-u.to.jpeg" are valid in
  // filenames, no substitution needed) and they'll be picked up
  // automatically; falls back to a letter avatar if missing.
  const logoSrc = `/etfs/${etf.ticker.toLowerCase()}.jpeg`;

  return (
    <Link
      href={`/etfs/${etf.ticker}`}
      className="group block rounded-2xl border border-slate-200 border-l-4 border-l-brand-200 bg-white p-4 shadow-card transition-all duration-150 hover:-translate-y-0.5 hover:border-brand-300 hover:border-l-brand-500 hover:shadow-card-hover"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2.5">
          {!logoFailed ? (
            <img
              src={logoSrc}
              alt=""
              className="h-9 w-9 shrink-0 rounded-lg border border-slate-100 object-contain"
              onError={() => setLogoFailed(true)}
            />
          ) : (
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-sm font-bold text-brand-700 transition-colors group-hover:bg-brand-100">
              {etf.ticker[0]}
            </span>
          )}
          <span className="text-lg font-bold tracking-tight text-slate-900 group-hover:text-brand-700">
            {etf.ticker}
          </span>
        </div>
        <span className="text-xs font-medium text-slate-400">{etf.exchange}</span>
      </div>
      <p className="mt-2 truncate text-sm text-slate-600">{etf.name}</p>

      <p className="mt-3 text-xs tabular-nums text-slate-500">
        Avg daily volume: <span className="font-medium text-slate-700">{etf.avg_daily_volume.toLocaleString()}</span>
      </p>

      <div className="mt-3">
        <Badge tone="neutral">{etf.category}</Badge>
      </div>
    </Link>
  );
}
