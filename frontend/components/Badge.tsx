import type { ReactNode } from "react";

export type BadgeTone =
  | "neutral"
  | "positive"
  | "warning"
  | "danger"
  | "conservative"
  | "moderate"
  | "aggressive";

const TONE_CLASSES: Record<BadgeTone, string> = {
  neutral: "bg-slate-100 text-slate-600",
  positive: "bg-positive-100 text-positive-700",
  warning: "bg-moderate-100 text-moderate-700",
  danger: "bg-red-100 text-red-700",
  conservative: "bg-conservative-100 text-conservative-700",
  moderate: "bg-moderate-100 text-moderate-700",
  aggressive: "bg-aggressive-100 text-aggressive-700",
};

export function Badge({
  tone = "neutral",
  icon,
  children,
}: {
  tone?: BadgeTone;
  icon?: ReactNode;
  children: ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${TONE_CLASSES[tone]}`}
    >
      {icon}
      {children}
    </span>
  );
}
