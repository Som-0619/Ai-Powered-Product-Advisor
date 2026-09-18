"use client";

import React, { useEffect, useState } from "react";

export const CustomCursor: React.FC = () => {
  const [position, setPosition] = useState({ x: -100, y: -100 });
  const [isHovered, setIsHovered] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    // Detect touch device
    if (window.matchMedia("(pointer: coarse)").matches || "ontouchstart" in window) {
      setIsTouchDevice(true);
      return;
    }

    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
      if (!isVisible) setIsVisible(true);

      // Check if hovering interactive element
      const target = e.target as HTMLElement | null;
      if (target) {
        const interactive = target.closest("button, a, input, [role='button'], .glass-card, .glass-panel, [data-interactive]");
        setIsHovered(!!interactive);
      }
    };

    const handleMouseLeave = () => {
      setIsVisible(false);
    };

    const handleMouseEnter = () => {
      setIsVisible(true);
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    document.body.addEventListener("mouseleave", handleMouseLeave);
    document.body.addEventListener("mouseenter", handleMouseEnter);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      document.body.removeEventListener("mouseleave", handleMouseLeave);
      document.body.removeEventListener("mouseenter", handleMouseEnter);
    };
  }, [isVisible]);

  if (isTouchDevice || !isVisible) return null;

  return (
    <>
      {/* Small Precision Dot */}
      <div
        className="fixed top-0 left-0 pointer-events-none z-[9999] rounded-full transition-transform duration-75 ease-out"
        style={{
          transform: `translate3d(${position.x}px, ${position.y}px, 0) translate(-50%, -50%)`,
          width: isHovered ? "8px" : "6px",
          height: isHovered ? "8px" : "6px",
          backgroundColor: isHovered ? "rgb(59, 130, 246)" : "currentColor",
        }}
      />

      {/* Ambient Smooth Follower Ring / Glow */}
      <div
        className={`fixed top-0 left-0 pointer-events-none z-[9998] rounded-full transition-all duration-300 ease-out ${
          isHovered
            ? "w-12 h-12 bg-blue-500/15 border border-blue-500/30 scale-125"
            : "w-8 h-8 border border-slate-400/20 dark:border-white/20 scale-100"
        }`}
        style={{
          transform: `translate3d(${position.x}px, ${position.y}px, 0) translate(-50%, -50%)`,
          boxShadow: isHovered ? "0 0 20px rgba(59, 130, 246, 0.25)" : "none",
        }}
      />
    </>
  );
};
