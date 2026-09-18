"use client";

import React from "react";
import { Cpu, Sun, Moon } from "lucide-react";
import { useTheme } from "./ThemeProvider";

export const Header: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <header className="border-b border-slate-200/80 dark:border-white/5 bg-white/70 dark:bg-background/80 backdrop-blur-md sticky top-0 z-50 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">
                Product Advisor
              </span>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                Phase 14
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
              AI Multimodal Product Intelligence & Recommendation
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Target Architecture Badge */}
          <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-surface-100 border border-slate-200/80 dark:border-white/5 text-xs text-slate-600 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Target: Local / AWS Portable</span>
          </div>

          {/* Dark / Light Mode Segmented Switch */}
          <div
            role="radiogroup"
            aria-label="Color theme selector"
            className="flex items-center p-1 rounded-xl bg-slate-100 dark:bg-surface-100 border border-slate-200/80 dark:border-white/10 shadow-inner"
          >
            <button
              type="button"
              role="radio"
              aria-checked={theme === "light"}
              onClick={() => setTheme("light")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                theme === "light"
                  ? "bg-white text-amber-600 shadow-sm font-bold ring-1 ring-slate-200"
                  : "text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
              title="Light Mode"
            >
              <Sun className={`w-3.5 h-3.5 ${theme === "light" ? "text-amber-500 fill-amber-400/20" : ""}`} />
              <span className="hidden xs:inline sm:inline">Light</span>
            </button>
            <button
              type="button"
              role="radio"
              aria-checked={theme === "dark"}
              onClick={() => setTheme("dark")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                theme === "dark"
                  ? "bg-slate-800 text-blue-400 shadow-sm font-bold border border-white/10 ring-1 ring-white/10"
                  : "text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
              title="Dark Mode"
            >
              <Moon className={`w-3.5 h-3.5 ${theme === "dark" ? "text-blue-400 fill-blue-400/20" : ""}`} />
              <span className="hidden xs:inline sm:inline">Dark</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
