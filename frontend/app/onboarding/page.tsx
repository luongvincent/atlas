"use client";

import { useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { ApiError, submitOnboarding } from "@/lib/api";
import type {
  Goal,
  InvestingExperience,
  OnboardingRequest,
  PortfolioSizeRange,
  RiskProfileLabel,
  TimeHorizon,
} from "@/lib/types";

const EXPERIENCE_OPTIONS: { value: InvestingExperience; label: string }[] = [
  { value: "none", label: "I've never invested" },
  { value: "beginner", label: "Beginner - a little experience" },
  { value: "intermediate", label: "Intermediate - fairly comfortable" },
  { value: "experienced", label: "Experienced investor" },
];

const HORIZON_OPTIONS: { value: TimeHorizon; label: string }[] = [
  { value: "short_term", label: "Short term (< 1 year)" },
  { value: "medium_term", label: "Medium term (1-5 years)" },
  { value: "long_term", label: "Long term (5+ years)" },
];

const PORTFOLIO_OPTIONS: { value: PortfolioSizeRange; label: string }[] = [
  { value: "under_1k", label: "Under $1,000" },
  { value: "1k_10k", label: "$1,000 - $10,000" },
  { value: "10k_100k", label: "$10,000 - $100,000" },
  { value: "100k_1m", label: "$100,000 - $1,000,000" },
  { value: "over_1m", label: "Over $1,000,000" },
];

const GOAL_OPTIONS: { value: Goal; label: string }[] = [
  { value: "preserve_capital", label: "Preserve what I have" },
  { value: "income", label: "Generate income" },
  { value: "growth", label: "Grow my money over time" },
  { value: "speculation", label: "Speculate for big gains" },
];

const RISK_PROFILE_COPY: Record<RiskProfileLabel, string> = {
  conservative: "Conservative - explanations will emphasize stability and downside risk.",
  moderate: "Moderate - explanations will balance growth potential and risk.",
  aggressive: "Aggressive - explanations will emphasize growth trajectory over short-term noise.",
};

export default function OnboardingPage() {
  const { user, session, loading: authLoading } = useAuth();
  const [form, setForm] = useState<OnboardingRequest>({
    investing_experience: "beginner",
    time_horizon: "medium_term",
    risk_comfort: 3,
    portfolio_size_range: "1k_10k",
    goals: "growth",
  });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<RiskProfileLabel | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!session) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await submitOnboarding(form, session.access_token);
      setResult(res.risk_profile);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading) return null;

  if (!user) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
        <p className="text-sm text-amber-800">Sign in above to take the risk profile quiz.</p>
      </div>
    );
  }

  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold text-slate-900">Risk profile quiz</h1>
      <p className="mt-1 text-sm text-slate-600">
        5 quick questions. We use this to adjust the tone and depth of your explanations - not to give
        investment advice.
      </p>

      {result ? (
        <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-medium text-green-800">Your risk profile: {result}</p>
          <p className="mt-1 text-sm text-green-700">{RISK_PROFILE_COPY[result]}</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="mt-6 space-y-6">
          <fieldset>
            <legend className="text-sm font-medium text-slate-900">Investing experience</legend>
            <div className="mt-2 space-y-1">
              {EXPERIENCE_OPTIONS.map((opt) => (
                <label key={opt.value} className="flex items-center gap-2 text-sm text-slate-700">
                  <input
                    type="radio"
                    name="investing_experience"
                    checked={form.investing_experience === opt.value}
                    onChange={() => setForm((f) => ({ ...f, investing_experience: opt.value }))}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset>
            <legend className="text-sm font-medium text-slate-900">Time horizon</legend>
            <div className="mt-2 space-y-1">
              {HORIZON_OPTIONS.map((opt) => (
                <label key={opt.value} className="flex items-center gap-2 text-sm text-slate-700">
                  <input
                    type="radio"
                    name="time_horizon"
                    checked={form.time_horizon === opt.value}
                    onChange={() => setForm((f) => ({ ...f, time_horizon: opt.value }))}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset>
            <legend className="text-sm font-medium text-slate-900">
              Risk comfort: {form.risk_comfort} / 5
            </legend>
            <input
              type="range"
              min={1}
              max={5}
              value={form.risk_comfort}
              onChange={(e) => setForm((f) => ({ ...f, risk_comfort: Number(e.target.value) }))}
              className="mt-2 w-full"
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>Very cautious</span>
              <span>Very comfortable</span>
            </div>
          </fieldset>

          <fieldset>
            <legend className="text-sm font-medium text-slate-900">Portfolio size</legend>
            <select
              value={form.portfolio_size_range}
              onChange={(e) =>
                setForm((f) => ({ ...f, portfolio_size_range: e.target.value as PortfolioSizeRange }))
              }
              className="mt-2 w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            >
              {PORTFOLIO_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </fieldset>

          <fieldset>
            <legend className="text-sm font-medium text-slate-900">Primary goal</legend>
            <div className="mt-2 space-y-1">
              {GOAL_OPTIONS.map((opt) => (
                <label key={opt.value} className="flex items-center gap-2 text-sm text-slate-700">
                  <input
                    type="radio"
                    name="goals"
                    checked={form.goals === opt.value}
                    onChange={() => setForm((f) => ({ ...f, goals: opt.value }))}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </fieldset>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
          >
            {submitting ? "Submitting..." : "Submit"}
          </button>
        </form>
      )}
    </div>
  );
}
