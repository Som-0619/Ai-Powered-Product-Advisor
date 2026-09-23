"use client";

import React from "react";
import { X, FileText, CheckCircle2, AlertTriangle, ExternalLink, ShieldCheck, Scale } from "lucide-react";
import { RecommendationItem, VerificationResult } from "../services/api";

interface EvidencePanelProps {
  item: RecommendationItem | null;
  globalVerification?: VerificationResult;
  onClose: () => void;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  item,
  globalVerification,
  onClose,
}) => {
  if (!item) return null;

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
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">Traceable Evidence & Critic Audit</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">{item.product_name}</p>
          </div>
        </div>

        {/* Verification Critic Audit Box */}
        {globalVerification && (
          <div className="mb-6 p-4 rounded-xl bg-surface-100/70 border border-slate-200/80 dark:border-white/5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                <span className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                  Critic Verification Findings
                </span>
              </div>
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-bold border ${
                  globalVerification.passed
                    ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                    : "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20"
                }`}
              >
                {globalVerification.passed ? "Audit Passed" : "Audit Review Required"}
              </span>
            </div>

            {/* Coverage Meter */}
            <div className="mb-4">
              <div className="flex justify-between text-xs mb-1 font-semibold">
                <span className="text-slate-600 dark:text-slate-400">Evidence Grounding Coverage</span>
                <span className="text-slate-900 dark:text-white">
                  {Math.round(globalVerification.evidence_coverage_score * 100)}%
                </span>
              </div>
              <div className="w-full h-2 bg-surface-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.round(globalVerification.evidence_coverage_score * 100)}%` }}
                />
              </div>
            </div>

            {/* Findings List */}
            {globalVerification.findings && globalVerification.findings.length > 0 && (
              <div className="space-y-2">
                {globalVerification.findings.map((f, i) => {
                  const isSuccess = f.status === "verified" || f.status === "passed";
                  const formattedCheck = f.check.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
                  return (
                    <div key={i} className="flex items-start space-x-2 text-xs bg-surface-50 p-2.5 rounded-lg border border-slate-200/60 dark:border-white/5">
                      {isSuccess ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                      )}
                      <div>
                        <span className="font-semibold text-slate-900 dark:text-white block">{formattedCheck}</span>
                        <p className="text-slate-600 dark:text-slate-300 mt-0.5">{f.reasoning}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Mapped Claims & Citations */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            <Scale className="w-4 h-4 text-emerald-500" />
            <span>Mapped Technical Claims</span>
          </div>

          {item.evidence && item.evidence.length > 0 ? (
            item.evidence.map((ev, idx) => (
              <div
                key={idx}
                className="bg-surface-100/50 p-4 rounded-xl border border-slate-200/80 dark:border-white/5 space-y-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center space-x-1.5 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Claim #{idx + 1}</span>
                  </div>
                  {ev.confidence !== undefined && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20 font-bold">
                      {Math.round(ev.confidence * 100)}% Confidence
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-900 dark:text-white font-medium">{ev.claim}</p>

                {ev.evidence_text && (
                  <div className="bg-surface-50 p-2.5 rounded-lg border border-slate-200/60 dark:border-white/5">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold block mb-0.5">
                      Grounded Citation
                    </span>
                    <p className="text-xs text-slate-700 dark:text-slate-300 italic">"{ev.evidence_text}"</p>
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500 italic">No specific claims mapped for this product.</p>
          )}
        </div>
      </div>
    </div>
  );
};
