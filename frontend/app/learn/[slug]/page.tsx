import Link from "next/link";
import { notFound } from "next/navigation";

import { getInsight } from "@/lib/insights";

export default function InsightPage({ params }: { params: { slug: string } }) {
  const insight = getInsight(params.slug);

  if (!insight) {
    notFound();
  }

  return (
    <div className="max-w-2xl">
      <Link href="/learn" className="text-sm font-medium text-brand-700 hover:underline">
        ← Back to Learn
      </Link>

      <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900">{insight.title}</h1>
      <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
        <span>{insight.date}</span>
        <span className="text-slate-300">&middot;</span>
        <span>{insight.readTime}</span>
      </div>

      <div className="mt-6 space-y-4">
        {insight.content.map((paragraph, i) => (
          <p key={i} className="text-sm leading-relaxed text-slate-700">
            {paragraph}
          </p>
        ))}
      </div>
    </div>
  );
}