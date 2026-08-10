import Link from "next/link";

import type { TickerInfo } from "@/lib/types";
import { Badge } from "./Badge";

export function TickerCard({ ticker }: { ticker: TickerInfo }) {
  const ingested = Boolean(ticker.latest_quarter);

  return (
    <Link
      href={`/tickers/${ticker.ticker}`}
      className="group block rounded-2xl border border-slate-200 bg-white p-4 shadow-card transition-all duration-150 hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-card-hover"
    >
      <div className="flex items-baseline justify-between">
        <span className="text-lg font-bold tracking-tight text-slate-900 group-hover:text-brand-700">
          {ticker.ticker}
        </span>
        <span className="text-xs font-medium text-slate-400">{ticker.exchange}</span>
      </div>
      <p className="mt-0.5 truncate text-sm text-slate-600">{ticker.company_name}</p>

      <p className="mt-3 text-xs tabular-nums text-slate-500">
        Avg daily volume: <span className="font-medium text-slate-700">{ticker.avg_daily_volume.toLocaleString()}</span>
      </p>

      <div className="mt-3 flex items-center gap-2">
        {ingested ? (
          <>
            <Badge tone="positive">{ticker.latest_quarter}</Badge>
            <span className="truncate text-xs text-slate-400">{ticker.latest_call_date}</span>
          </>
        ) : (
          <Badge tone="neutral">Not yet ingested</Badge>
        )}
      </div>
    </Link>
  );
}
