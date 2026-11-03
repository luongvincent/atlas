import Link from "next/link";

import { PageHero } from "@/components/PageHero";
import { INSIGHTS } from "@/lib/insights";

export default function LearnPage() {
  return (
    <div>
      <PageHero title="Learn">
        <p className="text-lg leading-8">Short, plain-language notes on how to read what you&apos;re looking at.</p>
      </PageHero>

      <ul className="row-list mt-8">
        {INSIGHTS.map((insight) => (
          <li key={insight.slug}>
            <Link
              href={`/learn/${insight.slug}`}
              className="group block rounded-2xl px-4 py-5 transition-colors hover:bg-slate-50 sm:px-5"
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
