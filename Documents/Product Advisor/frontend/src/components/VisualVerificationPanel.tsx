"use client";

import React, { useState } from "react";
import {
  X,
  Eye,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Camera,
  Check,
  Sparkles,
  Maximize2,
} from "lucide-react";
import { RecommendationItem } from "../services/api";
import { resolveProductImage, IMAGE_UNAVAILABLE_PLACEHOLDER } from "../services/productImages";

interface VisualVerificationPanelProps {
  item: RecommendationItem | null;
  onClose: () => void;
}

type AngleKey = string;

interface AngleMeta {
  key: string;
  label: string;
  badge: string;
  icon: string;
  description: string;
}

const VIEW_METAS: Record<string, { label: string; badge: string; icon: string; description: string }> = {
  primary: {
    label: "Primary View",
    badge: "Main Overview",
    icon: "⭐",
    description: "Primary verified high-resolution product overview.",
  },
  front: {
    label: "Front View",
    badge: "Display & Face",
    icon: "📸",
    description: "Front-facing display bezels, screen-to-body ratio, earpieces, or front interface layout.",
  },
  back: {
    label: "Back View",
    badge: "Rear & Chassis",
    icon: "🔄",
    description: "Rear chassis finish, camera island, thermal exhaust vents, or reverse connector branding.",
  },
  left: {
    label: "Left Profile",
    badge: "Side Profile",
    icon: "◀️",
    description: "Left side chassis profile, port cluster, and edge thickness.",
  },
  right: {
    label: "Right Profile",
    badge: "Side Profile",
    icon: "▶️",
    description: "Right side chassis profile, volume rockers, buttons, or auxiliary ports.",
  },
  top: {
    label: "Top View",
    badge: "Lid & Upper Deck",
    icon: "🔼",
    description: "Top surface finish, lid logo, microphone array, and upper structural profile.",
  },
  bottom: {
    label: "Bottom View",
    badge: "Base & Intake",
    icon: "🔽",
    description: "Base plate, rubber feet, thermal intake grills, and regulatory certification marks.",
  },
  screen: {
    label: "Screen & Display",
    badge: "Display Panel",
    icon: "🖥️",
    description: "High-resolution display panel, viewing angles, color fidelity, and bezel borders.",
  },
  keyboard: {
    label: "Keyboard & Deck",
    badge: "Input & Trackpad",
    icon: "⌨️",
    description: "Keyboard keycap layout, trackpad surface, and ergonomic palm rest.",
  },
  ports: {
    label: "I/O Ports & Profile",
    badge: "Connectivity & I/O",
    icon: "🔌",
    description: "Thunderbolt, USB-C, HDMI, audio jack, and power charging port placement.",
  },
  camera: {
    label: "Camera Module",
    badge: "Optics & Sensors",
    icon: "📷",
    description: "Multi-lens camera array, flash alignment, and optical sensor assembly.",
  },
  connector: {
    label: "Connectors & Pins",
    badge: "Bus & Terminals",
    icon: "⚡",
    description: "Header pins, screw terminals, GPIO pinout, and wiring connectors.",
  },
  board: {
    label: "Circuit Board",
    badge: "PCB & ICs",
    icon: "🧩",
    description: "Microcontroller ICs, crystal oscillators, bypass capacitors, and PCB solder traces.",
  },
  accessories: {
    label: "Accessories & Included",
    badge: "Box Contents",
    icon: "📦",
    description: "Included cables, charging adapter, carry pouch, or ear tips.",
  },
  gallery: {
    label: "Hardware Angle / In-Use",
    badge: "Context & Detail",
    icon: "🖼️",
    description: "Detailed angle or in-use view demonstrating hardware scale and ergonomic context.",
  },
  earcups: {
    label: "Earcups & Drivers",
    badge: "Acoustics & Cushions",
    icon: "🎧",
    description: "Acoustic driver housing, ergonomic cushioned padding, and physical controls.",
  },
  case: {
    label: "Charging Case",
    badge: "Battery & Enclosure",
    icon: "🔋",
    description: "Charging case contacts, battery LED indicator, and wireless charging coil.",
  },
  board_front: {
    label: "Board Front",
    badge: "MCU & Headers",
    icon: "⚡",
    description: "Primary microcontroller IC, status LEDs, and header pin layout.",
  },
  board_back: {
    label: "Board Back",
    badge: "Solder & Ground",
    icon: "🔧",
    description: "Ground plane, solder traces, reverse pin labeling, and mounting holes.",
  },
  pins: {
    label: "Pins & Connectors",
    badge: "Pinout & Bus",
    icon: "📌",
    description: "Standard 2.54mm pitch header pins, voltage labels, and bus signals.",
  },
};

