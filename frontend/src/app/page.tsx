"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  Sparkles,
  SearchCheck,
  MessagesSquare,
  ShieldCheck,
  ScanEye,
  ListOrdered,
  FileCheck2,
  Workflow,
  Languages,
  Star,
  Check,
  Search,
  Loader2,
} from "lucide-react";
import { Logo } from "../components/Logo";

const SUGGESTIONS = ["Phones under ₹30K", "Gaming laptops", "Wireless earbuds", "Arduino sensors"];

const PIPELINE_STEPS = [
  {
    icon: Languages,
    title: "Understand the request",
    description:
      "Parses plain English or mixed Hindi-English into category, budget, use-case, hard constraints and soft preferences — and asks a clarifying question when it's too vague to act on.",
  },
  {
    icon: SearchCheck,
    title: "Retrieve real candidates",
    description:
      "Hybrid BM25 + vector search over the product catalogue and linked customer reviews, filtered by budget and category before ranking begins.",
  },
  {
    icon: ShieldCheck,
    title: "Read the reviews honestly",
    description:
      "Summarises what customers actually praise and complain about, and flags near-duplicate, bursty or templated reviews as likely fake — with the reason shown.",
  },
  {
    icon: ScanEye,
    title: "Verify with the images",
    description:
      "A vision model checks product photos against spec claims — ports, keypads, bundled accessories — and reports agreement or contradiction.",
  },
  {
    icon: ListOrdered,
    title: "Rank with a documented formula",
    description:
      "Combines retrieval relevance, constraint fit, review sentiment, trustworthiness and visual verification into an explainable ranking, not a black box.",
  },
  {
    icon: FileCheck2,
    title: "Explain every recommendation",
    description:
      "Cites the exact spec lines, quoted reviews and image observations behind each pick, with a confidence level and an honest negative if one exists.",
  },
];

const GUARDRAILS = [
  "Treats catalogue and review text as untrusted data — embedded instructions are never followed",
  "Redacts phone numbers, emails and IDs found in review text before display",
  "Refuses to recommend when nothing in the catalogue meets the hard constraints",
  "Never invents a spec, price or review — every claim traces back to real data or an image",
];

