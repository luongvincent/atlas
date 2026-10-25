"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { Button } from "@/components/Button";
import { PriceChart } from "@/components/PriceChart";
import { assignDefinitions, RichText } from "@/components/RichText";
import { Skeleton } from "@/components/Skeleton";
import { SentimentCard } from "@/components/SentimentCard";
import { SimilarItems } from "@/components/SimilarItems";
import { StatsGrid } from "@/components/StatsGrid";
import { ApiError, getExplanation, requestExplanation } from "@/lib/api";
import type { ExplainResponse, GlossaryEntry } from "@/lib/types";

const SECTIONS: { key: keyof ExplainResponse["sections"]; id: string; label: string }[] = [
  { key: "what_happened", id: "what-happened", label: "What happened" },
  { key: "what_management_said", id: "what-management-said", label: "What management actually said" },
  { key: "what_analysts_pushed_back_on", id: "analyst-pushback", label: "What analysts pushed back on" },
  { key: "why_it_matters", id: "why-it-matters", label: "Why it matters" },
];

// "What happened" opens with its first sentence set large; every other section
// is a single paragraph.
function paragraphsFor(key: string, text: string): string[] {
  if (key !== "what_happened") return [text];
  const [lede, ...rest] = text.split(/(?<=[.!?])\s+/);
  return rest.length > 0 ? [lede, rest.join(" ")] : [lede];
}

function SectionBody({
  sectionKey,
  paragraphs,
  definitions,
}: {
  sectionKey: string;
  paragraphs: string[];
  // One entry per paragraph: the terms to underline there (see assignDefinitions).
  definitions: GlossaryEntry[][];
}) {
  if (sectionKey === "what_happened") {
    const [lede, ...rest] = paragraphs;
    return (
      <>
        <RichText
          text={lede}
          definitions={definitions[0]}
          className="mt-3 font-serif text-2xl font-semibold leading-snug text-slate-900"
        />
        {rest.length > 0 && (
          <RichText
            text={rest[0]}
            definitions={definitions[1]}
            className="mt-4 whitespace-pre-line font-serif text-[1.0625rem] leading-8 text-slate-700"
          />
        )}
      </>
    );
  }
  const hedged = sectionKey === "what_management_said";
  return (
    <>
      <RichText
        text={paragraphs[0]}
        definitions={definitions[0]}
        hedged={hedged}
        className="mt-3 whitespace-pre-line font-serif text-[1.0625rem] leading-8 text-slate-700"
      />
      {hedged && (
        <p className="mt-3 font-sans text-sm text-slate-500">
          Highlighted words mean the company is predicting, not promising.
        </p>
      )}
    </>
  );
}

