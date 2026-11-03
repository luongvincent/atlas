import type { ButtonHTMLAttributes } from "react";

// "light" and "ghost" are for dark panels (the landing hero).
type Variant = "primary" | "secondary" | "light" | "ghost";
type Size = "sm" | "md";

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: "bg-brand-600 text-white shadow-sm hover:bg-brand-700",
  secondary: "border border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50",
  light: "bg-white text-slate-900 shadow-sm hover:bg-slate-100",
  ghost: "border border-white/30 text-white hover:bg-white/10",
};

const SIZE_CLASSES: Record<Size, string> = {
  sm: "px-4 py-1.5",
  md: "px-5 py-2.5",
};

// Exported separately so a <Link> can look like a button without nesting
// a <button> inside an <a>.
export function buttonClass(variant: Variant = "primary", size: Size = "sm") {
  return `inline-block rounded-full text-center text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${VARIANT_CLASSES[variant]} ${SIZE_CLASSES[size]}`;
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
