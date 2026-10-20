"use client";

import { useEffect } from "react";
import Image from "next/image";
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
      <Image
        src="/logo.png"
        alt="Atlas Capital"
        width={56}
        height={56}
        className="mb-4 h-14 w-14 rounded-lg object-cover shadow-card"
        priority
      />
      <h1 className="mb-1 font-serif text-3xl font-semibold tracking-tight text-slate-900">Atlas Capital</h1>
      <p className="mb-1 text-sm font-medium text-brand-700">Stocks, plainly explained.</p>
      <p className="mb-8 text-sm text-slate-600">Sign in to generate and personalize explanations.</p>
      <LoginForm />
    </div>
  );
}
