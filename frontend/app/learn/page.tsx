import Link from "next/link";

import { INSIGHTS } from "@/lib/insights";

export default function LearnPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold tracking-tight text-slate-900">Learn</h1>
      <p className="mt-1 text-sm text-slate-600">
        Short, plain-language notes on how to read what you're looking at.
      </p>

      <div className="mt-6 space-y-4">
        {INSIGHTS.map((insight) => (
          <Link
            key={insight.slug}
            href={`/learn/${insight.slug}`}
            className="group block rounded-2xl border border-slate-200 border-l-4 border-l-brand-200 bg-white p-5 shadow-card transition-all duration-150 hover:-translate-y-0.5 hover:border-brand-300 hover:border-l-brand-500 hover:shadow-card-hover"
          >
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-lg font-semibold tracking-tight text-slate-900 group-hover:text-brand-700">
                {insight.title}
              </h2>
              <span className="shrink-0 text-xs font-medium text-slate-400">{insight.readTime}</span>
            </div>
            <p className="mt-1.5 text-sm text-slate-600">{insight.summary}</p>
            <p className="mt-3 text-xs font-medium text-slate-400">{insight.date}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}