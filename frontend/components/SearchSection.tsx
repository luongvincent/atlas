"use client";

import Link from "next/link";
import { useEffect, useState, type ReactNode } from "react";

import { ApiError, searchStocks } from "@/lib/api";
import type { SearchKind, SearchResponse, SearchResult } from "@/lib/types";
import { Badge } from "./Badge";
import { Skeleton } from "./Skeleton";

const KIND_LABEL: Record<SearchKind, string> = { stock: "Stock", etf: "ETF" };
const KIND_PATH: Record<SearchKind, string> = { stock: "/tickers", etf: "/etfs" };

export function LeveragedWarning() {
  return (
    <p className="mt-1 max-w-[65ch] text-sm text-moderate-700">
      Leveraged or inverse fund: it moves 2-3 times the index each day, or the opposite way. It is built for
      short-term trading and can lose value fast. It is not meant to be held long term.
    </p>
  );
}

function SearchRow({ result }: { result: SearchResult }) {
  return (
    <li>
      <Link
        href={`${KIND_PATH[result.kind]}/${result.ticker}`}
        className="group flex flex-col gap-2 rounded-2xl px-4 py-5 transition-colors hover:bg-slate-50 sm:px-5 sm:flex-row sm:items-start sm:justify-between sm:gap-6"
      >
        <div className="min-w-0">
          <p className="font-serif text-lg font-semibold leading-tight text-slate-900 group-hover:text-brand-700">
            {result.company_name}
          </p>
          <p className="mt-0.5 text-sm text-slate-500">
            <span className="font-semibold text-slate-700">{result.ticker}</span>
            {result.exchange && (
              <>
                <span className="mx-1.5 text-slate-300" aria-hidden="true">
                  |
                </span>
                {result.exchange}
              </>
            )}
          </p>
          {result.leveraged && <LeveragedWarning />}
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          <Badge tone="neutral">{KIND_LABEL[result.kind]}</Badge>
          {result.leveraged && <Badge tone="warning">Leveraged / inverse</Badge>}
          {result.kind === "stock" && (
            <Badge tone={result.supported ? "positive" : "neutral"}>
              {result.supported ? "Explanation available" : "Price and stats only"}
            </Badge>
          )}
        </div>
      </Link>
    </li>
  );
}

/**
 * Search box plus results for one kind of security. While the box is empty it
 * renders `children` (the page's default list) instead.
 */
export function SearchSection({ kind, children }: { kind: SearchKind; children: ReactNode }) {
  const [query, setQuery] = useState("");
  const [data, setData] = useState<SearchResponse | null>(null);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const trimmed = query.trim();
  const noun = kind === "stock" ? "stocks" : "ETFs";
  const otherNoun = kind === "stock" ? "ETFs" : "stocks";

  // Debounced: wait for a pause in typing, and cancel any request that a newer
  // keystroke has made stale.
  useEffect(() => {
    if (!trimmed) {
      setData(null);
      setError(null);
      setSearching(false);
      return;
    }
    setSearching(true);
    const controller = new AbortController();
    const timer = setTimeout(() => {
      searchStocks(trimmed, kind, controller.signal)
        .then((res) => {
          setData(res);
          setError(null);
        })
        .catch((err) => {
          if (controller.signal.aborted) return;
          setError(err instanceof ApiError ? err.message : "Search failed. Check your connection and try again.");
        })
        .finally(() => {
          if (!controller.signal.aborted) setSearching(false);
        });
    }, 300);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [trimmed, kind]);

  const inputId = `${kind}-search`;
  const results = data?.results ?? [];
  const others = data?.other_matches ?? [];

  return (
    <>
      <div className="mt-6 max-w-xl">
        <label htmlFor={inputId} className="mb-1 block text-sm font-medium text-slate-700">
          Search {noun} by name or ticker
        </label>
        <input
          id={inputId}
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          maxLength={50}
          autoComplete="off"
          placeholder={kind === "stock" ? "For example: Tesla or AMD" : "For example: Vanguard or VTI"}
          className="w-full rounded-full border border-slate-300 bg-white px-5 py-3 text-base shadow-card transition-colors focus:border-brand-500"
        />
      </div>

      {!trimmed ? (
        children
      ) : (
        <div className="mt-8" aria-live="polite">
          {error && (
            <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </p>
          )}

          {!error && searching && !data && (
            <div className="row-list">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="px-4 py-5 sm:px-5">
                  <Skeleton className="h-5 w-48" />
                  <Skeleton className="mt-2 h-4 w-32" />
                </div>
              ))}
            </div>
          )}

          {!error && data && results.length > 0 && (
            <ul className={`row-list ${searching ? "opacity-60" : ""}`}>
              {results.map((r) => (
                <SearchRow key={r.ticker} result={r} />
              ))}
            </ul>
          )}

          {!error && data && results.length === 0 && !searching && (
            <p className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
              No {noun} found for &ldquo;{trimmed}&rdquo;. Try the full name or the ticker symbol.
            </p>
          )}

          {!error && data && others.length > 0 && (
            <div className="mt-6">
              <p className="text-sm font-medium text-slate-700">Also matches these {otherNoun}:</p>
              <ul className="row-list mt-2">
                {others.map((r) => (
                  <SearchRow key={r.ticker} result={r} />
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </>
  );
}
