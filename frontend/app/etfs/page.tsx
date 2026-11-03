"use client";

import { useEffect, useState } from "react";

import { EtfCard } from "@/components/EtfCard";
import { PageHero } from "@/components/PageHero";
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
    <div className="row-list mt-8">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 px-4 py-5 sm:px-5">
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
      <PageHero title="ETFs">
        <p className="text-lg leading-8">
          An ETF is a basket of investments you can buy as one. Look up any US or Canadian ETF for its price,
          key numbers and what it holds.
        </p>
      </PageHero>

      <SearchSection kind="etf">
        <div className="mt-10 flex flex-wrap items-center justify-between gap-4">
          <h2 className="font-serif text-2xl font-semibold tracking-tight text-slate-900">{copy.title}</h2>

          <div className="flex gap-1 rounded-full bg-slate-200 p-1 text-sm">
            {(Object.keys(REGION_COPY) as Region[]).map((r) => (
              <button
                key={r}
                type="button"
                aria-pressed={region === r}
                onClick={() => setRegion(r)}
                className={`rounded-full px-3.5 py-1.5 font-medium transition-colors ${
                  region === r ? "bg-white text-brand-700 shadow-sm" : "text-slate-700 hover:text-slate-900"
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
          <ul className="row-list mt-8">
            {etfs.map((e) => (
              <EtfCard key={e.ticker} etf={e} />
            ))}
          </ul>
        )}
      </SearchSection>
    </div>
  );
}
