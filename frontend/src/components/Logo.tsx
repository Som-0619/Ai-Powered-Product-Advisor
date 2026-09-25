import React from "react";

/**
 * Verdict's mark: a checkmark inside a rounded square badge -- the checkmark
 * reads as both "verified" (the product's core value prop: evidence-backed
 * confidence, not a guess) and, stretched wide, echoes the "V" in Verdict.
 * Single-color, uses currentColor so it inherits text-accent-foreground /
 * whatever color is set on it -- no separate logo palette.
 */
export const LogoMark: React.FC<{ className?: string }> = ({ className }) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d="M4.5 12.5L9.5 17.5L19.5 6.5"
      stroke="currentColor"
      strokeWidth="2.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const Logo: React.FC<{ size?: number; className?: string }> = ({ size = 36, className }) => (
  <div
    className={`rounded-lg bg-accent flex items-center justify-center shrink-0 ${className ?? ""}`}
    style={{ width: size, height: size }}
  >
    <LogoMark className="w-[55%] h-[55%] text-accent-foreground" />
  </div>
);
