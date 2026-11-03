"use client";

import Link from "next/link";
import { useState } from "react";

import type { EtfInfo } from "@/lib/types";
import { Badge } from "./Badge";

// One row in the ETF index; same layout as TickerCard so the two lists match.
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
    <li>
      <Link
        href={`/etfs/${etf.ticker}`}
        className="group flex flex-col gap-3 rounded-2xl px-4 py-5 transition-colors hover:bg-slate-50 sm:px-5 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
      >
        <div className="flex min-w-0 items-center gap-4">
          {!logoFailed ? (
            <img
              src={logoSrc}
              alt=""
              className="h-10 w-10 shrink-0 rounded-lg border border-slate-200 object-contain"
              onError={() => setLogoFailed(true)}
            />
          ) : (
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-sm font-bold text-brand-700">
              {etf.ticker[0]}
            </span>
          )}
          <div className="min-w-0">
            <p className="font-serif text-lg font-semibold leading-tight text-slate-900 group-hover:text-brand-700">
              {etf.name}
            </p>
            <p className="mt-0.5 text-sm text-slate-500">
              <span className="font-semibold text-slate-700">{etf.ticker}</span>
              <span className="mx-1.5 text-slate-300" aria-hidden="true">
                |
              </span>
              <span className="tabular-nums">{etf.avg_daily_volume.toLocaleString()} shares traded per day</span>
            </p>
          </div>
        </div>

        <div className="shrink-0 pl-14 sm:pl-0">
          <Badge tone="neutral">{etf.category}</Badge>
        </div>
      </Link>
    </li>
  );
}
