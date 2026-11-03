"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useAuth } from "./AuthProvider";
import { Button } from "./Button";

// Where to go after signing in: ?next=/some/path, same-origin only (parsed, so
// tricks like "/\evil.com" that browsers read as "//evil.com" fall back too).
export function safeNext(next: string | null, origin: string): string {
  if (!next) return "/tickers";
  try {
    const u = new URL(next, origin);
    return u.origin === origin ? u.pathname + u.search + u.hash : "/tickers";
  } catch {
    return "/tickers";
  }
}

export function nextPath(): string {
  return safeNext(new URLSearchParams(window.location.search).get("next"), window.location.origin);
}

export function LoginForm() {
  const { signIn, signUp } = useAuth();
  const router = useRouter();

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
      setSignupNotice("Account created. Check your email to confirm, then sign in below.");
      setMode("signin");
      setPassword("");
      return;
    }

    router.replace(nextPath());
  }

  return (
    <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
      <div className="mb-5 flex gap-1 rounded-lg bg-slate-100 p-1 text-sm">
        <button
          type="button"
          aria-pressed={mode === "signin"}
          className={`flex-1 rounded-md py-1.5 font-medium transition-colors ${
            mode === "signin" ? "bg-white text-brand-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
          onClick={() => setMode("signin")}
        >
          Sign in
        </button>
        <button
          type="button"
          aria-pressed={mode === "signup"}
          className={`flex-1 rounded-md py-1.5 font-medium transition-colors ${
            mode === "signup" ? "bg-white text-brand-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
          onClick={() => setMode("signup")}
        >
          Sign up
        </button>
      </div>

      {signupNotice && (
        <p className="mb-4 rounded-md bg-positive-50 px-3 py-2 text-sm text-positive-700">{signupNotice}</p>
      )}

      <form onSubmit={handleSubmit} className="space-y-3.5">
        <div>
          <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700">Email</label>
          <input
            id="email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm transition-colors focus:border-brand-500"
          />
        </div>
        <div>
          <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">
            Password <span className="font-normal text-slate-500">(at least 6 characters)</span>
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={6}
            autoComplete={mode === "signin" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm transition-colors focus:border-brand-500"
          />
        </div>

        {error && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        )}

        <Button type="submit" size="md" disabled={submitting} className="w-full">
          {submitting ? "One moment..." : mode === "signin" ? "Sign in" : "Create account"}
        </Button>
      </form>
    </div>
  );
}
