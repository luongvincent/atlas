import Link from "next/link";
import type { ReactNode } from "react";

// The dark page header shared by every page below the landing hero.
export function PageHero({
  title,
  back,
  children,
}: {
  title: ReactNode;
  back?: { href: string; label: string };
  children?: ReactNode;
}) {
  return (
    <section className="rounded-3xl bg-slate-900 px-6 py-8 sm:px-10 sm:py-12">
      {back && (
        <Link href={back.href} className="mb-3 inline-block text-sm font-medium text-slate-300 hover:text-white hover:underline">
          ← {back.label}
        </Link>
      )}
      <h1 className="font-serif text-4xl font-semibold leading-tight tracking-tight text-white sm:text-5xl">{title}</h1>
      {children && <div className="mt-4 max-w-[65ch] text-slate-300">{children}</div>}
    </section>
  );
}