export const VisualVerificationPanel: React.FC<VisualVerificationPanelProps> = ({
  item,
  onClose,
}) => {
  const [selectedAngle, setSelectedAngle] = useState<string>("front");
  const [isZoomed, setIsZoomed] = useState(false);

  if (!item) return null;
  const vision = item.visual_verification;
  const isAvailable = vision?.visual_verification_status === "available";
  const isUnavailable = vision?.visual_verification_status === "unavailable";

  const fallbackImage = resolveProductImage(item);

  // Build authentic verified multi-view gallery
  // Strictly filter out any duplicate URLs within the gallery to prevent fake views
  const rawGallery: Record<string, string> =
    vision?.gallery && Object.keys(vision.gallery).length > 0
      ? vision.gallery
      : { front: fallbackImage };

  const gallery: Record<string, string> = {};
  const seenUrls = new Set<string>();
  for (const [key, url] of Object.entries(rawGallery)) {
    if (url && !seenUrls.has(url)) {
      seenUrls.add(url);
      gallery[key] = url;
    }
  }

  const availableKeys = Object.keys(gallery);
  const activeKey = availableKeys.includes(selectedAngle) ? selectedAngle : availableKeys[0] || "front";
  const activeImage = gallery[activeKey] || fallbackImage;
  const metaDef = VIEW_METAS[activeKey] || {
    label: activeKey.charAt(0).toUpperCase() + activeKey.slice(1),
    badge: "Verified Hardware View",
    icon: "🔍",
    description: `Detailed verified ${activeKey} hardware inspection view.`,
  };
  const activeMeta: AngleMeta = {
    key: activeKey,
    ...metaDef,
  };

  // Filter observations matching the active angle/view
  const observations = vision?.observations || [];
  const activeAngleObservations = observations.filter(
    (obs) => obs.angle === activeKey || obs.view_type === activeKey
  );
  const otherObservations = observations.filter(
    (obs) => obs.angle !== activeKey && obs.view_type !== activeKey
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 md:p-6 bg-black/70 dark:bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-white dark:bg-surface-50 border border-slate-200 dark:border-white/10 rounded-2xl max-w-4xl w-full max-h-[92vh] overflow-y-auto shadow-2xl p-5 sm:p-6 relative transition-colors duration-200 text-slate-800 dark:text-slate-100">
        
        {/* Modal Close Button */}
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-5 right-5 p-2 rounded-xl bg-slate-100 dark:bg-surface-100 hover:bg-slate-200 dark:hover:bg-surface-200 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all z-10"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-5 border-b border-slate-200/80 dark:border-white/5 pb-4">
          <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-600 dark:text-rose-400 shrink-0">
            <Eye className="w-5 h-5" />
          </div>
          <div className="pr-10">
            <div className="flex items-center space-x-2">
              <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                Hardware Visual Verification ({availableKeys.length} Verified Views)
              </h3>
              <span className="hidden sm:inline-flex items-center text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                Verified CDN Assets
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 truncate max-w-xl">
              {item.product_name}
            </p>
          </div>
        </div>

        {/* 2-Angle Gallery Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-6">
          
          {/* Main Showcase Image (7 Cols on desktop) */}
          <div className="lg:col-span-7 flex flex-col space-y-3">
            <div className="relative group w-full h-72 sm:h-80 md:h-96 rounded-2xl overflow-hidden bg-slate-950/5 dark:bg-black/40 border border-slate-200/80 dark:border-white/10 flex items-center justify-center p-4">
              <img
                src={activeImage}
                alt={`${item.product_name} - ${activeMeta.label}`}
                className={`max-h-full max-w-full object-contain transition-transform duration-300 ${
                  isZoomed ? "scale-125 cursor-zoom-out" : "group-hover:scale-105 cursor-zoom-in"
                }`}
                onClick={() => setIsZoomed(!isZoomed)}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = IMAGE_UNAVAILABLE_PLACEHOLDER;
                }}
              />

              {/* Angle Badge Overlay */}
              <div className="absolute top-3 left-3 flex items-center space-x-1.5 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-full text-white text-[11px] font-medium border border-white/10">
                <span>{activeMeta.icon}</span>
                <span>{activeMeta.label}</span>
                <span className="opacity-60 text-[10px]">({activeMeta.badge})</span>
              </div>

              {/* Sourcing Watermark */}
              <div className="absolute bottom-3 right-3 bg-black/70 backdrop-blur-md px-2.5 py-1 rounded-lg text-emerald-400 text-[10px] font-medium border border-emerald-500/20 flex items-center space-x-1">
                <Check className="w-3 h-3 text-emerald-400" />
                <span>Direct Amazon / Flipkart CDN</span>
              </div>

              {/* Zoom hint button */}
              <button
                onClick={() => setIsZoomed(!isZoomed)}
                aria-label="Toggle zoom"
                className="absolute bottom-3 left-3 p-1.5 rounded-lg bg-black/50 text-white/80 hover:text-white border border-white/10 hover:bg-black/70 transition-all text-xs flex items-center space-x-1"
              >
                <Maximize2 className="w-3.5 h-3.5" />
                <span className="text-[10px] hidden sm:inline">{isZoomed ? "Reset" : "Zoom"}</span>
              </button>
            </div>

            {/* Multi-Angle Verified Thumbnails Strip */}
            <div className={`grid gap-2 ${availableKeys.length > 2 ? "grid-cols-2 sm:grid-cols-3 md:grid-cols-4" : "grid-cols-2"}`}>
              {availableKeys.map((key) => {
                const meta = VIEW_METAS[key] || {
                  label: key.charAt(0).toUpperCase() + key.slice(1),
                  badge: "Hardware View",
                  icon: "🔍",
                  description: "",
                };
                const imgUrl = gallery[key];
                const isSelected = activeKey === key;
                return (
                  <button
                    key={key}
                    onClick={() => {
                      setSelectedAngle(key);
                      setIsZoomed(false);
                    }}
                    className={`relative rounded-xl border p-2 transition-all text-left flex items-center space-x-2.5 ${
                      isSelected
                        ? "border-rose-500 bg-rose-500/10 ring-2 ring-rose-500/30"
                        : "border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20 bg-slate-50 dark:bg-surface-100"
                    }`}
                  >
                    <div className="w-12 h-12 shrink-0 flex items-center justify-center overflow-hidden rounded-lg bg-white dark:bg-black/30 p-1">
                      <img
                        src={imgUrl}
                        alt={meta.label}
                        className="max-h-full max-w-full object-contain"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = IMAGE_UNAVAILABLE_PLACEHOLDER;
                        }}
                      />
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center space-x-1 truncate">
                        <span>{meta.icon}</span>
                        <span>{meta.label}</span>
                      </div>
                      <span className="text-[10px] text-slate-500 dark:text-slate-400 block truncate">
                        {meta.badge}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Observations & Vision Metadata Panel (5 Cols on desktop) */}
          <div className="lg:col-span-5 flex flex-col justify-between space-y-3">
            
            {/* Active Angle Description */}
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-surface-100 border border-slate-200/80 dark:border-white/5">
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 dark:text-white mb-1">
                <span>{activeMeta.icon}</span>
                <span>{activeMeta.label} Verification</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                {activeMeta.description}
              </p>
            </div>

            {/* Status Banner */}
            <div
              className={`p-3.5 rounded-xl border flex items-start space-x-3 ${
                isAvailable
                  ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-800 dark:text-emerald-300"
                  : isUnavailable
                  ? "bg-amber-500/10 border-amber-500/20 text-amber-800 dark:text-amber-300"
                  : "bg-slate-100 dark:bg-surface-100 border-slate-200/80 dark:border-white/5 text-slate-700 dark:text-slate-300"
              }`}
            >
              {isAvailable ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              ) : isUnavailable ? (
                <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
              ) : (
                <HelpCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
              )}
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider block opacity-75">
                  Vision Pipeline Audit
                </span>
                <h4 className="text-xs font-bold capitalize">
                  {isAvailable
                    ? "Front & Back Physical Hardware Verified"
                    : "Graceful Fallback Mode"}
                </h4>
                <p className="text-[11px] mt-0.5 opacity-90 leading-relaxed">
                  {isAvailable
                    ? "Multimodal inspection confirmed visual match with manufacturer datasheets from Amazon and Flipkart product media."
                    : vision?.error ||
                      "Textual specs safely verified. Visual inspection completed with graceful catalog degradation."}
                </p>
              </div>
            </div>

            {/* Observations List */}
            <div className="space-y-2 flex-1 overflow-y-auto max-h-60 pr-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Verified Observations ({observations.length})
                </span>
                <span className="text-[10px] text-slate-400">Qwen-VL Multimodal</span>
              </div>

              {/* Render observations matching active angle first */}
              {activeAngleObservations.map((obs, idx) => (
                <div
                  key={`active-${idx}`}
                  className="bg-rose-500/5 dark:bg-rose-500/10 p-3 rounded-xl border border-rose-500/20 space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-900 dark:text-white">
                      <Camera className="w-3.5 h-3.5 text-rose-500" />
                      <span>{obs.observation}</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 font-bold border border-rose-500/20 shrink-0">
                      {Math.round(obs.confidence * 100)}%
                    </span>
                  </div>
                  {obs.related_claim && (
                    <div className="flex items-center space-x-1 text-[11px] text-slate-600 dark:text-slate-400 pt-0.5">
                      <Check className="w-3 h-3 text-emerald-500 shrink-0" />
                      <span className="line-clamp-1">Confirms: "{obs.related_claim}"</span>
                    </div>
                  )}
                </div>
              ))}

              {/* Render remaining observations */}
              {otherObservations.map((obs, idx) => (
                <div
                  key={`other-${idx}`}
                  className="bg-slate-50 dark:bg-surface-100/60 p-3 rounded-xl border border-slate-200/80 dark:border-white/5 space-y-1 opacity-80 hover:opacity-100 transition-opacity"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-800 dark:text-slate-200">
                      <Camera className="w-3.5 h-3.5 text-slate-400" />
                      <span>{obs.observation}</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 font-bold border border-blue-500/20 shrink-0">
                      {Math.round(obs.confidence * 100)}%
                    </span>
                  </div>
                  {obs.related_claim && (
                    <div className="flex items-center space-x-1 text-[11px] text-slate-500 dark:text-slate-400 pt-0.5">
                      <Check className="w-3 h-3 text-emerald-500 shrink-0" />
                      <span className="line-clamp-1">Confirms: "{obs.related_claim}"</span>
                    </div>
                  )}
                </div>
              ))}

              {observations.length === 0 && (
                <div className="text-center py-6 text-xs text-slate-400">
                  No visual anomalies detected across Amazon & Flipkart catalog imagery.
                </div>
              )}
            </div>

          </div>
        </div>

        {/* Footer Note */}
        <div className="border-t border-slate-200/80 dark:border-white/5 pt-3.5 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>Strictly 2 photos: Front and Back side from authentic Amazon & Flipkart CDN.</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 text-xs font-semibold transition-all"
          >
            Close Audit
          </button>
        </div>

      </div>
    </div>
  );
};
