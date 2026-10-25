import Link from "next/link";
import { useState } from "react";

import type { TickerInfo } from "@/lib/types";
import { Badge } from "./Badge";

// One row in the stocks index. Name file kept as TickerCard so imports stay put.
export function TickerCard({ ticker }: { ticker: TickerInfo }) {
  const ingested = Boolean(ticker.latest_quarter);
  const [logoFailed, setLogoFailed] = useState(false);
  const logoSrc = `/tickers/${ticker.ticker.toLowerCase()}.jpeg`;

  return (
    <li>
      <Link
        href={`/tickers/${ticker.ticker}`}
        className="group flex flex-col gap-3 px-2 py-5 transition-colors hover:bg-white sm:flex-row sm:items-center sm:justify-between sm:gap-6"
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
              {ticker.ticker[0]}
            </span>
          )}
          <div className="min-w-0">
            <p className="font-serif text-lg font-semibold leading-tight text-slate-900 group-hover:text-brand-700">
              {ticker.company_name}
            </p>
            <p className="mt-0.5 text-sm text-slate-500">
              <span className="font-semibold text-slate-700">{ticker.ticker}</span>
              <span className="mx-1.5 text-slate-300" aria-hidden="true">
                |
              </span>
              <span className="tabular-nums">{ticker.avg_daily_volume.toLocaleString()} shares traded per day</span>
            </p>
          </div>
        </div>

        <div className="flex shrink-0 flex-wrap items-center gap-x-3 gap-y-1 pl-14 sm:flex-col sm:items-end sm:gap-1 sm:pl-0">
          {ingested ? (
            <>
              <Badge tone="positive">{ticker.latest_quarter} earnings call</Badge>
              <span className="text-sm text-slate-500">{ticker.latest_call_date}</span>
            </>
          ) : (
            <Badge tone="neutral">Coming soon</Badge>
          )}
        </div>
      </Link>
    </li>
  );
}
