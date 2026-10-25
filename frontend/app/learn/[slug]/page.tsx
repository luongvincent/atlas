import Link from "next/link";
import { notFound } from "next/navigation";

import { getInsight } from "@/lib/insights";

export default function InsightPage({ params }: { params: { slug: string } }) {
  const insight = getInsight(params.slug);

  if (!insight) {
    notFound();
  }

  return (
    <div className="max-w-[65ch]">
      <Link href="/learn" className="text-sm font-medium text-brand-700 hover:underline">
        ← Back to Learn
      </Link>

      <h1 className="mt-3 font-serif text-4xl font-semibold leading-tight tracking-tight text-slate-900">
        {insight.title}
      </h1>
      <div className="mt-3 flex items-center gap-2 text-sm text-slate-500">
        <span>{insight.date}</span>
        <span className="text-slate-300">&middot;</span>
        <span>{insight.readTime}</span>
      </div>

      <div className="mt-8 space-y-5">
        {insight.content.map((paragraph, i) => (
          <p key={i} className="font-serif text-[1.0625rem] leading-8 text-slate-700">
            {paragraph}
          </p>
        ))}
      </div>
    </div>
  );
}