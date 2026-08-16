"use client";

import { useEffect, useState } from "react";

import { ApiError, getStats } from "@/lib/api";
import type { TickerStats } from "@/lib/types";
import { InfoTooltip } from "./InfoTooltip";
import { Skeleton } from "./Skeleton";

type StatKey = keyof Omit<TickerStats, "ticker">;

interface StatDef {
  key: StatKey;
  label: string;
  // General-audience explanation of what the number means for the stock,
  // plus a rough "what's typical" range - this product's whole premise is
  // not assuming finance background, so a jargon-y ratio name never ships
  // without context a beginner can actually use.
  definition: string;
  format: (value: number) => string;
  // Only set for metrics with an unambiguous "beat/missed a benchmark"
  // zero-point (alpha). Everything else stays neutral - a high P/E or
  // low Sharpe isn't simply good or bad without more context, so it
  // shouldn't visually imply a judgment. See .claude/skills/fintech-ui.
  signColored?: boolean;
}

const percent = (v: number) => `${v.toFixed(2)}%`;
const ratio = (v: number) => v.toFixed(2);

const VALUATION_GROUP_DESCRIPTION =
  "How the stock's price compares to the company's earnings, assets, and payouts - these help gauge whether the stock looks cheap or expensive relative to the actual business behind it.";

const RISK_GROUP_DESCRIPTION =
  "How much the stock's price tends to swing, and whether it has rewarded investors enough for that risk compared to the overall market.";

const VALUATION_STATS: StatDef[] = [
  {
    key: "pe_ratio",
    label: "P/E Ratio",
    definition:
      "Shows how much investors are paying for each $1 of the company's yearly profit. A P/E of 20 means paying $20 for every $1 earned. Roughly 15-25 is considered a fair valuation for most established companies; below 15 can mean the stock is undervalued (or the market has concerns); above 25-30 usually means investors expect fast growth ahead.",
    format: ratio,
  },
  {
    key: "pb_ratio",
    label: "P/B Ratio",
    definition:
      "Compares the stock price to the company's net worth (what it owns minus what it owes) per share. Under 1 can mean the stock trades below its accounting value - potentially a bargain, or a warning sign. 1-3 is typical for a healthy company; above 3-5 is common for fast-growing or tech-heavy businesses whose real value isn't fully captured on the balance sheet.",
    format: ratio,
  },
  {
    key: "peg_ratio",
    label: "PEG Ratio",
    definition:
      "Takes the P/E ratio and adjusts it for how fast the company is expected to grow. Around 1 suggests the price is well-matched to that growth. Below 1 is often seen as undervalued relative to growth; above 2 can mean investors are paying a steep premium for it.",
    format: ratio,
  },
  {
    key: "dividend_yield",
    label: "Dividend Yield",
    definition:
      "The percentage of the stock price paid back to shareholders each year as cash dividends. 2-4% is typical for a stable, mature company (banks, utilities). Above 5-6% can mean a generous payout - or a red flag if the price has recently dropped a lot. Many growth companies (tech, biotech) pay 0% and reinvest profits into the business instead.",
    format: percent,
  },
];

const RISK_STATS: StatDef[] = [
  {
    key: "sharpe_ratio",
    label: "Sharpe Ratio",
    definition:
      "Measures how much return the stock earned for the amount of risk (price swings) it took on, over the past year. Above 1 is generally considered good, above 2 is very good, and below 0 means it didn't even beat a safe investment like a Treasury bond.",
    format: ratio,
  },
  {
    key: "sortino_ratio",
    label: "Sortino Ratio",
    definition:
      "Similar to the Sharpe Ratio, but only counts downside risk (price drops) instead of all price swings, so it doesn't penalize a stock for volatility that worked in your favor. Above 1 is generally considered good, and higher is better.",
    format: ratio,
  },
  {
    key: "beta",
    label: "Beta",
    definition:
      "Measures how much the stock moves compared to the overall market. 1.0 means it tends to move in line with the market; above 1 means bigger swings (more volatile); below 1 means smaller, steadier moves. A rare negative beta means it tends to move opposite the market.",
    format: ratio,
  },
  {
    key: "alpha",
    label: "Alpha",
    definition:
      "The extra return (or shortfall) the stock delivered over the past year compared to what its risk level (beta) would predict. Positive means it outperformed expectations; negative means it underperformed. Values are usually small - beyond +/-5% in a year is a notably large deviation.",
    format: ratio,
    signColored: true,
  },
];

function StatTile({ def, value, loading }: { def: StatDef; value: number | null; loading: boolean }) {
  const colorClass =
    !loading && def.signColored && value !== null
      ? value >= 0
        ? "text-positive-700"
        : "text-red-700"
      : "text-slate-900";

  return (
    <div className="relative rounded-xl border border-slate-200 bg-white p-3.5">
      <div className="flex items-center gap-1.5">
        <p className="text-xs font-medium text-slate-500">{def.label}</p>
        <InfoTooltip text={def.definition} />
      </div>
      {loading ? (
        <Skeleton className="mt-1.5 h-5 w-12" />
      ) : (
        <p className={`mt-1 text-lg font-bold tabular-nums ${colorClass}`}>
          {value !== null ? (def.signColored && value >= 0 ? "+" : "") + def.format(value) : "N/A"}
        </p>
      )}
    </div>
  );
}

function StatGroup({
  title,
  description,
  stats,
  data,
}: {
  title: string;
  description: string;
  stats: StatDef[];
  data: TickerStats | null;
}) {
  return (
    <div>
      <div className="relative flex items-center gap-1.5">
        <h3 className="text-sm font-semibold text-slate-700">{title}</h3>
        <InfoTooltip text={description} />
      </div>
      <div className="mt-2 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map((def) => (
          <StatTile key={def.key} def={def} value={data ? data[def.key] : null} loading={!data} />
        ))}
      </div>
    </div>
  );
}

export function StatsGrid({ ticker }: { ticker: string }) {
  const [data, setData] = useState<TickerStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setData(null);
    setError(null);
    getStats(ticker)
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load stats"));
  }, [ticker]);

  if (error) {
    return <p className="mt-6 text-sm text-red-600">{error}</p>;
  }

  return (
    <div className="mt-6 space-y-5">
      <StatGroup
        title="Valuation & Profitability"
        description={VALUATION_GROUP_DESCRIPTION}
        stats={VALUATION_STATS}
        data={data}
      />
      <StatGroup
        title="Risk & Performance"
        description={RISK_GROUP_DESCRIPTION}
        stats={RISK_STATS}
        data={data}
      />
    </div>
  );
}
