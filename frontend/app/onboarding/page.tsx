"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { Badge } from "@/components/Badge";
import { Button } from "@/components/Button";
import { Skeleton } from "@/components/Skeleton";
import { ApiError, getOnboarding, submitOnboarding } from "@/lib/api";
import type {
  Goal,
  InvestingExperience,
  OnboardingRequest,
  OnboardingResponse,
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
  conservative: "Explanations will emphasize stability and downside risk.",
  moderate: "Explanations will balance growth potential and risk.",
  aggressive: "Explanations will emphasize growth trajectory over short-term noise.",
};

const DEFAULT_FORM: OnboardingRequest = {
  investing_experience: "beginner",
  time_horizon: "medium_term",
  risk_comfort: 3,
  portfolio_size_range: "1k_10k",
  goals: "growth",
};

function formFromResponse(res: OnboardingResponse): OnboardingRequest {
  return {
    investing_experience: res.investing_experience,
    time_horizon: res.time_horizon,
    risk_comfort: res.risk_comfort,
    portfolio_size_range: res.portfolio_size_range,
    goals: res.goals,
  };
}

function OptionCards<T extends string>({
  options,
  value,
  name,
  onChange,
}: {
  options: { value: T; label: string }[];
  value: T;
  name: string;
  onChange: (value: T) => void;
}) {
  return (
    <div className="mt-2 space-y-2">
      {options.map((opt) => {
        const selected = value === opt.value;
        return (
          <label
            key={opt.value}
            className={`flex cursor-pointer items-center gap-3 rounded-lg border px-3.5 py-2.5 text-sm transition-colors ${
              selected
                ? "border-brand-500 bg-brand-50 text-brand-900"
                : "border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50"
            }`}
          >
            <input
              type="radio"
              name={name}
              checked={selected}
              onChange={() => onChange(opt.value)}
              className="h-4 w-4 accent-brand-600"
            />
            {opt.label}
          </label>
        );
      })}
    </div>
  );
}

const QUESTIONS = [
  { step: "01", legend: "Investing experience" },
  { step: "02", legend: "Time horizon" },
  { step: "03", legend: "Risk comfort" },
  { step: "04", legend: "Portfolio size" },
  { step: "05", legend: "Primary goal" },
];

function QuestionChip({ step }: { step: string }) {
  return (
    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-xs font-bold tabular-nums text-brand-700">
      {step}
    </span>
  );
}

