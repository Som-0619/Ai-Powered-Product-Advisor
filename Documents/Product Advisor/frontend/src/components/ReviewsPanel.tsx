"use client";

import React from "react";
import { X, MessageSquare, ShieldAlert, CheckCircle2, ThumbsUp, ThumbsDown, AlertTriangle, Users } from "lucide-react";
import { RecommendationItem } from "../services/api";

interface ReviewsPanelProps {
  item: RecommendationItem | null;
  onClose: () => void;
}

export const ReviewsPanel: React.FC<ReviewsPanelProps> = ({ item, onClose }) => {
  if (!item) return null;
  const reviews = item.reviews;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-surface-50 border border-slate-200/80 dark:border-white/10 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl p-6 relative transition-colors duration-200">
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-5 right-5 p-2 rounded-xl bg-surface-100 hover:bg-surface-200 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-5 border-b border-slate-200/80 dark:border-white/5 pb-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">Grounded Review Analysis & Trust Audit</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">{item.product_name}</p>
          </div>
        </div>

        {/* Sentiment Overview */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-5">
          <div className="bg-surface-100 p-3 rounded-xl border border-slate-200/80 dark:border-white/5">
            <span className="text-[11px] text-slate-500 dark:text-slate-400 block uppercase font-semibold">Sentiment</span>
            <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400 capitalize">
              {reviews?.sentiment || "Positive"}
            </span>
          </div>
          <div className="bg-surface-100 p-3 rounded-xl border border-slate-200/80 dark:border-white/5">
            <span className="text-[11px] text-slate-500 dark:text-slate-400 block uppercase font-semibold">Fraud Risk</span>
            <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
              {reviews?.suspicious_signals?.length ? "Signals Flagged" : "Low Risk (Clean)"}
            </span>
          </div>
          <div className="bg-surface-100 p-3 rounded-xl border border-slate-200/80 dark:border-white/5 col-span-2 sm:col-span-1">
            <span className="text-[11px] text-slate-500 dark:text-slate-400 block uppercase font-semibold">Signals Analyzed</span>
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {reviews?.suspicious_signals?.length || 0} Anomalies
            </span>
          </div>
        </div>

        {/* Fraud / Suspicious Signals */}
        {reviews?.suspicious_signals && reviews.suspicious_signals.length > 0 ? (
          <div className="mb-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400 mb-3">
              <ShieldAlert className="w-4 h-4" />
              <h4 className="text-xs font-bold uppercase tracking-wider">Detected Suspicious Signals</h4>
            </div>
            <div className="space-y-2">
              {reviews.suspicious_signals.map((sig, i) => (
                <div key={i} className="bg-surface-50 p-3 rounded-xl border border-slate-200/60 dark:border-white/5">
                  <div className="flex items-center justify-between text-xs font-semibold mb-1">
                    <span className="text-slate-900 dark:text-white uppercase tracking-wider">{sig.signal_type}</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">{sig.review_ids.length} affected reviews</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300">{sig.explanation}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center space-x-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <div>
              <h4 className="text-xs font-bold text-emerald-700 dark:text-emerald-300 uppercase tracking-wider">High Integrity Reviews</h4>
              <p className="text-xs text-slate-600 dark:text-slate-300 mt-0.5">
                No statistical bursts, duplicate copy-paste phrasing, or incentivized reviewer anomalies detected.
              </p>
            </div>
          </div>
        )}

        {/* Community Pros and Cons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-surface-100/50 p-4 rounded-xl border border-slate-200/80 dark:border-white/5 space-y-2">
            <div className="flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400 text-xs font-bold uppercase tracking-wider">
              <ThumbsUp className="w-3.5 h-3.5" />
              <span>User Praises</span>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
              {reviews?.pros && reviews.pros.length > 0 ? (
                reviews.pros.map((p, i) => (
                  <li key={i} className="flex items-start space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                    <span>{p}</span>
                  </li>
                ))
              ) : (
                item.pros.map((p, i) => (
                  <li key={i} className="flex items-start space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                    <span>{p}</span>
                  </li>
                ))
              )}
            </ul>
          </div>

          <div className="bg-surface-100/50 p-4 rounded-xl border border-slate-200/80 dark:border-white/5 space-y-2">
            <div className="flex items-center space-x-1.5 text-amber-600 dark:text-amber-400 text-xs font-bold uppercase tracking-wider">
              <ThumbsDown className="w-3.5 h-3.5" />
              <span>Reported Complaints</span>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-400">
              {reviews?.cons && reviews.cons.length > 0 ? (
                reviews.cons.map((c, i) => (
                  <li key={i} className="flex items-start space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                    <span>{c}</span>
                  </li>
                ))
              ) : (
                item.cons.map((c, i) => (
                  <li key={i} className="flex items-start space-x-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                    <span>{c}</span>
                  </li>
                ))
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
