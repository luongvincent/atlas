"use client";

import Link from "next/link";

import { Button, buttonClass } from "@/components/Button";

// Shown when a page crashes while rendering. The error text is intentionally
// not displayed - it's for developers, and Next already logs it.
export default function ErrorPage({ reset }: { error: Error; reset: () => void }) {
  return (
    <div role="alert" className="max-w-[40rem] py-8">
      <h1 className="font-serif text-4xl font-semibold tracking-tight text-slate-900">Something went wrong</h1>
      <p className="mt-4 font-serif text-lg leading-8 text-slate-700">
        This page ran into a problem. Trying again often fixes it. If it keeps happening, come back in a few
        minutes.
      </p>
      <div className="mt-6 flex flex-wrap gap-3">
        <Button size="md" onClick={reset}>
          Try again
        </Button>
        <Link href="/" className={buttonClass("secondary", "md")}>
          Go to the home page
        </Link>
      </div>
    </div>
  );
}
