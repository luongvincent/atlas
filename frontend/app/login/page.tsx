"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/AuthProvider";
import { LoginForm } from "@/components/LoginForm";

export default function LoginPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.replace("/tickers");
    }
  }, [loading, user, router]);

  if (loading || user) return null;

  return (
    <div className="flex flex-col items-center py-16">
      <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600 text-xl font-bold text-white shadow-card">
        A
      </span>
      <h1 className="mb-1 text-2xl font-bold tracking-tight text-slate-900">Atlas Capital</h1>
      <p className="mb-1 text-sm font-medium text-brand-700">Stocks, plainly explained.</p>
      <p className="mb-8 text-sm text-slate-600">Sign in to generate and personalize explanations.</p>
      <LoginForm />
    </div>
  );
}