export default function OnboardingPage() {
  const { user, session, loading: authLoading } = useAuth();

  // The saved preferences as last returned by the API, or null if the
  // user has never submitted them.
  const [savedProfile, setSavedProfile] = useState<OnboardingResponse | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);

  // Whether the form is currently open for editing. Irrelevant/ignored
  // when savedProfile is null, since the form is always shown in that case.
  const [editing, setEditing] = useState(false);

  const [form, setForm] = useState<OnboardingRequest>(DEFAULT_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;

    if (!user || !session) {
      setProfileLoading(false);
      return;
    }

    async function loadProfile() {
      try {
        const res = await getOnboarding(session!.access_token);
        if (res) {
          setSavedProfile(res);
        }
      } catch (err) {
        setError(
          err instanceof ApiError
            ? err.message
            : "Failed to load preferences"
        );
      } finally {
        setProfileLoading(false);
      }
    }

    loadProfile();
  }, [authLoading, user, session]);

  function handleEditClick() {
    if (savedProfile) {
      setForm(formFromResponse(savedProfile));
    }
    setError(null);
    setEditing(true);
  }

  function handleCancel() {
    setError(null);
    setEditing(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!session) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await submitOnboarding(form, session.access_token);
      setSavedProfile(res);
      setEditing(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading || profileLoading) {
    return (
      <div className="mx-auto max-w-xl">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="mt-2 h-4 w-full" />
        <div className="mt-6 flex flex-col items-center rounded-2xl border border-slate-200 bg-white p-8">
          <Skeleton className="h-12 w-12 rounded-full" />
          <Skeleton className="mt-4 h-4 w-32" />
          <Skeleton className="mt-3 h-6 w-24 rounded-full" />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="rounded-2xl border border-moderate-100 bg-moderate-50 p-4">
        <p className="text-sm text-moderate-700">
          <Link href="/login" className="font-medium underline">
            Sign in
          </Link>{" "}
          to set your explanation preferences.
        </p>
      </div>
    );
  }

  // Form is shown when there's nothing saved yet, or when explicitly editing.
  const showForm = !savedProfile || editing;

  return (
    <div className="mx-auto max-w-xl text-center">
      <h1 className="font-serif text-3xl font-semibold tracking-tight text-slate-900">Explanation preferences</h1>
      <p className="mt-2 font-serif text-lg leading-8 text-slate-700">
        5 quick questions. We use this to adjust the tone and depth of your explanations - not to
        give investment advice.
      </p>

      {!showForm && savedProfile ? (
        <div className="mt-6 flex flex-col items-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-card">
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-600 text-xl shadow-card">
            🎯
          </span>
          <p className="mt-4 text-sm font-medium text-slate-500">Your risk profile</p>
          <div className="mt-3">
            <Badge tone={savedProfile.risk_profile}>{savedProfile.risk_profile}</Badge>
          </div>
          <p className="mt-3 max-w-sm text-sm leading-relaxed text-slate-700">
            {RISK_PROFILE_COPY[savedProfile.risk_profile]}
          </p>
          <Button size="md" onClick={handleEditClick} className="mt-6">
            Edit preferences
          </Button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="mt-6 space-y-6">
          <fieldset className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
            <legend className="flex items-center gap-3 text-sm font-semibold text-slate-900">
              <QuestionChip step={QUESTIONS[0].step} />
              {QUESTIONS[0].legend}
            </legend>
            <OptionCards
              options={EXPERIENCE_OPTIONS}
              value={form.investing_experience}
              name="investing_experience"
              onChange={(v) => setForm((f) => ({ ...f, investing_experience: v }))}
            />
          </fieldset>

          <fieldset className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
            <legend className="flex items-center gap-3 text-sm font-semibold text-slate-900">
              <QuestionChip step={QUESTIONS[1].step} />
              {QUESTIONS[1].legend}
            </legend>
            <OptionCards
              options={HORIZON_OPTIONS}
              value={form.time_horizon}
              name="time_horizon"
              onChange={(v) => setForm((f) => ({ ...f, time_horizon: v }))}
            />
          </fieldset>

          <fieldset className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
            <legend className="flex w-full items-center gap-3 text-sm font-semibold text-slate-900">
              <QuestionChip step={QUESTIONS[2].step} />
              <span className="flex-1">Risk comfort</span>
              <span className="text-lg font-bold tabular-nums text-brand-700">{form.risk_comfort}/5</span>
            </legend>
            <input
              type="range"
              aria-label="Risk comfort, 1 (very cautious) to 5 (very comfortable)"
              min={1}
              max={5}
              value={form.risk_comfort}
              onChange={(e) => setForm((f) => ({ ...f, risk_comfort: Number(e.target.value) }))}
              className="mt-4 h-2 w-full cursor-pointer appearance-none rounded-full accent-brand-600"
              style={{
                background: "linear-gradient(to right, #0ea5e9, #f59e0b, #f43f5e)",
              }}
            />
            <div className="mt-1.5 flex justify-between text-xs text-slate-500">
              <span>Very cautious</span>
              <span>Very comfortable</span>
            </div>
          </fieldset>

          <fieldset className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
            <legend className="flex items-center gap-3 text-sm font-semibold text-slate-900">
              <QuestionChip step={QUESTIONS[3].step} />
              {QUESTIONS[3].legend}
            </legend>
            <select
              value={form.portfolio_size_range}
              onChange={(e) =>
                setForm((f) => ({ ...f, portfolio_size_range: e.target.value as PortfolioSizeRange }))
              }
              className="mt-3 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm transition-colors focus:border-brand-500"
            >
              {PORTFOLIO_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </fieldset>

          <fieldset className="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
            <legend className="flex items-center gap-3 text-sm font-semibold text-slate-900">
              <QuestionChip step={QUESTIONS[4].step} />
              {QUESTIONS[4].legend}
            </legend>
            <OptionCards
              options={GOAL_OPTIONS}
              value={form.goals}
              name="goals"
              onChange={(v) => setForm((f) => ({ ...f, goals: v }))}
            />
          </fieldset>

          {error && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
          )}

          <div className="flex gap-3">
            <Button type="submit" size="md" disabled={submitting}>
              {submitting ? "Saving..." : "Save preferences"}
            </Button>
            {savedProfile && (
              <Button variant="secondary" size="md" onClick={handleCancel} disabled={submitting}>
                Cancel
              </Button>
            )}
          </div>
        </form>
      )}
    </div>
  );
}