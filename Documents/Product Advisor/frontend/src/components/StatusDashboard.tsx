"use client";

import React, { useEffect, useState } from "react";
import {
  Database,
  Search,
  Zap,
  HardDrive,
  Bot,
  Server,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
} from "lucide-react";
import { fetchReady, ReadyResponse, ServiceStatus } from "../services/api";

const SERVICE_ICONS: Record<string, React.ReactNode> = {
  postgres: <Database className="w-5 h-5 text-blue-500" />,
  opensearch: <Search className="w-5 h-5 text-indigo-500" />,
  redis: <Zap className="w-5 h-5 text-amber-500" />,
  minio: <HardDrive className="w-5 h-5 text-rose-500" />,
  ollama: <Bot className="w-5 h-5 text-emerald-500" />,
};

const SERVICE_TITLES: Record<string, { title: string; desc: string }> = {
  postgres: { title: "PostgreSQL", desc: "Relational source of truth & catalogs" },
  opensearch: { title: "OpenSearch", desc: "BM25 keyword & vector retrieval layer" },
  redis: { title: "Redis", desc: "Query cache & local task queue" },
  minio: { title: "MinIO S3", desc: "Object storage for crawls, images, & datasheets" },
  ollama: { title: "Ollama LLM", desc: "Local runtime for Qwen fast & reasoning models" },
};

export const StatusDashboard: React.FC = () => {
  const [data, setData] = useState<ReadyResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastCheck, setLastCheck] = useState<string>("");

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchReady();
      setData(res);
      setLastCheck(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError(err.message || "Failed to reach backend");
      setLastCheck(new Date().toLocaleTimeString());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status?: string) => {
    if (status === "ok" || status === "ready") {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Operational</span>
        </span>
      );
    }
    if (status === "degraded") {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Degraded</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
        <XCircle className="w-3.5 h-3.5" />
        <span>Offline</span>
      </span>
    );
  };

  return (
    <div className="w-full max-w-5xl mx-auto my-6 transition-colors duration-200">
      {/* Top Banner */}
      <div className="glass-panel rounded-2xl p-6 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <Server className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">System Infrastructure Status</h2>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Real-time connectivity monitoring for Phase 1 containerized architecture
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs text-slate-500 dark:text-slate-400">
              {lastCheck ? `Checked at ${lastCheck}` : "Connecting..."}
            </span>
            <button
              onClick={checkHealth}
              disabled={loading}
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-surface-100 hover:bg-surface-200 border border-slate-200/80 dark:border-white/10 text-xs font-semibold text-slate-900 dark:text-white transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-500" : ""}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-300 text-xs flex items-center space-x-2">
            <XCircle className="w-4 h-4 shrink-0" />
            <span>Backend unreachable: {error}. Ensure FastAPI is running on port 8000.</span>
          </div>
        )}
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Backend Node Card */}
        <div className="glass-card rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                <Server className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              {getStatusBadge(data ? "ok" : "error")}
            </div>
            <h3 className="font-semibold text-slate-900 dark:text-white text-base mt-3">FastAPI Gateway</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Core REST application & LangGraph coordination gateway
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-200/60 dark:border-white/5 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Port 8000</span>
            <span className="font-mono text-slate-700 dark:text-slate-300">v{data?.version || "0.1.0"}</span>
          </div>
        </div>

        {/* Dynamic Service Cards */}
        {Object.entries(SERVICE_TITLES).map(([key, info]) => {
          const service = data?.services?.[key];
          return (
            <div key={key} className="glass-card rounded-xl p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between">
                  <div className="w-10 h-10 rounded-lg bg-surface-100 border border-slate-200/80 dark:border-white/10 flex items-center justify-center">
                    {SERVICE_ICONS[key] || <Server className="w-5 h-5 text-slate-400" />}
                  </div>
                  {getStatusBadge(service?.status)}
                </div>
                <h3 className="font-semibold text-slate-900 dark:text-white text-base mt-3">{info.title}</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{info.desc}</p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-200/60 dark:border-white/5 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>
                  {service?.latency_ms !== undefined ? (
                    <span className="font-mono text-emerald-600 dark:text-emerald-400">{service.latency_ms}ms</span>
                  ) : (
                    "Pending ping"
                  )}
                </span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 truncate max-w-[120px]">
                  {service?.error ? (
                    <span className="text-rose-500" title={service.error}>
                      {service.error.substring(0, 18)}...
                    </span>
                  ) : (
                    "Connected"
                  )}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
