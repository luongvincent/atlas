import Link from "next/link";

import { buttonClass } from "@/components/Button";

const SECTIONS = [
  { title: "What happened", body: "The headline numbers, in everyday words." },
  { title: "What management actually said", body: "Their outlook and tone, with hedged language flagged." },
  { title: "What analysts pushed back on", body: "The tough questions from the Q&A." },
  { title: "Why it matters", body: "The takeaway, with no jargon." },
];

export default function HomePage() {
  return (
    <div className="py-4 sm:py-10">
      <section className="max-w-[40rem]">
        <h1 className="font-serif text-4xl font-semibold leading-tight tracking-tight text-slate-900 sm:text-5xl">
          Earnings calls, explained in plain English.
        </h1>
        <p className="mt-5 font-serif text-xl leading-9 text-slate-700">
          Every quarter, public companies hold a call to explain their results. The calls are long, full of
          jargon, and made for professionals. Atlas turns the latest one into four short sections anyone can read.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/tickers" className={buttonClass("primary", "md")}>
            Browse the top 15 stocks
          </Link>
          <Link href="/learn" className={buttonClass("secondary", "md")}>
            Learn the basics
          </Link>
        </div>
      </section>

      <section className="mt-16" aria-labelledby="example-heading">
        <h2 id="example-heading" className="font-serif text-2xl font-semibold tracking-tight text-slate-900">
          What that looks like
        </h2>
        <p className="mt-1 text-sm text-slate-500">An example from Apple&apos;s latest earnings call.</p>

        <div className="mt-6 grid gap-8 md:grid-cols-2">
          <div className="border-t border-slate-200 pt-4">
            <h3 className="text-sm font-semibold text-slate-500">What management said</h3>
            <p className="mt-2 font-serif text-lg leading-8 text-slate-800">
              Management said they{" "}
              <mark className="rounded-sm bg-moderate-100 px-0.5 text-slate-900 underline decoration-moderate-600 decoration-dotted underline-offset-4">
                expect
              </mark>{" "}
              revenue to grow 9-11% in the next quarter.
            </p>
          </div>
          <div className="border-t border-brand-500 pt-4">
            <h3 className="text-sm font-semibold text-brand-700">In plain English</h3>
            <p className="mt-2 font-serif text-lg leading-8 text-slate-800">
              &ldquo;Expect&rdquo; means they are predicting, not promising. It is an educated guess, so treat the
              number with some caution.
            </p>
          </div>
        </div>
      </section>

      <section className="mt-16 max-w-[65ch]" aria-labelledby="sections-heading">
        <h2 id="sections-heading" className="font-serif text-2xl font-semibold tracking-tight text-slate-900">
          What you get for each company
        </h2>
        <ul className="mt-4 divide-y divide-slate-200 border-y border-slate-200">
          {SECTIONS.map((s) => (
            <li key={s.title} className="py-4">
              <p className="font-serif text-lg font-semibold text-slate-900">{s.title}</p>
              <p className="mt-0.5 text-sm text-slate-600">{s.body}</p>
            </li>
          ))}
        </ul>
        <p className="mt-4 text-sm leading-relaxed text-slate-600">
          Each explanation lists the parts of the call it came from, so you can check it. Anyone can read the
          explanations that already exist. Sign in to generate new ones and to set how much detail you want.
        </p>
      </section>

      <section className="mt-16 max-w-[65ch]">
        <h2 className="font-serif text-2xl font-semibold tracking-tight text-slate-900">Look up anything else</h2>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          Search any US stock or US and Canadian ETF for its price, key numbers and, for ETFs, what it holds.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link href="/tickers" className={buttonClass("secondary", "sm")}>
            Search stocks
          </Link>
          <Link href="/etfs" className={buttonClass("secondary", "sm")}>
            Search ETFs
          </Link>
        </div>
      </section>
    </div>
  );
}
