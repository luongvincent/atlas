"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "./AuthProvider";

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

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4.8">
        <Link href="/" className="flex items-center gap-2">
          <Image
            src="/logo.png"
            alt="Atlas Capital"
            width={56}
            height={56}
            className="h-14 w-14 rounded-lg object-cover"
            priority
          />
          <span className="text-xl font-semibold tracking-tight text-slate-900">Atlas Capital</span>
        </Link>

        <nav className="flex items-center gap-1">
          {NAV_LINKS.map((link) => {
            const active = pathname === link.href || pathname?.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  active ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                {link.label}
              </Link>
            );
          })}

          <div className="ml-2 flex items-center gap-3 border-l border-slate-200 pl-3">
            {loading ? null : user ? (
              <>
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
                  {user.email?.[0]?.toUpperCase() ?? "?"}
                </span>
                <button
                  onClick={() => signOut()}
                  className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50"
                >
                  Sign out
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="rounded-md bg-brand-600 px-3.5 py-1.5 text-sm font-medium text-white transition-colors hover:bg-brand-700"
              >
                Sign in
              </Link>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}
