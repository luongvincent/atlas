"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/Badge";
import { HoldingsBreakdown } from "@/components/HoldingsBreakdown";
import { PriceChart } from "@/components/PriceChart";
import { Skeleton } from "@/components/Skeleton";
import { StatsGrid } from "@/components/StatsGrid";
import { LeveragedWarning } from "@/components/SearchSection";
import { ApiError, getEtfs, getEtfsCa, searchStocks } from "@/lib/api";
import type { EtfInfo, SearchResult } from "@/lib/types";

export default function EtfDetailPage({ params }: { params: { ticker: string } }) {
  const ticker = params.ticker.toUpperCase();

  const [etf, setEtf] = useState<EtfInfo | null>(null);
  const [unlisted, setUnlisted] = useState<SearchResult | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // The ticker could be in either list (US or Canada) - check both rather
    // than assuming US, and only fall back to an error if BOTH requests
    // fail (one list being briefly unreachable shouldn't hide a ticker
    // that's actually findable in the other).
    Promise.allSettled([getEtfs(), getEtfsCa()]).then(([usResult, caResult]) => {
      const usEtfs = usResult.status === "fulfilled" ? usResult.value.etfs : [];
      const caEtfs = caResult.status === "fulfilled" ? caResult.value.etfs : [];
      const match = [...usEtfs, ...caEtfs].find((e) => e.ticker === ticker);

      if (match) {
        setEtf(match);
        return;
      }

      if (usResult.status === "rejected" && caResult.status === "rejected") {
        const err = usResult.reason;
        setError(err instanceof ApiError ? err.message : "Failed to load ETF");
        return;
      }

      // Not on the curated lists: it may still be a real ETF (search covers them all).
      searchStocks(ticker, "etf")
        .then((res) => {
          const found = res.results.find((r) => r.ticker === ticker);
          if (found) setUnlisted(found);
          else setNotFound(true);
        })
        .catch(() => setError("We couldn't look up this ETF right now. Please try again in a moment."));
    });
  }, [ticker]);

  return (
    <div>
      <Link href="/etfs" className="text-sm font-medium text-brand-700 hover:underline">
        ← Back to ETFs
      </Link>

      <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{ticker}</h1>

      {error && (
        <p role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {notFound && (
        <div className="mt-6 max-w-[65ch] border-t border-slate-200 pt-6">
          <p className="font-serif text-lg leading-8 text-slate-700">We couldn&apos;t find an ETF with the ticker {ticker}.</p>
          <Link href="/etfs" className="mt-2 inline-block text-sm font-medium text-brand-700 hover:underline">
            See the ETFs we cover
          </Link>
        </div>
      )}

      {!etf && !unlisted && !notFound && !error && (
        <div className="mt-2 flex items-center gap-2">
          <Skeleton className="h-5 w-56" />
        </div>
      )}

      {etf && (
        <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600">
          <span className="font-semibold text-slate-900">{etf.name}</span>
          <span className="text-slate-300">&middot;</span>
          <Badge tone="neutral">{etf.category}</Badge>
        </div>
      )}

      {unlisted && (
        <>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600">
            <span className="font-semibold text-slate-900">{unlisted.company_name}</span>
            <span className="text-slate-300">&middot;</span>
            <Badge tone="neutral">ETF</Badge>
            {unlisted.leveraged && <Badge tone="warning">Leveraged / inverse</Badge>}
          </div>
          {unlisted.leveraged && <LeveragedWarning />}
        </>
      )}

      {!notFound && (
        <>
          <div className="mt-4">
            <PriceChart ticker={ticker} />
          </div>

          <StatsGrid ticker={ticker} />

          <HoldingsBreakdown ticker={ticker} />
        </>
      )}
    </div>
  );
}
