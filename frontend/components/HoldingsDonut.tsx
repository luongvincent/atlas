"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { HoldingEntry } from "@/lib/types";

// Pre-validated categorical order, taken directly from the dataviz skill's
// reference palette (references/palette.md, slots 1-6) rather than hand-
// picked - passes the adjacent-pair CVD/normal-vision floors in this exact
// order (worst adjacent ΔE 9.1, target >=8). Slices always render in
// descending-weight order (data-driven, never shuffled), which is the
// "adjacent pairlist" this sequence was validated against - a true
// all-pairs form (random adjacency, e.g. scatter) only clears 3 slots
// under the same method, which is too few to be useful here.
const DONUT_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"];
// Intentionally neutral/de-emphasized - "Other" isn't a real holding
// identity competing for attention, just an aggregate remainder.
const OTHER_COLOR = "#94a3b8";
const MAX_NAMED_SLICES = 6;

interface DonutSlice {
  key: string;
  label: string;
  percent: number;
  color: string;
}

function buildSlices(holdings: HoldingEntry[]): DonutSlice[] {
  const top = holdings.slice(0, MAX_NAMED_SLICES);
  const slices: DonutSlice[] = top.map((h, i) => ({
    key: h.ticker,
    label: h.ticker,
    percent: h.weight_percent,
    color: DONUT_COLORS[i % DONUT_COLORS.length],
  }));

  // "Other" = 100% minus the named slices, not just holdings 7-10 - a
  // diversified fund's top 10 often sum to well under half the fund, so
  // omitting this would visually claim the shown slices ARE the whole
  // fund (a pie/donut inherently implies its slices sum to 100%).
  const shownTotal = top.reduce((sum, h) => sum + h.weight_percent, 0);
  const other = Math.max(0, 100 - shownTotal);
  if (other > 0.01) {
    slices.push({ key: "__other__", label: "Other", percent: other, color: OTHER_COLOR });
  }
  return slices;
}

interface DonutTooltipProps {
  active?: boolean;
  payload?: { payload: DonutSlice }[];
}

function DonutTooltip({ active, payload }: DonutTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;
  const slice = payload[0].payload;
  return (
    <div className="max-w-[220px] rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-card-hover">
      <p className="text-sm font-semibold text-slate-900">{slice.label}</p>
      <p className="text-xs tabular-nums text-slate-600">{slice.percent.toFixed(2)}%</p>
      {slice.key === "__other__" && (
        <p className="mt-1 text-xs leading-relaxed text-slate-500">
          Holdings ranked below what&apos;s shown, plus anything this data source doesn&apos;t
          individually disclose for this fund.
        </p>
      )}
    </div>
  );
}

export function HoldingsDonut({ holdings }: { holdings: HoldingEntry[] }) {
  const slices = buildSlices(holdings);
  if (slices.length === 0) return null;

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row">
      <div className="h-36 w-36 shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={slices}
              dataKey="percent"
              nameKey="label"
              innerRadius="62%"
              outerRadius="100%"
              paddingAngle={1.5}
              stroke="#ffffff"
              strokeWidth={2}
              isAnimationActive={false}
            >
              {slices.map((s) => (
                <Cell key={s.key} fill={s.color} />
              ))}
            </Pie>
            <Tooltip content={<DonutTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="flex-1">
        {/* Direct labels, not tooltip-only - three of the six hues above dip
            below 3:1 contrast on white per the reference palette's own
            disclosure, so color alone isn't a reliable read for everyone. */}
        <ul className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
          {slices.map((s) => (
            <li key={s.key} className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: s.color }} />
              <span className="truncate font-medium text-slate-700">{s.label}</span>
              <span className="ml-auto shrink-0 tabular-nums text-slate-500">{s.percent.toFixed(1)}%</span>
            </li>
          ))}
        </ul>

        {slices.some((s) => s.key === "__other__") && (
          <p className="mt-2 text-xs leading-relaxed text-slate-400">
            &quot;Other&quot; includes holdings ranked below what&apos;s shown, plus anything this data
            source doesn&apos;t individually disclose - for some funds that&apos;s most of it.
          </p>
        )}
      </div>
    </div>
  );
}
