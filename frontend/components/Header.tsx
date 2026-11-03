"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { useAuth } from "./AuthProvider";
import { Button, buttonClass } from "./Button";

const NAV_LINKS = [
  { href: "/tickers", label: "Stocks" },
  { href: "/etfs", label: "ETFs" },
  { href: "/learn", label: "Learn" },
  { href: "/onboarding", label: "Preferences" },
  { href: "/team", label: "Team" },
];

export function Header() {
  const { user, loading, signOut } = useAuth();
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  // Preferences needs an account, so signed-out visitors don't see it.
  const links = NAV_LINKS.filter((link) => user || link.href !== "/onboarding").map((link) => {
    const active = pathname === link.href || pathname?.startsWith(`${link.href}/`);
    return (
      <Link
        key={link.href}
        href={link.href}
        onClick={() => setMenuOpen(false)}
        className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
          active ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        }`}
      >
        {link.label}
      </Link>
    );
  });

  const auth = loading ? null : user ? (
    <>
      <span
        role="img"
        aria-label={`Signed in as ${user.email ?? "unknown user"}`}
        className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700"
      >
        {user.email?.[0]?.toUpperCase() ?? "?"}
      </span>
      <Button variant="secondary" onClick={() => signOut()}>
        Sign out
      </Button>
    </>
  ) : (
    <Link href="/login" onClick={() => setMenuOpen(false)} className={buttonClass()}>
      Sign in
    </Link>
  );

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5 rounded-lg">
          {/* Decorative: the wordmark beside it already names the link. */}
          <Image src="/logo-mark.png" alt="" width={36} height={36} className="h-9 w-9 object-contain mix-blend-multiply" priority />
          <span className="whitespace-nowrap font-display text-xl font-semibold tracking-tight text-slate-900">Atlas</span>
        </Link>

        <nav aria-label="Main" className="hidden items-center gap-1 md:flex">
          {links}
          <div className="ml-2 flex items-center gap-3 border-l border-slate-200 pl-3">{auth}</div>
        </nav>

        <button
          type="button"
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
          onClick={() => setMenuOpen((o) => !o)}
          className="rounded-lg border border-slate-300 p-2 text-slate-700 transition-colors hover:bg-slate-50 md:hidden"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            {menuOpen ? <path d="M5 5l10 10M15 5L5 15" /> : <path d="M3 6h14M3 10h14M3 14h14" />}
          </svg>
        </button>
      </div>

      {menuOpen && (
        <nav id="mobile-menu" aria-label="Main" className="border-t border-slate-200 px-4 py-3 md:hidden">
          <div className="flex flex-col gap-1">{links}</div>
          <div className="mt-3 flex items-center gap-3 border-t border-slate-200 pt-3">{auth}</div>
        </nav>
      )}
    </header>
  );
}
