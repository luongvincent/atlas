"use client";

import { useEffect } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/AuthProvider";
import { LoginForm, nextPath } from "@/components/LoginForm";

export default function LoginPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.replace(nextPath());
    }
  }, [loading, user, router]);

  if (loading || user) return null;

  return (
    <div className="flex flex-col items-center py-16">
      <Image
        src="/logo-mark.png"
        alt=""
        width={64}
        height={64}
        className="mb-4 h-16 w-16 object-contain mix-blend-multiply"
        priority
      />
      <h1 className="mb-1 font-serif text-3xl font-semibold tracking-tight text-slate-900">Atlas</h1>
      <p className="mb-1 text-sm font-medium text-brand-700">Stocks, plainly explained.</p>
      <p className="mb-8 text-sm text-slate-600">Sign in to generate and personalize explanations.</p>
      <LoginForm />
    </div>
  );
}
