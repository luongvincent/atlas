"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useAuth } from "./AuthProvider";
import { Button } from "./Button";

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

    router.replace("/tickers");
  }

  return (
    <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
      <div className="mb-5 flex gap-1 rounded-lg bg-slate-100 p-1 text-sm">
        <button
          type="button"
          className={`flex-1 rounded-md py-1.5 font-medium transition-colors ${
            mode === "signin" ? "bg-white text-brand-700 shadow-sm" : "text-slate-500 hover:text-slate-700"
          }`}
          onClick={() => setMode("signin")}
        >
          Sign in
        </button>
        <button
          type="button"
          className={`flex-1 rounded-md py-1.5 font-medium transition-colors ${
            mode === "signup" ? "bg-white text-brand-700 shadow-sm" : "text-slate-500 hover:text-slate-700"
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
          <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">Password</label>
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
