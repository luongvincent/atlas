"use client";

import { useEffect, useState } from "react";

import { EtfCard } from "@/components/EtfCard";
import { SearchSection } from "@/components/SearchSection";
import { Skeleton } from "@/components/Skeleton";
import { ApiError, getEtfs, getEtfsCa } from "@/lib/api";
import type { EtfInfo } from "@/lib/types";

type Region = "us" | "ca";

const REGION_COPY: Record<Region, { tab: string; title: string; description: string }> = {
  us: {
    tab: "US",
    title: "Top 15 US ETFs",
    description:
      "The most actively traded US ETFs by volume, excluding leveraged and inverse funds built for short-term trading rather than long-term investing.",
  },
  ca: {
    tab: "Canada",
    title: "Top 15 Canadian ETFs",
    description:
      "The most actively traded Canadian ETFs by volume, ranked separately from the US list since Canadian markets trade at a much smaller scale.",
  },
};

function EtfGridSkeleton() {
  return (
    <div className="mt-8 divide-y divide-slate-200 border-y border-slate-200">
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
  );
}

export default function EtfsPage() {
  const [region, setRegion] = useState<Region>("us");

  const [usEtfs, setUsEtfs] = useState<EtfInfo[] | null>(null);
  const [usError, setUsError] = useState<string | null>(null);
  const [caEtfs, setCaEtfs] = useState<EtfInfo[] | null>(null);
  const [caError, setCaError] = useState<string | null>(null);

  useEffect(() => {
    getEtfs()
      .then((res) => setUsEtfs(res.etfs))
      .catch((err) => setUsError(err instanceof ApiError ? err.message : "Failed to load ETFs"));
    getEtfsCa()
      .then((res) => setCaEtfs(res.etfs))
      .catch((err) => setCaError(err instanceof ApiError ? err.message : "Failed to load ETFs"));
  }, []);

  const etfs = region === "us" ? usEtfs : caEtfs;
  const error = region === "us" ? usError : caError;
  const copy = REGION_COPY[region];

  return (
    <div>
      <h1 className="font-serif text-4xl font-semibold tracking-tight text-slate-900">ETFs</h1>
      <p className="mt-3 max-w-[65ch] font-serif text-lg leading-8 text-slate-700">
        An ETF is a basket of investments you can buy as one. Look up any US or Canadian ETF for its price,
        key numbers and what it holds.
      </p>

      <SearchSection kind="etf">
        <div className="mt-10 flex flex-wrap items-center justify-between gap-4">
          <h2 className="font-serif text-2xl font-semibold tracking-tight text-slate-900">{copy.title}</h2>

          <div className="flex gap-1 rounded-lg bg-slate-100 p-1 text-sm">
            {(Object.keys(REGION_COPY) as Region[]).map((r) => (
              <button
                key={r}
                type="button"
                aria-pressed={region === r}
                onClick={() => setRegion(r)}
                className={`rounded-md px-3.5 py-1.5 font-medium transition-colors ${
                  region === r ? "bg-white text-brand-700 shadow-sm" : "text-slate-500 hover:text-slate-700"
                }`}
              >
                {REGION_COPY[r].tab}
              </button>
            ))}
          </div>
        </div>
        <p className="mt-2 max-w-[65ch] font-serif text-lg leading-8 text-slate-700">{copy.description}</p>

        {error && (
          <p className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
        )}

        {!etfs && !error && <EtfGridSkeleton />}

        {etfs && (
          <ul className="mt-8 divide-y divide-slate-200 border-y border-slate-200">
            {etfs.map((e) => (
              <EtfCard key={e.ticker} etf={e} />
            ))}
          </ul>
        )}
      </SearchSection>
    </div>
  );
}
