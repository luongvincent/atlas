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
    <div className="space-y-16 sm:space-y-20">
      <section className="rounded-3xl bg-slate-900 px-6 py-10 sm:px-12 sm:py-16">
        <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-14">
          <div>
            <h1 className="font-serif text-4xl font-semibold leading-tight tracking-tight text-white sm:text-6xl sm:leading-[1.05]">
              Earnings calls, explained in plain English.
            </h1>
            <p className="mt-6 max-w-[34rem] text-lg leading-8 text-slate-300">
              Every quarter, public companies hold a call to explain their results. The calls are long, full of jargon,
              and made for professionals. Atlas turns the latest one into four short sections anyone can read.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/tickers" className={buttonClass("light", "md")}>
                Browse the top 15 stocks
              </Link>
              <Link href="/learn" className={buttonClass("ghost", "md")}>
                Learn the basics
              </Link>
            </div>
          </div>

          <figure className="rounded-2xl bg-white p-6 shadow-card sm:p-8">
            <figcaption className="text-sm text-slate-600">Example of how Atlas translates a call</figcaption>
            <p className="mt-5 text-sm font-semibold text-slate-600">What management said</p>
            <p className="mt-1 font-serif text-lg leading-8 text-slate-800">
              Management said they{" "}
              <mark className="rounded-sm bg-moderate-100 px-0.5 text-slate-900 underline decoration-moderate-600 decoration-dotted underline-offset-4">
                expect
              </mark>{" "}
              revenue to grow 9-11% in the next quarter.
            </p>
            <p className="mt-6 border-t border-slate-200 pt-6 text-sm font-semibold text-brand-700">In plain English</p>
            <p className="mt-1 font-serif text-lg leading-8 text-slate-800">
              &ldquo;Expect&rdquo; means they are predicting, not promising. It is an educated guess, so treat the
              number with some caution.
            </p>
          </figure>
        </div>
      </section>

      <section aria-labelledby="sections-heading">
        <h2 id="sections-heading" className="font-serif text-3xl font-semibold tracking-tight text-slate-900">
          What you get for each company
        </h2>
        <ul className="mt-8 grid gap-x-10 gap-y-8 sm:grid-cols-2">
          {SECTIONS.map((s) => (
            <li key={s.title} className="border-t border-slate-200 pt-4">
              <p className="font-serif text-xl font-semibold text-slate-900">{s.title}</p>
              <p className="mt-1 text-slate-600">{s.body}</p>
            </li>
          ))}
        </ul>
        <p className="mt-8 max-w-[65ch] text-sm leading-relaxed text-slate-600">
          Each explanation lists the parts of the call it came from, so you can check it. Anyone can read the
          explanations that already exist. Sign in to generate new ones and to set how much detail you want.
        </p>
      </section>

      <section className="flex flex-col gap-6 rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 md:flex-row md:items-center md:justify-between">
        <div className="max-w-[65ch]">
          <h2 className="font-serif text-2xl font-semibold tracking-tight text-slate-900">Look up anything else</h2>
          <p className="mt-2 text-sm leading-relaxed text-slate-600">
            Search any US stock or US and Canadian ETF for its price, key numbers and, for ETFs, what it holds.
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-3">
          <Link href="/tickers" className={buttonClass("secondary", "md")}>
            Search stocks
          </Link>
          <Link href="/etfs" className={buttonClass("secondary", "md")}>
            Search ETFs
          </Link>
        </div>
      </section>
    </div>
  );
}