export default function TickerExplainPage({ params }: { params: { ticker: string } }) {
  const ticker = params.ticker.toUpperCase();
  const { session, user, loading: authLoading } = useAuth();

  const [data, setData] = useState<ExplainResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(true);
  const [requestStatus, setRequestStatus] = useState<"idle" | "sending" | "sent">("idle");
  const [requestError, setRequestError] = useState<string | null>(null);

  async function handleRequest() {
    if (!session) return;
    setRequestStatus("sending");
    setRequestError(null);
    try {
      await requestExplanation(ticker, session.access_token);
      setRequestStatus("sent");
    } catch (err) {
      setRequestStatus("idle");
      setRequestError(err instanceof ApiError ? err.message : "We couldn't save your request. Please try again.");
    }
  }

  // Underline each jargon term once on the whole page, at its first mention.
  const paragraphsBySection = useMemo(
    () => (data ? SECTIONS.map(({ key }) => paragraphsFor(key, data.sections[key])) : []),
    [data],
  );
  const definitionsBySection = useMemo(() => {
    const perParagraph = assignDefinitions(paragraphsBySection.flat(), data?.definitions ?? []);
    let next = 0;
    return paragraphsBySection.map((paragraphs) => paragraphs.map(() => perParagraph[next++]));
  }, [paragraphsBySection, data]);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    getExplanation(ticker, session?.access_token)
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err : new ApiError(500, "Unknown error")))
      .finally(() => setLoading(false));
  }, [ticker, session?.access_token]);

  useEffect(() => {
    if (authLoading) return;
    load();
  }, [authLoading, load]);

  return (
    <div>
      <Link href="/tickers" className="text-sm font-medium text-brand-700 hover:underline">
        ← Back to stocks
      </Link>

      <h1 className="mt-2 font-serif text-4xl font-semibold tracking-tight text-slate-900">
        {data?.company_name ?? ticker}
      </h1>

      {data && (
        <>
          <p className="mt-2 text-sm text-slate-600">
            <span className="font-semibold text-slate-900">{ticker}</span>
            <span className="mx-1.5 text-slate-300" aria-hidden="true">
              |
            </span>
            {data.quarter} earnings call
            <span className="mx-1.5 text-slate-300" aria-hidden="true">
              |
            </span>
            {data.generated_at
              ? `Written ${new Date(data.generated_at).toLocaleDateString()}`
              : "Just written for you"}
          </p>
        </>
      )}

      <section id="price" aria-labelledby="price-heading" className="mt-6 scroll-mt-28">
        <h2 id="price-heading" className="sr-only">
          Price and key numbers
        </h2>
        <PriceChart ticker={ticker} />
        <StatsGrid ticker={ticker} />
      </section>

      <SentimentCard ticker={ticker} />

      <SimilarItems ticker={ticker} />

      {loading && (
        <div className="mt-6 space-y-4">
          <p role="status" className="text-sm text-slate-600">
            Reading the transcript and writing your explanation. The first time can take up to a minute.
          </p>
          <Skeleton className="h-4 w-64" />
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="max-w-[65ch] border-t border-slate-200 pt-6">
              <Skeleton className="h-5 w-48" />
              <Skeleton className="mt-3 h-3 w-full" />
              <Skeleton className="mt-2 h-3 w-5/6" />
              <Skeleton className="mt-2 h-3 w-2/3" />
            </div>
          ))}
        </div>
      )}

      {error && error.status === 401 && (
        <div className="mt-6 rounded-2xl border border-moderate-100 bg-moderate-50 p-4">
          <p className="text-sm text-moderate-700">{error.message}</p>
          {!user && (
            <p className="mt-2 text-sm text-moderate-700">
              <Link href="/login" className="font-medium underline">
                Sign in
              </Link>{" "}
              then come back to this page.
            </p>
          )}
          {user && (
            <Button onClick={load} className="mt-3">
              Retry now that you're signed in
            </Button>
          )}
        </div>
      )}

      {error && error.status === 404 && (
        <div className="mt-6 max-w-[65ch] border-t border-slate-200 pt-6">
          <p className="font-serif text-lg leading-8 text-slate-700">{error.message}</p>
          <p className="mt-1 text-sm text-slate-500">The price chart and key numbers above are still available.</p>

          {requestStatus === "sent" ? (
            <p role="status" className="mt-4 rounded-lg bg-positive-50 px-3 py-2 text-sm text-positive-700">
              Request saved. We&apos;ll look at it when choosing which stocks to explain next.
            </p>
          ) : user ? (
            <Button className="mt-4" onClick={handleRequest} disabled={requestStatus === "sending"}>
              {requestStatus === "sending" ? "Saving request..." : "Request an explanation"}
            </Button>
          ) : (
            <p className="mt-4 text-sm text-slate-600">
              <Link href="/login" className="font-medium text-brand-700 underline">
                Sign in
              </Link>{" "}
              to request an explanation for {ticker}.
            </p>
          )}

          {requestError && (
            <p role="alert" className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {requestError}
            </p>
          )}
        </div>
      )}

      {error && error.status !== 401 && error.status !== 404 && (
        <div role="alert" className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-700">{error.message}</p>
          <Button onClick={load} className="mt-3">
            Try again
          </Button>
        </div>
      )}

      {data && (
        <div className="relative mt-10 max-w-[65ch] space-y-10">
          {/* Desktop only: sits in the empty space beside the reading column. */}
          <nav aria-label="On this page" className="absolute left-full top-0 ml-16 hidden h-full w-56 lg:block">
            <div className="sticky top-28">
              <p className="text-sm font-semibold text-slate-900">On this page</p>
              <ul className="mt-3 border-l border-slate-200">
                {[
                  { id: "price", label: "Price and key numbers" },
                  ...SECTIONS,
                  ...(data.citations.length > 0 ? [{ id: "citations", label: "Citations" }] : []),
                ].map(
                  ({ id, label }) => (
                    <li key={id}>
                      <a
                        href={`#${id}`}
                        className="-ml-px block border-l-2 border-transparent py-1.5 pl-3 text-sm text-slate-600 transition-colors hover:border-brand-500 hover:text-brand-700"
                      >
                        {label}
                      </a>
                    </li>
                  ),
                )}
              </ul>
            </div>
          </nav>

          <div className="rounded-xl border border-brand-100 bg-brand-50 px-4 py-3">
            <p className="text-sm leading-relaxed text-brand-900">
              <span className="font-semibold">This is an AI-generated explanation, not financial advice.</span>{" "}
              Use it to understand what happened - not as a recommendation to buy, sell, or hold.
            </p>
          </div>

          {SECTIONS.map(({ key, id, label }, s) => (
            <section key={key} id={id} className="scroll-mt-28 border-t border-slate-200 pt-6">
              <h2 className="font-serif text-2xl font-semibold tracking-tight text-slate-900">{label}</h2>
              <SectionBody
                sectionKey={key}
                paragraphs={paragraphsBySection[s]}
                definitions={definitionsBySection[s]}
              />
            </section>
          ))}

          {data.glossary.length > 0 && (
            <section className="border-t border-slate-200 pt-6">
              <h2 className="font-serif text-2xl font-semibold tracking-tight text-slate-900">Terms used</h2>
              <dl className="mt-3 space-y-2.5">
                {data.glossary.map((g) => (
                  <div key={g.term} className="text-sm">
                    <dt className="inline font-semibold capitalize text-slate-900">{g.term}: </dt>
                    <dd className="inline text-slate-700">{g.definition}</dd>
                  </div>
                ))}
              </dl>
            </section>
          )}

          {data.citations.length > 0 && (
            <section id="citations" className="scroll-mt-28 border-t border-slate-200 pt-6">
              <h2 className="font-serif text-2xl font-semibold tracking-tight text-slate-900">Citations</h2>
              <ul className="mt-3 divide-y divide-slate-200 border-y border-slate-200">
                {data.citations.map((c, i) => (
                  <li key={i} className="py-3 text-sm">
                    <p className="text-slate-700">{c.claim}</p>
                    <p className="mt-1 text-slate-500">
                      <span className="font-medium text-slate-900">{c.speaker}</span>
                      {", "}
                      {c.section === "qa" ? "Q&A" : "prepared remarks"}
                    </p>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
