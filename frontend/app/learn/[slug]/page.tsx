import { notFound } from "next/navigation";

import { PageHero } from "@/components/PageHero";
import { getInsight } from "@/lib/insights";

export default function InsightPage({ params }: { params: { slug: string } }) {
  const insight = getInsight(params.slug);

  if (!insight) {
    notFound();
  }

  return (
    <div>
      <PageHero title={insight.title} back={{ href: "/learn", label: "Back to Learn" }}>
        <p className="text-sm">
          {insight.date}
          <span className="mx-1.5 text-slate-500" aria-hidden="true">
            |
          </span>
          {insight.readTime}
        </p>
      </PageHero>

      <div className="mt-10 max-w-[65ch] space-y-5">
        {insight.content.map((paragraph, i) => (
          <p key={i} className="font-serif text-[1.0625rem] leading-8 text-slate-700">
            {paragraph}
          </p>
        ))}
      </div>
    </div>
  );
}
