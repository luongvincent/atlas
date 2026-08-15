"use client";

import { useEffect, useMemo, useState } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ApiError, getChart } from "@/lib/api";
import type { ChartPoint, ChartRangeOption } from "@/lib/types";
import { Skeleton } from "./Skeleton";

const RANGES: ChartRangeOption[] = ["1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "ALL"];

// Line color encodes gain/loss (emerald/red, reusing the app's existing
// semantic tokens) - always paired with the numeric change as text below,
// never color alone. See .claude/skills/fintech-ui/SKILL.md.
const POSITIVE_HEX = "#059669"; // positive-600
const NEGATIVE_HEX = "#dc2626"; // Tailwind red-600

const currencyFormatter = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

function formatTick(ts: string, range: ChartRangeOption): string {
  const date = new Date(ts);
  if (range === "1D") return date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
  if (range === "5D") return date.toLocaleDateString("en-US", { weekday: "short" });
  if (range === "5Y" || range === "ALL") {
    return date.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
  }
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function formatTooltipLabel(ts: string, range: ChartRangeOption): string {
  const date = new Date(ts);
  if (range === "1D" || range === "5D") {
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

interface ChartTooltipProps {
  active?: boolean;
  payload?: { payload: ChartPoint }[];
  range: ChartRangeOption;
}

function ChartTooltip({ active, payload, range }: ChartTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;
  const point = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-card-hover">
      <p className="text-xs text-slate-500">{formatTooltipLabel(point.timestamp, range)}</p>
      <p className="text-sm font-semibold tabular-nums text-slate-900">
        {currencyFormatter.format(point.close)}
      </p>
    </div>
  );
}

export function PriceChart({ ticker }: { ticker: string }) {
  const [range, setRange] = useState<ChartRangeOption>("1M");
  const [points, setPoints] = useState<ChartPoint[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPoints(null);
    setError(null);
    getChart(ticker, range)
      .then((res) => setPoints(res.points))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load chart"));
  }, [ticker, range]);

  const { changeAmount, changePercent, isUp } = useMemo(() => {
    if (!points || points.length < 2) return { changeAmount: 0, changePercent: 0, isUp: true };
    const first = points[0].close;
    const last = points[points.length - 1].close;
    const amount = last - first;
    return { changeAmount: amount, changePercent: first !== 0 ? (amount / first) * 100 : 0, isUp: amount >= 0 };
  }, [points]);

  const lineColor = isUp ? POSITIVE_HEX : NEGATIVE_HEX;
  const lastPrice = points && points.length > 0 ? points[points.length - 1].close : null;
  const gradientId = `chart-fill-${ticker}`;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          {lastPrice !== null ? (
            <>
              <p className="text-2xl font-bold tabular-nums text-slate-900">
                {currencyFormatter.format(lastPrice)}
              </p>
              {points && points.length >= 2 && (
                <p
                  className={`text-sm font-medium tabular-nums ${isUp ? "text-positive-700" : "text-red-700"}`}
                >
                  {isUp ? "+" : ""}
                  {currencyFormatter.format(changeAmount)} ({isUp ? "+" : ""}
                  {changePercent.toFixed(2)}%){" "}
                  <span className="font-normal text-slate-400">{range}</span>
                </p>
              )}
            </>
          ) : (
            <Skeleton className="h-8 w-28" />
          )}
        </div>

        <div className="flex gap-1 rounded-lg bg-slate-100 p-1 text-xs">
          {RANGES.map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={`rounded-md px-2.5 py-1.5 font-medium transition-colors ${
                range === r ? "bg-white text-brand-700 shadow-sm" : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 h-64">
        {error && (
          <p className="flex h-full items-center justify-center text-sm text-red-600">{error}</p>
        )}

        {!error && !points && <Skeleton className="h-full w-full" />}

        {!error && points && points.length > 0 && (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={points} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={lineColor} stopOpacity={0.18} />
                  <stop offset="100%" stopColor={lineColor} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} stroke="#e2e8f0" strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(ts: string) => formatTick(ts, range)}
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
                minTickGap={40}
              />
              <YAxis
                domain={["auto", "auto"]}
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => currencyFormatter.format(v).replace(".00", "")}
                width={60}
              />
              <Tooltip
                content={<ChartTooltip range={range} />}
                cursor={{ stroke: "#94a3b8", strokeDasharray: "3 3" }}
              />
              <Area
                type="monotone"
                dataKey="close"
                stroke={lineColor}
                strokeWidth={2}
                fill={`url(#${gradientId})`}
                dot={false}
                activeDot={{ r: 4, strokeWidth: 0 }}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {!error && points && points.length === 0 && (
          <p className="flex h-full items-center justify-center text-sm text-slate-500">
            No price data available.
          </p>
        )}
      </div>
    </div>
  );
}
