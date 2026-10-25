import Link from "next/link";

import { buttonClass } from "@/components/Button";

export default function NotFound() {
  return (
    <div className="max-w-[40rem] py-8">
      <h1 className="font-serif text-4xl font-semibold tracking-tight text-slate-900">
        We couldn&apos;t find that page
      </h1>
      <p className="mt-4 font-serif text-lg leading-8 text-slate-700">
        The link may be mistyped, or the page may have moved. Try one of these instead.
      </p>
      <div className="mt-6 flex flex-wrap gap-3">
        <Link href="/" className={buttonClass("primary", "md")}>
          Go to the home page
        </Link>
        <Link href="/tickers" className={buttonClass("secondary", "md")}>
          Browse stocks
        </Link>
        <Link href="/etfs" className={buttonClass("secondary", "md")}>
          Browse ETFs
        </Link>
      </div>
    </div>
  );
}
