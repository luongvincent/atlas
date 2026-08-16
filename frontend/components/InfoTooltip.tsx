// A visible, tap/click-friendly info affordance - deliberately not a bare
// `title` attribute, which is invisible until a user happens to hover the
// exact right spot and doesn't work on touch at all. Built on <details> so
// it's keyboard/screen-reader accessible and works on mobile with zero
// extra JS state.
//
// The popover anchors to the nearest `position: relative` ANCESTOR, not to
// this icon itself - callers must wrap their whole card/row in `relative`.
// That's deliberate: anchoring to the icon made the popover open directly
// on top of the number it's explaining, which defeats the point of showing
// both at once. Anchoring to the card instead opens it below everything,
// so the value stays fully visible while reading the explanation.
export function InfoTooltip({ text }: { text: string }) {
  return (
    <details className="group/tip inline-block align-middle">
      <summary
        className="flex h-4 w-4 cursor-pointer list-none items-center justify-center rounded-full bg-slate-200 text-[10px] font-bold leading-none text-slate-600 marker:hidden hover:bg-slate-300 group-open/tip:bg-brand-100 group-open/tip:text-brand-700 [&::-webkit-details-marker]:hidden"
        aria-label="What does this mean?"
      >
        i
      </summary>
      <div className="absolute left-1/2 top-full z-20 mt-2 w-60 max-w-[85vw] -translate-x-1/2 rounded-lg border border-slate-200 bg-white p-3 text-xs font-normal leading-relaxed text-slate-600 shadow-card-hover">
        {text}
      </div>
    </details>
  );
}
