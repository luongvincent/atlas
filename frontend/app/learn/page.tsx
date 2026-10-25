import Link from "next/link";

import { INSIGHTS } from "@/lib/insights";

export default function LearnPage() {
  return (
    <div>
      <h1 className="font-serif text-4xl font-semibold tracking-tight text-slate-900">Learn</h1>
      <p className="mt-3 max-w-[65ch] font-serif text-lg leading-8 text-slate-700">
        Short, plain-language notes on how to read what you&apos;re looking at.
      </p>

      <ul className="mt-8 divide-y divide-slate-200 border-y border-slate-200">
        {INSIGHTS.map((insight) => (
          <li key={insight.slug}>
            <Link
              href={`/learn/${insight.slug}`}
              className="group block px-2 py-5 transition-colors hover:bg-white"
            >
              <h2 className="font-serif text-xl font-semibold leading-snug text-slate-900 group-hover:text-brand-700">
                {insight.title}
              </h2>
              <p className="mt-1.5 max-w-[65ch] text-sm leading-relaxed text-slate-600">{insight.summary}</p>
              <p className="mt-2 text-sm text-slate-500">
                {insight.date}
                <span className="mx-1.5 text-slate-300" aria-hidden="true">
                  |
                </span>
                {insight.readTime}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
