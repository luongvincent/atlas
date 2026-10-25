import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary";
type Size = "sm" | "md";

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: "bg-brand-600 text-white hover:bg-brand-700",
  secondary: "border border-slate-300 text-slate-700 hover:bg-slate-50",
};

const SIZE_CLASSES: Record<Size, string> = {
  sm: "px-3 py-1.5",
  md: "px-4 py-2.5",
};

// Exported separately so a <Link> can look like a button without nesting
// a <button> inside an <a>.
export function buttonClass(variant: Variant = "primary", size: Size = "sm") {
  return `inline-block rounded-lg text-center text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${VARIANT_CLASSES[variant]} ${SIZE_CLASSES[size]}`;
}

export function Button({
  variant,
  size,
  className = "",
  type = "button",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }) {
  return <button type={type} className={`${buttonClass(variant, size)} ${className}`} {...props} />;
}
