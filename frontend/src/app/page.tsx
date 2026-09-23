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
  CircuitBoard,
  Cpu,
  Binary,
  Zap,
} from "lucide-react";

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
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 h-[32rem] w-[60rem] rounded-full bg-pa-blue/10 blur-[120px]" />
        <div className="absolute top-1/3 -left-40 h-96 w-96 rounded-full bg-pa-violet/10 blur-[100px]" />
        <div className="absolute bottom-0 -right-40 h-96 w-96 rounded-full bg-pa-mint/10 blur-[100px]" />
        <div className="absolute inset-x-0 top-0 h-[36rem] bg-grid-fade" />
      </div>

      {/* Hero */}
      <section className="relative max-w-3xl mx-auto text-center pt-10 sm:pt-16 pb-14 px-2 overflow-hidden">
        {/* Floating technical doodles -- sparse, low-opacity, hidden on small screens */}
        <div className="hidden sm:block pointer-events-none absolute inset-0 -z-10" aria-hidden="true">
          <CircuitBoard
            className="absolute top-4 left-2 w-7 h-7 text-pa-blue/25 animate-float-slow"
            style={{ animationDelay: "0s", ["--float-rot" as any]: "-8deg" }}
          />
          <span
            className="font-technical absolute top-20 -left-2 text-[10px] text-pa-violet/40 border border-pa-violet/20 rounded px-1.5 py-0.5 animate-float-slow"
            style={{ animationDelay: "0.8s", ["--float-rot" as any]: "3deg" }}
          >
            R=10kΩ
          </span>
          <Binary
            className="absolute bottom-8 left-10 w-5 h-5 text-pa-mint/30 animate-float-slow"
            style={{ animationDelay: "1.6s" }}
          />
          <Cpu
            className="absolute top-6 right-2 w-6 h-6 text-pa-violet/25 animate-float-slow"
            style={{ animationDelay: "0.4s", ["--float-rot" as any]: "6deg" }}
          />
          <span
            className="font-technical absolute top-24 right-0 text-[10px] text-pa-blue/40 border border-pa-blue/20 rounded px-1.5 py-0.5 animate-float-slow"
            style={{ animationDelay: "1.2s", ["--float-rot" as any]: "-3deg" }}
          >
            3.3V
          </span>
          <Zap
            className="absolute bottom-10 right-8 w-5 h-5 text-pa-yellow/40 animate-float-slow"
            style={{ animationDelay: "2s" }}
          />
          <div className="absolute top-1/2 left-6 w-10 border-t border-dashed border-pa-blue/20" />
          <div className="absolute top-1/3 right-10 w-8 border-t border-dashed border-pa-violet/20 rotate-45" />
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-100 border border-border text-[11px] font-technical font-semibold tracking-wide uppercase text-muted-foreground mb-6 animate-fade-up">
          <Sparkles className="w-3.5 h-3.5 text-pa-violet" />
          AI-powered electronics discovery
        </div>

        <h1 className="font-heading text-4xl sm:text-6xl font-extrabold tracking-tight text-foreground leading-[1.08] animate-fade-up [animation-delay:60ms]">
          Find the Right Tech.
          <br />
          <span className="bg-gradient-to-r from-pa-blue via-pa-violet to-pa-blue bg-clip-text text-transparent">
            Without the Noise.
          </span>
        </h1>

        <p className="mt-5 text-base sm:text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed animate-fade-up [animation-delay:120ms]">
          Search products naturally, compare real specifications, understand reviews, and discover
          electronics beyond a fixed catalog.
        </p>

        {/* Search bar -- the visual centerpiece, wired to the real search pipeline */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            runSearch(heroQuery);
          }}
          className="mt-8 max-w-xl mx-auto animate-fade-up [animation-delay:180ms]"
        >
          <div className="search-glow rounded-2xl p-2 flex items-center gap-2 bg-card border-2 border-pa-blue/25 shadow-sm">
            <Search className="w-5 h-5 text-pa-blue ml-2 shrink-0" />
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
              className="px-5 py-2.5 rounded-xl bg-pa-blue hover:brightness-110 active:scale-[0.97] text-white text-sm font-semibold flex items-center gap-1.5 transition-all shrink-0 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
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
        <div className="mt-4 flex flex-wrap items-center justify-center gap-2 animate-fade-up [animation-delay:220ms]">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => runSearch(s)}
              disabled={isSubmitting}
              className="px-3.5 py-1.5 rounded-full text-xs font-medium bg-surface-100 hover:bg-pa-blue/10 hover:text-pa-blue hover:-translate-y-0.5 active:translate-y-0 text-foreground border border-border hover:border-pa-blue/30 transition-all cursor-pointer disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>

        <div className="mt-5 flex items-center justify-center gap-3 animate-fade-up [animation-delay:260ms]">
          <Link
            href="/advisor?mode=chat"
            className="group inline-flex items-center gap-1.5 text-xs font-semibold text-pa-violet hover:text-pa-violet/80 transition-colors cursor-pointer"
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
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
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
              className="tilt-card relative rounded-2xl border border-border bg-card p-5 shadow-sm hover:border-blue-500/30 group animate-rise-in"
              style={{ animationDelay: `${Math.min(idx, 6) * 70}ms` }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center group-hover:bg-blue-500/15 transition-colors">
                  <step.icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <span className="text-[11px] font-bold text-muted-foreground/60 tabular-nums">
                  {String(idx + 1).padStart(2, "0")}
                </span>
              </div>
              <h3 className="text-sm font-bold text-foreground mb-1.5">{step.title}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Agent orchestration + guardrails */}
      <section className="max-w-6xl mx-auto px-2 pb-16 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center mb-4">
            <Workflow className="w-5 h-5 text-violet-600 dark:text-violet-400" />
          </div>
          <h3 className="text-base font-bold text-foreground mb-2">An agent loop, not a fixed pipeline</h3>
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
                <Check className="w-3.5 h-3.5 text-pa-violet shrink-0 mt-0.5" />
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-pa-mint/10 flex items-center justify-center mb-4">
            <ShieldCheck className="w-5 h-5 text-pa-mint" />
          </div>
          <h3 className="text-base font-bold text-foreground mb-2">Guardrails, not vibes</h3>
          <p className="text-xs text-muted-foreground leading-relaxed mb-4">
            Untrusted catalogue and review text can't hijack the agent's behaviour, and the system
            would rather abstain than invent an answer.
          </p>
          <ul className="space-y-2">
            {GUARDRAILS.map((line) => (
              <li key={line} className="flex items-start gap-2 text-xs text-foreground/90">
                <Check className="w-3.5 h-3.5 text-pa-mint shrink-0 mt-0.5" />
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Evidence card mock */}
      <section className="max-w-5xl mx-auto px-2 pb-20">
        <div className="text-center mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
            Every recommendation, cited.
          </h2>
          <p className="text-sm text-muted-foreground mt-2 max-w-xl mx-auto">
            Spec lines, quoted reviews with rating and date, and image-based observations — not just
            a star rating.
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card shadow-md overflow-hidden">
          <div className="p-5 sm:p-6 grid grid-cols-1 md:grid-cols-[auto_1fr] gap-5">
            <div className="w-full md:w-40 h-40 rounded-xl bg-surface-100 border border-border overflow-hidden shrink-0 mx-auto md:mx-0">
              <img
                src="https://m.media-amazon.com/images/I/81x+1vl1kCL._SX679_.jpg"
                alt="Gaming laptop example"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <h4 className="text-sm font-bold text-foreground">Example: "gaming laptop under ₹70,000"</h4>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-pa-mint/10 text-pa-mint font-semibold border border-pa-mint/20">
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
                      <Star key={i} className={`w-3 h-3 ${i < 5 ? "fill-pa-yellow text-pa-yellow" : "text-border"}`} />
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
                      <Star key={i} className={`w-3 h-3 ${i < 3 ? "fill-pa-yellow text-pa-yellow" : "text-border"}`} />
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

      {/* Final CTA */}
      <section className="max-w-3xl mx-auto px-2 pb-20 text-center">
        <div className="rounded-2xl border border-border bg-gradient-to-br from-pa-blue to-pa-violet p-8 sm:p-10 shadow-xl">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Ask it what to buy.
          </h2>
          <p className="text-sm text-white/80 mt-2 max-w-md mx-auto">
            Open the interactive chat and describe what you need — budget, use-case, dealbreakers.
          </p>
          <Link
            href="/advisor?mode=chat"
            className="group inline-flex items-center gap-2 mt-6 px-6 py-3 rounded-xl bg-white hover:bg-blue-50 text-pa-blue text-sm font-bold shadow-lg transition-all cursor-pointer"
          >
            <span>Try now</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
