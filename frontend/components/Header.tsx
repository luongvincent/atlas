"use client";

import Link from "next/link";
import { useState } from "react";

import { useAuth } from "./AuthProvider";

export function Header() {
  const { user, loading, signIn, signUp, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [signupNotice, setSignupNotice] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSignupNotice(null);
    setSubmitting(true);
    const errMessage = mode === "signin" ? await signIn(email, password) : await signUp(email, password);
    setSubmitting(false);
    if (errMessage) {
      setError(errMessage);
      return;
    }
    if (mode === "signup") {
      setSignupNotice("Account created. Check your email to confirm, then sign in.");
      setMode("signin");
      return;
    }
    setOpen(false);
    setEmail("");
    setPassword("");
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-lg font-semibold text-slate-900">
          Earnings Call Explainer
        </Link>

        <nav className="flex items-center gap-4">
          <Link href="/onboarding" className="text-sm text-slate-600 hover:text-slate-900">
            Risk profile quiz
          </Link>

          {loading ? null : user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-600">{user.email}</span>
              <button
                onClick={() => signOut()}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50"
              >
                Sign out
              </button>
            </div>
          ) : (
            <div className="relative">
              <button
                onClick={() => setOpen((v) => !v)}
                className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700"
              >
                Sign in
              </button>

              {open && (
                <div className="absolute right-0 z-10 mt-2 w-72 rounded-lg border border-slate-200 bg-white p-4 shadow-lg">
                  <div className="mb-3 flex gap-2 text-sm">
                    <button
                      className={`flex-1 rounded-md py-1.5 ${mode === "signin" ? "bg-brand-50 text-brand-700" : "text-slate-500"}`}
                      onClick={() => setMode("signin")}
                    >
                      Sign in
                    </button>
                    <button
                      className={`flex-1 rounded-md py-1.5 ${mode === "signup" ? "bg-brand-50 text-brand-700" : "text-slate-500"}`}
                      onClick={() => setMode("signup")}
                    >
                      Sign up
                    </button>
                  </div>

                  <form onSubmit={handleSubmit} className="space-y-2">
                    <input
                      type="email"
                      required
                      placeholder="Email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
                    />
                    <input
                      type="password"
                      required
                      minLength={6}
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
                    />
                    {error && <p className="text-xs text-red-600">{error}</p>}
                    <button
                      type="submit"
                      disabled={submitting}
                      className="w-full rounded-md bg-brand-600 py-1.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
                    >
                      {submitting ? "..." : mode === "signin" ? "Sign in" : "Create account"}
                    </button>
                  </form>
                </div>
              )}
            </div>
          )}
        </nav>
      </div>
      {signupNotice && (
        <div className="bg-green-50 px-4 py-2 text-center text-sm text-green-700">{signupNotice}</div>
      )}
    </header>
  );
}
