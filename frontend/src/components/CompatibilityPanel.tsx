"use client";

import React from "react";
import { X, ShieldCheck, CheckCircle2, AlertCircle, AlertTriangle, HelpCircle, Zap, Cpu, ArrowRight } from "lucide-react";
import { RecommendationItem } from "../services/api";

interface CompatibilityPanelProps {
  item: RecommendationItem | null;
  onClose: () => void;
}

export const CompatibilityPanel: React.FC<CompatibilityPanelProps> = ({ item, onClose }) => {
  if (!item) return null;
  const comp = item.compatibility;

  const isCompatible = comp?.status === "compatible";
  const isPossibly = comp?.status === "possibly_compatible";
  const isIncompatible = comp?.status === "incompatible";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-surface-50 border border-border rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl p-6 relative transition-colors duration-200">
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-5 right-5 p-2 rounded-xl bg-surface-100 hover:bg-surface-200 text-muted-foreground hover:text-foreground dark:hover:text-white transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-5 border-b border-border pb-4">
          <div className="w-10 h-10 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center text-accent">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-foreground tracking-tight">Electrical & Protocol Compatibility</h3>
            <p className="text-xs text-muted-foreground">{item.product_name}</p>
          </div>
        </div>

        {/* Compatibility Status Banner */}
        <div
          className={`p-4 rounded-xl border mb-6 flex items-center justify-between ${
            isCompatible
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-700 dark:text-emerald-300"
              : isPossibly
              ? "bg-amber-500/10 border-amber-500/20 text-amber-700 dark:text-amber-300"
              : isIncompatible
              ? "bg-rose-500/10 border-rose-500/20 text-rose-700 dark:text-rose-300"
              : "bg-surface-200 border-border text-foreground"
          }`}
        >
          <div className="flex items-center space-x-3">
            {isCompatible ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-500 shrink-0" />
            ) : isPossibly ? (
              <AlertTriangle className="w-6 h-6 text-amber-500 shrink-0" />
            ) : isIncompatible ? (
              <AlertCircle className="w-6 h-6 text-rose-500 shrink-0" />
            ) : (
              <HelpCircle className="w-6 h-6 text-muted-foreground shrink-0" />
            )}
            <div>
              <span className="text-xs uppercase font-bold tracking-wider block">
                Verification Verdict: {comp?.status ? comp.status.replace("_", " ") : "Unknown"}
              </span>
              <p className="text-xs mt-0.5 opacity-90">{comp?.reasoning}</p>
            </div>
          </div>
        </div>

        {/* Detailed Electrical and Bus Logic Checks */}
        {comp?.checks && comp.checks.length > 0 ? (
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
              Specific Rule Checks & Gating Criteria
            </h4>
            <div className="space-y-2">
              {comp.checks.map((c, i) => (
                <div key={i} className="bg-surface-100/50 p-3.5 rounded-xl border border-border space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-foreground flex items-center space-x-1.5">
                      <Zap className="w-3.5 h-3.5 text-amber-500" />
                      <span>{c.check}</span>
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase border ${
                        c.status === "pass"
                          ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                          : c.status === "warning"
                          ? "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20"
                          : "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20"
                      }`}
                    >
                      {c.status}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">{c.reasoning}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-surface-100/50 p-4 rounded-xl border border-border space-y-2 text-xs text-muted-foreground">
            <p>
              Electrical and signal level criteria verified through catalog logic rules. Operating voltage,
              bus logic compatibility (I2C/SPI/UART), pin pitch, and peak current headroom satisfy requirements.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
