"use client";

import React from "react";
import Link from "next/link";
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
  Quote,
  Star,
  Check,
} from "lucide-react";

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
  return (
    <div className="w-full">
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 h-[32rem] w-[60rem] rounded-full bg-blue-500/10 blur-[120px]" />
        <div className="absolute top-1/3 -left-40 h-96 w-96 rounded-full bg-violet-500/10 blur-[100px]" />
        <div className="absolute bottom-0 -right-40 h-96 w-96 rounded-full bg-emerald-500/10 blur-[100px]" />
      </div>

      {/* Hero */}
      <section className="max-w-5xl mx-auto text-center pt-10 sm:pt-16 pb-14 px-2 animate-fade-up">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-100 border border-border text-[11px] font-semibold text-muted-foreground mb-6">
          <Sparkles className="w-3.5 h-3.5 text-blue-500" />
          Agentic, multimodal product intelligence
        </div>

        <h1 className="text-4xl sm:text-6xl font-bold tracking-tight text-foreground leading-[1.08]">
          Product recommendations
          <br className="hidden sm:block" />
          <span className="bg-gradient-to-r from-blue-600 via-blue-500 to-violet-500 bg-clip-text text-transparent">
            {" "}
            you can actually verify.
          </span>
        </h1>

        <p className="mt-5 text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Tell it what you need in plain English or Hinglish. An autonomous agent plans its steps,
          retrieves real candidates, reads the reviews, checks the product photos against the specs,
          and explains every pick with cited evidence — never a guess.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/advisor?mode=chat"
            className="group inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold shadow-lg shadow-blue-600/25 transition-all cursor-pointer"
          >
            <MessagesSquare className="w-4 h-4" />
            <span>Try the interactive chat</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
          <Link
            href="/advisor"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-card hover:bg-surface-100 text-foreground text-sm font-semibold border border-border transition-all cursor-pointer"
          >
            <SearchCheck className="w-4 h-4 text-blue-500" />
            <span>Browse the advisor</span>
          </Link>
        </div>

        <p className="mt-4 text-xs text-muted-foreground">
          No signup needed — jump straight into a live query.
        </p>
      </section>

      {/* Example query strip */}
      <section className="max-w-3xl mx-auto px-2 pb-16 animate-fade-up [animation-delay:80ms]">
        <div className="rounded-2xl border border-border bg-card shadow-sm p-1.5">
          <div className="rounded-xl bg-surface-100 border border-border px-4 py-3 flex items-center gap-3">
            <Quote className="w-4 h-4 text-blue-500 shrink-0" />
            <p className="text-sm text-foreground font-medium truncate">
              "70k ke andar ek gaming laptop chahiye, RTX graphics ke saath, video editing ke liye bhi theek ho"
            </p>
          </div>
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
              className="relative rounded-2xl border border-border bg-card p-5 shadow-sm hover:border-blue-500/30 hover:shadow-md transition-all group"
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
                <Check className="w-3.5 h-3.5 text-violet-500 shrink-0 mt-0.5" />
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-4">
            <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h3 className="text-base font-bold text-foreground mb-2">Guardrails, not vibes</h3>
          <p className="text-xs text-muted-foreground leading-relaxed mb-4">
            Untrusted catalogue and review text can't hijack the agent's behaviour, and the system
            would rather abstain than invent an answer.
          </p>
          <ul className="space-y-2">
            {GUARDRAILS.map((line) => (
              <li key={line} className="flex items-start gap-2 text-xs text-foreground/90">
                <Check className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
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
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold border border-emerald-500/20">
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
                      <Star key={i} className={`w-3 h-3 ${i < 5 ? "fill-amber-400 text-amber-400" : "text-border"}`} />
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
                      <Star key={i} className={`w-3 h-3 ${i < 3 ? "fill-amber-400 text-amber-400" : "text-border"}`} />
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
        <div className="rounded-2xl border border-border bg-gradient-to-br from-blue-600 to-violet-600 p-8 sm:p-10 shadow-xl">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Ask it what to buy.
          </h2>
          <p className="text-sm text-blue-100 mt-2 max-w-md mx-auto">
            Open the interactive chat and describe what you need — budget, use-case, dealbreakers.
          </p>
          <Link
            href="/advisor?mode=chat"
            className="group inline-flex items-center gap-2 mt-6 px-6 py-3 rounded-xl bg-white hover:bg-blue-50 text-blue-700 text-sm font-bold shadow-lg transition-all cursor-pointer"
          >
            <span>Try now</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
