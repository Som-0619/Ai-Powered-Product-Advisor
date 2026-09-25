"use client";

import React from "react";
import {
  Brain,
  Search,
  MessageSquare,
  Cpu,
  ShieldCheck,
  Eye,
  Sliders,
  FileCheck2,
  CheckCircle2,
  Clock,
  AlertCircle,
  SkipForward,
  Loader2,
} from "lucide-react";
import { TraceStep } from "../services/api";

interface AgentTracePanelProps {
  trace: TraceStep[];
  activeStep?: string;
  totalLatencyMs?: number;
}

const ORDERED_NODES: Array<{ id: string; label: string; icon: React.ReactNode; desc: string }> = [
  { id: "Query Understanding", label: "Query Understanding", icon: <Brain className="w-4 h-4" />, desc: "Intent, constraints & language" },
  { id: "Retrieval", label: "Retrieval", icon: <Search className="w-4 h-4" />, desc: "OpenSearch hybrid search" },
  { id: "Review", label: "Review", icon: <MessageSquare className="w-4 h-4" />, desc: "Sentiment & fraud detection" },
  { id: "Parts", label: "Parts", icon: <Cpu className="w-4 h-4" />, desc: "Electrical spec extraction" },
  { id: "Compatibility", label: "Compatibility", icon: <ShieldCheck className="w-4 h-4" />, desc: "Deterministic voltage & logic checks" },
  { id: "Vision", label: "Vision", icon: <Eye className="w-4 h-4" />, desc: "Multimodal connector & port audit" },
  { id: "Ranking", label: "Ranking", icon: <Sliders className="w-4 h-4" />, desc: "Deterministic mathematical scoring" },
  { id: "Evidence", label: "Evidence", icon: <FileCheck2 className="w-4 h-4" />, desc: "Grounded claim mapping" },
  { id: "Verification", label: "Verification", icon: <CheckCircle2 className="w-4 h-4" />, desc: "Critic audit & contradiction checks" },
];

export const AgentTracePanel: React.FC<AgentTracePanelProps> = ({
  trace,
  activeStep,
  totalLatencyMs,
}) => {
  const traceMap = new Map<string, TraceStep>();
  trace.forEach((step) => {
    traceMap.set(step.node, step);
  });

  return (
    <div className="bg-surface-50 border border-border rounded-2xl p-5 shadow-sm transition-colors duration-200">
      <div className="flex items-center justify-between border-b border-border pb-4 mb-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center text-accent">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground tracking-tight">Multi-Agent Supervisor Trace</h3>
            <p className="text-xs text-muted-foreground">Real-time LangGraph node progression & telemetry</p>
          </div>
        </div>

        {totalLatencyMs !== undefined && (
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-surface-100 border border-border text-xs text-muted-foreground">
            <Clock className="w-3.5 h-3.5 text-accent" />
            <span>Total: {totalLatencyMs.toFixed(0)} ms</span>
          </div>
        )}
      </div>

      {/* Grid of Agent Nodes */}
      <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-9 gap-2">
        {ORDERED_NODES.map((node) => {
          const step = traceMap.get(node.id);
          const isActive = activeStep === node.id;
          const isCompleted = step?.status === "completed";
          const isSkipped = step?.status === "skipped";
          const isFailed = step?.status === "failed";

          let borderStyle = "border-border bg-surface-100/40 text-muted-foreground";
          let badge = null;

          if (isActive) {
            borderStyle = "border-accent bg-accent/10 text-accent shadow-sm animate-pulse";
            badge = <Loader2 className="w-3 h-3 animate-spin text-accent" />;
          } else if (isCompleted) {
            borderStyle = "border-emerald-500/30 bg-emerald-500/5 text-foreground";
            badge = <CheckCircle2 className="w-3 h-3 text-emerald-500" />;
          } else if (isSkipped) {
            borderStyle = "border-border bg-surface-100/30 text-muted-foreground";
            badge = <SkipForward className="w-3 h-3 text-muted-foreground" />;
          } else if (isFailed) {
            borderStyle = "border-rose-500/30 bg-rose-500/10 text-rose-500";
            badge = <AlertCircle className="w-3 h-3 text-rose-500" />;
          }

          return (
            <div
              key={node.id}
              className={`p-2.5 rounded-xl border flex flex-col justify-between transition-all ${borderStyle}`}
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="p-1 rounded-md bg-surface-100">{node.icon}</span>
                  {badge}
                </div>
                <h4 className="text-[11px] font-bold tracking-tight line-clamp-1">{node.label}</h4>
              </div>

              <div className="mt-2 pt-1 border-t border-border flex items-center justify-between text-[10px]">
                {step ? (
                  <>
                    <span className="capitalize opacity-80">{step.status}</span>
                    <span className="font-mono font-semibold">{step.latency_ms}ms</span>
                  </>
                ) : (
                  <span className="opacity-50">Pending</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
