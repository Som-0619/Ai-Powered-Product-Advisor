"use client";

import React from "react";
import Link from "next/link";
import { Cpu, Sun, Moon } from "lucide-react";
import { useTheme } from "./ThemeProvider";

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="border-b border-border/60 bg-card/70 backdrop-blur-md sticky top-0 z-50 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand identity */}
        <Link href="/" className="group flex items-center space-x-3 cursor-pointer">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center shadow-sm transition-transform duration-300 group-hover:-rotate-6 group-hover:scale-105">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-heading font-bold text-base sm:text-lg tracking-tight text-foreground">
                Product Advisor
              </span>
            </div>
            <p className="text-xs text-muted-foreground hidden sm:block">
              Multimodal Product Intelligence & Verification
            </p>
          </div>
        </Link>

        <div className="flex items-center gap-4">
        {/* Minimal Theme Switch */}
        <div className="flex items-center">
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            className="p-2 rounded-xl bg-surface-100 hover:bg-surface-200 border border-border text-foreground transition-all duration-150 cursor-pointer flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4 text-amber-400" aria-hidden="true" />
            ) : (
              <Moon className="w-4 h-4 text-slate-700" aria-hidden="true" />
            )}
          </button>
        </div>
        </div>
      </div>
    </header>
  );
};