export default function LandingPage() {
  const router = useRouter();
  const [heroQuery, setHeroQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const runSearch = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isSubmitting) return;
    setIsSubmitting(true);
    // Reuses the exact same advisor search pipeline -- the advisor page
    // auto-runs streamRecommendation() for this ?q= on mount, so this is a
    // real search, not a demo/fake result.
    router.push(`/advisor?q=${encodeURIComponent(trimmed)}`);
  };

  return (
    <div className="w-full">
      {/* Hero -- flat on the page background, no panel/box. */}
      <section className="relative max-w-3xl mx-auto mt-8 sm:mt-14 mb-14 px-2 text-center">
        <div className="relative inline-flex items-center gap-2.5 mb-5 animate-fade-up">
          <Logo size={40} />
          <span className="font-heading text-2xl font-semibold tracking-tight text-foreground">
            Verdict
          </span>
        </div>

        <div className="relative flex items-center justify-center gap-1.5 text-[11px] font-technical font-semibold tracking-wide uppercase text-muted-foreground mb-6 animate-fade-up [animation-delay:30ms]">
          <Sparkles className="w-3 h-3 text-accent" />
          AI-powered electronics discovery
        </div>

        <h1 className="relative font-heading text-4xl sm:text-5xl font-semibold tracking-tight leading-[1.1] text-foreground animate-fade-up [animation-delay:60ms]">
          Find the right tech.
          <br />
          Without the noise.
        </h1>

        <p className="relative mt-5 text-base sm:text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed animate-fade-up [animation-delay:120ms]">
          Search products naturally, compare real specifications, understand reviews, and discover
          electronics beyond a fixed catalog.
        </p>

        {/* Search bar -- the visual centerpiece, wired to the real search pipeline */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            runSearch(heroQuery);
          }}
          className="relative mt-8 max-w-xl mx-auto animate-fade-up [animation-delay:180ms]"
        >
          <div className="search-glow rounded-xl p-1.5 flex items-center gap-2 bg-card border border-border">
            <Search className="w-5 h-5 text-muted-foreground ml-2 shrink-0" />
            <input
              type="text"
              value={heroQuery}
              onChange={(e) => setHeroQuery(e.target.value)}
              disabled={isSubmitting}
              placeholder="Try “gaming laptop under 70k” or “ESP32 sensors”..."
              className="flex-1 min-w-0 bg-transparent px-1 py-2.5 text-sm sm:text-base text-foreground placeholder-muted-foreground focus:outline-none disabled:opacity-60"
              autoFocus
            />
            <button
              type="submit"
              disabled={isSubmitting || !heroQuery.trim()}
              className="px-5 py-2.5 rounded-lg bg-accent hover:opacity-90 text-accent-foreground text-sm font-medium flex items-center gap-1.5 transition-all shrink-0 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <span className="hidden sm:inline">Search</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Suggestion chips -- trigger the real search, same as typing + submit */}
        <div className="relative mt-5 flex flex-wrap items-center justify-center gap-2 animate-fade-up [animation-delay:220ms]">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => runSearch(s)}
              disabled={isSubmitting}
              className="px-3.5 py-1.5 rounded-full text-xs font-medium bg-surface-100 hover:bg-surface-200 text-foreground border border-border transition-colors cursor-pointer disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>

        <div className="relative mt-6 flex items-center justify-center gap-3 animate-fade-up [animation-delay:260ms]">
          <Link
            href="/advisor?mode=chat"
            className="group inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          >
            <MessagesSquare className="w-3.5 h-3.5" />
            <span>Or try the interactive chat</span>
            <ArrowRight className="w-3 h-3 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </section>

      {/* Pipeline / How it works */}
      <section className="max-w-6xl mx-auto px-2 pb-16">
        <div className="text-center mb-10">
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-foreground">
            One request, a full evidence trail.
          </h2>
          <p className="text-sm text-muted-foreground mt-2 max-w-xl mx-auto">
            Each step below is a real tool call the agent makes — planned, verified, and recorded in
            a trace you can inspect.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {PIPELINE_STEPS.map((step, idx) => (
            <div
              key={step.title}
              className="tilt-card relative rounded-xl border border-border bg-card p-5 group animate-rise-in"
              style={{ animationDelay: `${Math.min(idx, 6) * 60}ms` }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                  <step.icon className="w-5 h-5 text-accent" />
                </div>
                <span className="text-[11px] font-medium text-muted-foreground/60 tabular-nums">
                  {String(idx + 1).padStart(2, "0")}
                </span>
              </div>
              <h3 className="text-sm font-semibold text-foreground mb-1.5">{step.title}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Agent orchestration + guardrails */}
      <section className="max-w-6xl mx-auto px-2 pb-16 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="tilt-card rounded-xl border border-border bg-card p-6">
          <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
            <Workflow className="w-5 h-5 text-accent" />
          </div>
          <h3 className="text-base font-semibold text-foreground mb-2">An agent loop, not a fixed pipeline</h3>
          <p className="text-xs text-muted-foreground leading-relaxed mb-4">
            The agent plans its steps, calls retrieval, review analysis, image analysis and ranking
            as tools, checks its own intermediate results, and retries or re-plans when something
            looks wrong — an empty retrieval, every candidate over budget, contradictory evidence.
          </p>
          <ul className="space-y-2">
            {[
              "Exposes its plan and every tool call in a live trace",
              "Retries with a bounded number of attempts on failure",
              "Asks a clarifying question and resumes once you answer",
            ].map((line) => (
              <li key={line} className="flex items-start gap-2 text-xs text-foreground/90">
                <Check className="w-3.5 h-3.5 text-accent shrink-0 mt-0.5" />
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="tilt-card rounded-xl border border-border bg-card p-6">
          <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
            <ShieldCheck className="w-5 h-5 text-accent" />
          </div>
          <h3 className="text-base font-semibold text-foreground mb-2">Guardrails, not vibes</h3>
          <p className="text-xs text-muted-foreground leading-relaxed mb-4">
            Untrusted catalogue and review text can't hijack the agent's behaviour, and the system
            would rather abstain than invent an answer.
          </p>
          <ul className="space-y-2">
            {GUARDRAILS.map((line) => (
              <li key={line} className="flex items-start gap-2 text-xs text-foreground/90">
                <Check className="w-3.5 h-3.5 text-accent shrink-0 mt-0.5" />
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Evidence card mock */}
      <section className="max-w-5xl mx-auto px-2 pb-20">
        <div className="text-center mb-8">
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-foreground">
            Every recommendation, cited.
          </h2>
          <p className="text-sm text-muted-foreground mt-2 max-w-xl mx-auto">
            Spec lines, quoted reviews with rating and date, and image-based observations — not just
            a star rating.
          </p>
        </div>

        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="p-5 sm:p-6 grid grid-cols-1 md:grid-cols-[auto_1fr] gap-5">
            <div className="w-full md:w-40 h-40 rounded-lg bg-surface-100 border border-border overflow-hidden shrink-0 mx-auto md:mx-0">
              <img
                src="https://m.media-amazon.com/images/I/81x+1vl1kCL._SX679_.jpg"
                alt="Gaming laptop example"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <h4 className="text-sm font-semibold text-foreground">Example: "gaming laptop under ₹70,000"</h4>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-accent/10 text-accent font-medium border border-accent/20">
                  High confidence
                </span>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Ranked #1 for RTX-class graphics under budget, with video-editing headroom noted from
                the use-case match. Two positive review excerpts and one honest negative are cited below.
              </p>
              <div className="grid sm:grid-cols-2 gap-2 pt-1">
                <div className="rounded-lg bg-surface-100 border border-border p-3">
                  <div className="flex items-center gap-1 mb-1">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className={`w-3 h-3 ${i < 5 ? "fill-accent text-accent" : "text-border"}`} />
                    ))}
                    <span className="text-[10px] text-muted-foreground ml-1">Jan 2026</span>
                  </div>
                  <p className="text-[11px] text-foreground/90 leading-snug">
                    "Runs Premiere Pro exports fast, thermals stay reasonable even after an hour of gaming."
                  </p>
                </div>
                <div className="rounded-lg bg-surface-100 border border-border p-3">
                  <div className="flex items-center gap-1 mb-1">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className={`w-3 h-3 ${i < 3 ? "fill-accent text-accent" : "text-border"}`} />
                    ))}
                    <span className="text-[10px] text-muted-foreground ml-1">Dec 2025</span>
                  </div>
                  <p className="text-[11px] text-foreground/90 leading-snug">
                    "Speakers are weak and the fan gets loud under full load — use headphones."
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA -- flat, no panel/box */}
      <section className="max-w-3xl mx-auto px-2 pb-20 text-center">
        <h2 className="text-2xl sm:text-3xl font-semibold text-foreground tracking-tight">
          Ask it what to buy.
        </h2>
        <p className="text-sm text-muted-foreground mt-2 max-w-md mx-auto">
          Open the interactive chat and describe what you need — budget, use-case, dealbreakers.
        </p>
        <Link
          href="/advisor?mode=chat"
          className="cta-pulse group inline-flex items-center gap-2 mt-6 px-6 py-3 rounded-lg bg-accent text-accent-foreground text-sm font-medium transition-transform hover:scale-[1.03] active:scale-[0.98] cursor-pointer"
        >
          <span>Try now</span>
          <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
        </Link>
      </section>
    </div>
  );
}
