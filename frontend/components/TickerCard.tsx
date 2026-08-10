import Link from "next/link";

import type { TickerInfo } from "@/lib/types";

export function TickerCard({ ticker }: { ticker: TickerInfo }) {
  const ingested = Boolean(ticker.latest_quarter);

  return (
    <Link
      href={`/tickers/${ticker.ticker}`}
      className="block rounded-lg border border-slate-200 bg-white p-4 transition hover:border-brand-500 hover:shadow-sm"
    >
      <div className="flex items-baseline justify-between">
        <span className="text-lg font-semibold text-slate-900">{ticker.ticker}</span>
        <span className="text-xs text-slate-500">{ticker.exchange}</span>
      </div>
      <p className="mt-1 truncate text-sm text-slate-600">{ticker.company_name}</p>
      <p className="mt-3 text-xs text-slate-500">
        Avg daily volume: {ticker.avg_daily_volume.toLocaleString()}
      </p>
      <p className="mt-1 text-xs">
        {ingested ? (
          <span className="text-green-700">
            Latest: {ticker.latest_quarter} ({ticker.latest_call_date})
          </span>
        ) : (
          <span className="text-slate-400">Not yet ingested</span>
        )}
      </p>
    </Link>
  );
}
