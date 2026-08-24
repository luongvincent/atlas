import Link from "next/link";

import { getRecommendedInsights } from "@/lib/insights";
import type { InvestingExperience } from "@/lib/types";

export function RecommendedArticles({ experience }: { experience: InvestingExperience }) {
  const recommended = getRecommendedInsights(experience, 3);
  if (recommended.length === 0) return null;

  return (
    <div className="mt-6 text-left">
      <h3 className="text-sm font-semibold text-slate-700">Recommended reading for you</h3>
      <div className="mt-2 space-y-2.5">
        {recommended.map((insight) => (
          <Link
            key={insight.slug}
            href={`/learn/${insight.slug}`}
            className="group block rounded-xl border border-slate-200 bg-white px-4 py-3 transition-colors hover:border-brand-300 hover:bg-brand-50/40"
          >
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-medium text-slate-900 group-hover:text-brand-700">
                {insight.title}
              </p>
              <span className="shrink-0 text-xs text-slate-400">{insight.readTime}</span>
            </div>
            <p className="mt-0.5 truncate text-xs text-slate-500">{insight.summary}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
