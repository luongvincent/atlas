"use client";

import { Fragment, useMemo, useState } from "react";

import type { GlossaryEntry } from "@/lib/types";

// Words that signal a prediction rather than a promise. Underline as well as
// tint so the meaning doesn't rely on color alone.
const HEDGE_WORDS = /\b(expect(?:s|ed|ing)?|anticipate[sd]?|believe[sd]?|hope[sd]?|may|might|could|approximately|roughly)\b/i;

function highlightHedges(text: string) {
  // split() with a capture group puts the matched words at odd indexes.
  return text.split(new RegExp(HEDGE_WORDS.source, "gi")).map((part, i) =>
    i % 2 === 1 ? (
      <mark key={i} className="rounded-sm bg-moderate-100 px-0.5 text-slate-900 underline decoration-moderate-600 decoration-dotted underline-offset-4">
        {part}
      </mark>
    ) : (
      part
    ),
  );
}

const escapeRegex = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/**
 * For each paragraph, the definitions whose term first appears there, so a
 * term is underlined once per page instead of once per paragraph.
 */
export function assignDefinitions(paragraphs: string[], definitions: GlossaryEntry[]): GlossaryEntry[][] {
  const result: GlossaryEntry[][] = paragraphs.map(() => []);
  for (const def of definitions) {
    const pattern = new RegExp(`\\b${escapeRegex(def.term)}\\b`, "i");
    const first = paragraphs.findIndex((p) => pattern.test(p));
    if (first >= 0) result[first].push(def);
  }
  return result;
}

/**
 * One paragraph of explanation text. Jargon from `definitions` is underlined
 * (first mention only, to keep the page calm); tapping a term shows its
 * definition under the paragraph. With `hedged`, prediction words like
 * "expect" are highlighted too.
 */
export function RichText({
  text,
  definitions,
  hedged = false,
  className,
}: {
  text: string;
  definitions: GlossaryEntry[];
  hedged?: boolean;
  className?: string;
}) {
  const [open, setOpen] = useState<string | null>(null);

  const byTerm = useMemo(() => new Map(definitions.map((d) => [d.term.toLowerCase(), d.definition])), [definitions]);
  const termRegex = useMemo(() => {
    if (byTerm.size === 0) return null;
    // Longest first so "earnings per share" wins over a shorter overlapping term.
    const terms = [...byTerm.keys()].sort((a, b) => b.length - a.length).map(escapeRegex);
    return new RegExp(`\\b(${terms.join("|")})\\b`, "gi");
  }, [byTerm]);

  const seen = new Set<string>();
  const parts = termRegex ? text.split(termRegex) : [text];

  return (
    <p className={className}>
      {parts.map((part, i) => {
        const key = part.toLowerCase();
        if (i % 2 === 1 && !seen.has(key)) {
          seen.add(key);
          return (
            <button
              key={i}
              type="button"
              aria-expanded={open === key}
              onClick={() => setOpen(open === key ? null : key)}
              className="rounded-sm underline decoration-brand-500 decoration-dotted underline-offset-4 transition-colors hover:text-brand-700"
            >
              {part}
            </button>
          );
        }
        return <Fragment key={i}>{hedged ? highlightHedges(part) : part}</Fragment>;
      })}
      {open && byTerm.get(open) && (
        <span role="note" className="mt-3 block rounded-lg bg-brand-50 px-3 py-2 font-sans text-sm leading-relaxed text-brand-900">
          <span className="font-semibold capitalize">{open}</span> means {byTerm.get(open)}
        </span>
      )}
    </p>
  );
}
