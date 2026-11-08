"use client";

import Link from "next/link";
import { useRef, useState, type FormEvent, type KeyboardEvent } from "react";

import { useAuth } from "@/components/AuthProvider";
import { Button } from "@/components/Button";
import { ApiError, askQuestion } from "@/lib/api";
import type { ChatTurn, Citation } from "@/lib/types";

const STARTERS = [
  "Why did revenue change?",
  "What did management expect next quarter?",
  "What worried analysts most?",
];
const MAX_LENGTH = 500;
const HISTORY_LIMIT = 6;

type Message = ChatTurn & { citations?: Citation[] };
type AskError = { status: number; message: string; question: string };

function errorText(err: ApiError): string {
  if (err.status === 401) return "Your sign-in has expired.";
  if (err.status === 429) return "You've asked a lot of questions. Try again in a minute.";
  if (err.status === 502) return "We couldn't write an answer this time. Please try again.";
  return err.message || "Something went wrong. Please try again.";
}

const headingClass = "font-serif text-2xl font-semibold tracking-tight text-slate-900";

export function AskPanel({ ticker }: { ticker: string }) {
  const { session, user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<AskError | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  // `pending` is stale inside one render; the ref stops a double Enter from sending twice.
  const sendingRef = useRef(false);

  async function send(raw: string) {
    const question = raw.trim();
    // Read the token now so a refreshed session is used.
    const token = session?.access_token;
    if (sendingRef.current || !question || !token) return;

    sendingRef.current = true;
    setPending(question);
    setError(null);
    setDraft("");
    const history = messages.slice(-HISTORY_LIMIT).map(({ role, content }) => ({ role, content }));
    try {
      const res = await askQuestion(ticker, { question, history }, token);
      // Both turns land together so a failed request never leaves half a turn in history.
      setMessages((prev) => [
        ...prev,
        { role: "user", content: question },
        { role: "assistant", content: res.answer, citations: res.citations },
      ]);
    } catch (err) {
      const apiErr = err instanceof ApiError ? err : new ApiError(500, "");
      setError({ status: apiErr.status, message: errorText(apiErr), question });
      setDraft(question);
    } finally {
      sendingRef.current = false;
      setPending(null);
      inputRef.current?.focus();
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    send(draft);
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      send(draft);
    }
  }

  if (!user) {
    return (
      <section id="ask" className="scroll-mt-28 border-t border-slate-200 pt-6">
        <h2 className={headingClass}>Ask about this call</h2>
        <p className="mt-3 text-sm text-slate-600">
          <Link href={`/login?next=/tickers/${ticker}`} className="font-medium text-brand-700 underline">
            Sign in
          </Link>{" "}
          to ask your own questions about this earnings call.
        </p>
      </section>
    );
  }

  return (
    <section id="ask" className="scroll-mt-28 border-t border-slate-200 pt-6">
      <h2 className={headingClass}>Ask about this call</h2>
      <p className="mt-2 text-sm text-slate-600">Ask anything about what was said, in your own words.</p>

      <ul aria-live="polite" className="mt-4 space-y-4">
        {messages.map((m, i) =>
          m.role === "user" ? (
            <li key={i} className="ml-auto max-w-[85%] rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-slate-900">
              <span className="sr-only">You: </span>
              <span className="whitespace-pre-line break-words">{m.content}</span>
            </li>
          ) : (
            <li key={i} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
              <p className="whitespace-pre-line break-words font-serif text-[1.0625rem] leading-8 text-slate-700">
                <span className="sr-only">Atlas: </span>
                {m.content}
              </p>
              {m.citations && m.citations.length > 0 && (
                <ul className="mt-3 divide-y divide-slate-200 border-y border-slate-200">
                  {m.citations.map((c, j) => (
                    <li key={j} className="py-3 text-sm">
                      <p className="text-slate-700">{c.claim}</p>
                      {c.quote && (
                        <p className="mt-1 break-words font-serif italic text-slate-600">&ldquo;{c.quote}&rdquo;</p>
                      )}
                      <p className="mt-1 text-slate-500">
                        <span className="font-medium text-slate-900">{c.speaker}</span>
                        {", "}
                        {c.section === "qa" ? "Q&A" : "prepared remarks"}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ),
        )}
      </ul>

      {pending && (
        <div className="mt-4 space-y-2">
          <p className="ml-auto max-w-[85%] whitespace-pre-line break-words rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-slate-900">
            <span className="sr-only">You: </span>
            {pending}
          </p>
          <p role="status" className="text-sm text-slate-600">
            Thinking...
          </p>
        </div>
      )}

      {error && (
        <div role="alert" className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-slate-700">
            <span className="font-medium">Your question:</span> <span className="break-words">{error.question}</span>
          </p>
          <p className="mt-1 text-sm text-red-700">{error.message}</p>
          {error.status === 401 ? (
            <p className="mt-2 text-sm text-red-700">
              <Link href={`/login?next=/tickers/${ticker}`} className="font-medium underline">
                Sign in again
              </Link>{" "}
              and we&apos;ll bring you back here.
            </p>
          ) : (
            error.status !== 404 &&
            error.status !== 429 && (
              <Button className="mt-3" onClick={() => send(error.question)}>
                Retry
              </Button>
            )
          )}
        </div>
      )}

      {messages.length === 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {STARTERS.map((q) => (
            <Button key={q} variant="secondary" disabled={!!pending} onClick={() => send(q)}>
              {q}
            </Button>
          ))}
        </div>
      )}

      <form onSubmit={onSubmit} className="mt-4">
        <label htmlFor="ask-input" className="block text-sm font-medium text-slate-900">
          Your question
        </label>
        <textarea
          id="ask-input"
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          maxLength={MAX_LENGTH}
          rows={3}
          aria-describedby="ask-hint"
          className="mt-1.5 block w-full resize-y rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        />
        <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
          <p id="ask-hint" className="text-sm text-slate-500">
            Press Enter to send, Shift+Enter for a new line.
            {draft.length >= 450 && ` ${MAX_LENGTH - draft.length} characters left.`}
          </p>
          <Button type="submit" disabled={!draft.trim() || !!pending}>
            {pending ? "Sending..." : "Ask"}
          </Button>
        </div>
      </form>

      <div className="mt-4 rounded-xl border border-moderate-100 bg-moderate-50 px-4 py-3">
        <p className="text-sm leading-relaxed text-slate-800">
          Answers come only from this earnings call and aren&apos;t financial advice.
        </p>
      </div>
    </section>
  );
}
