"use client";

import React from "react";
import {
  Check,
  AlertTriangle,
  FileText,
  ShieldCheck,
  MessageSquare,
  ExternalLink,
  Cpu,
  Layers,
  ChevronRight,
  ShoppingCart,
  TrendingDown,
} from "lucide-react";
import { RecommendationItem } from "../services/api";
import { SpotlightCard } from "./SpotlightCard";
import { getProductStoreComparison } from "../services/storeComparison";
import { resolveProductImage } from "../services/productImages";

interface RecommendationCardProps {
  item: RecommendationItem;
  onOpenDetails: (item: RecommendationItem) => void;
  onOpenEvidence: (item: RecommendationItem) => void;
  onOpenReviews: (item: RecommendationItem) => void;
  onOpenCompatibility: (item: RecommendationItem) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  item,
  onOpenDetails,
  onOpenEvidence,
  onOpenReviews,
  onOpenCompatibility,
}) => {
  const confidencePct = item.confidence > 0
    ? Math.min(100, Math.max(1, Math.round(item.confidence * 100)))
    : 85;
  const comparison = getProductStoreComparison(
    item.product_id,
    item.product_name,
    item.price,
    item.currency,
    item.amazon_url,
    item.flipkart_url
  );

  // Requirement 8 & 12: Broken/unverified retailer links must result in no Buy button rather than a broken destination.
  const offers = item.retailer_offers || item.buy_links || [];
  const azOffer = offers.find((o) => o.retailer === "Amazon");
  const fkOffer = offers.find((o) => o.retailer === "Flipkart");

  const isAzVerified = azOffer
    ? (azOffer.availability_status === "available" && azOffer.verification_status === "verified")
    : comparison.deals.amazon.isVerified;
  const isFkVerified = fkOffer
    ? (fkOffer.availability_status === "available" && fkOffer.verification_status === "verified")
    : comparison.deals.flipkart.isVerified;

  const amazonBuyUrl = isAzVerified
    ? (azOffer?.url || (azOffer ? null : comparison.deals.amazon.url))
    : null;
  const flipkartBuyUrl = isFkVerified
    ? (fkOffer?.url || (fkOffer ? null : comparison.deals.flipkart.url))
    : null;

  const productImage = resolveProductImage(item);

  return (
    <SpotlightCard
      className="tilt-card bg-surface-50 border border-border rounded-2xl p-5 sm:p-6 shadow-sm hover:border-accent/40 group flex flex-col justify-between h-full"
      spotlightColor="rgba(129, 140, 248, 0.14)"
    >
      {/* Top Banner & Badges */}
      <div>
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-start space-x-3 min-w-0">
            {/* Product Image Showcase */}
            <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl bg-surface-100 border border-border flex items-center justify-center shrink-0 overflow-hidden relative group-hover:scale-105 transition-transform shadow-inner">
              <img
                src={productImage}
                alt={item.product_name}
                loading="lazy"
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                onError={(e) => {
                  (e.target as HTMLImageElement).src =
                    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 400 400'><rect width='400' height='400' fill='%23f1f5f9'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='16' fill='%2364748b'>Image unavailable</text></svg>";
                }}
              />
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-1.5 mb-1">
                {item.brand && (
                  <span className="text-[10px] font-semibold text-accent uppercase tracking-wider">
                    {item.brand}
                  </span>
                )}
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-surface-100 text-muted-foreground border border-border">
                  {item.category || "Hardware"}
                </span>
                {item.rank && (
                  <span className="font-technical text-[10px] px-2 py-0.5 rounded-full bg-accent/10 text-accent border border-accent/20 font-bold">
                    #{item.rank}
                  </span>
                )}
              </div>
              <h4
                onClick={() => onOpenDetails(item)}
                className="text-base font-bold text-foreground group-hover:text-accent transition-colors line-clamp-1 cursor-pointer"
                title={item.product_name}
              >
                {item.product_name}
              </h4>
              <p className="font-technical text-lg font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5 tracking-tight">
                {item.formatted_price || `$${item.price.toFixed(2)}`}
              </p>
            </div>
          </div>

          {/* Confidence Score Gauge */}
          <div className="flex flex-col items-end shrink-0 pl-2">
            <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">
              Confidence
            </span>
            <div className="flex items-center space-x-1.5 mt-0.5">
              <div className="w-14 sm:w-16 h-2 bg-surface-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent rounded-full transition-all duration-700"
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
              <span className="font-technical text-xs font-bold text-foreground">{confidencePct}%</span>
            </div>
          </div>
        </div>

        {/* Quick Buy Marketplace Badges (Amazon & Flipkart) */}
        {(amazonBuyUrl || flipkartBuyUrl) && (
          <div className="mb-3.5 p-2.5 rounded-xl bg-surface-100/70 border border-border flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center space-x-1 text-xs">
              <ShoppingCart className="w-3.5 h-3.5 text-accent" />
              <span className="text-[11px] font-semibold text-foreground">
                Live Deals:
              </span>
            </div>

            <div className="flex items-center space-x-2">
              {/* Amazon Quick Chip */}
              {amazonBuyUrl && (
                <a
                  href={amazonBuyUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold flex items-center space-x-1 transition-all hover:scale-[1.04] active:scale-95 ${
                    comparison.deals.amazon.isLowestPrice
                      ? "bg-pa-yellow text-slate-950 shadow-sm hover:shadow-md hover:shadow-pa-yellow/30"
                      : "bg-surface-200 text-foreground hover:text-foreground"
                  }`}
                  title="View on Amazon"
                >
                  <span>Amazon: {comparison.deals.amazon.formattedPrice}</span>
                  {comparison.deals.amazon.isLowestPrice && <TrendingDown className="w-3 h-3" />}
                </a>
              )}

              {/* Flipkart Quick Chip */}
              {flipkartBuyUrl && (
                <a
                  href={flipkartBuyUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold flex items-center space-x-1 transition-all hover:scale-[1.04] active:scale-95 ${
                    comparison.deals.flipkart.isLowestPrice
                      ? "bg-accent text-accent-foreground shadow-sm hover:shadow-md hover:shadow-accent/20"
                      : "bg-surface-200 text-foreground hover:text-foreground"
                  }`}
                  title="View on Flipkart"
                >
                  <span>Flipkart: {comparison.deals.flipkart.formattedPrice}</span>
                  {comparison.deals.flipkart.isLowestPrice && <TrendingDown className="w-3 h-3" />}
                </a>
              )}
            </div>
          </div>
        )}

        {/* Pros & Cons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
          {/* Pros */}
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-pa-mint uppercase tracking-wider flex items-center space-x-1">
              <Check className="w-3 h-3" />
              <span>Key Advantages</span>
            </span>
            <ul className="space-y-1">
              {item.pros.slice(0, 2).map((pro, i) => (
                <li key={i} className="text-xs text-muted-foreground flex items-start space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-pa-mint mt-1.5 shrink-0" />
                  <span className="line-clamp-1">{pro}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Cons */}
          <div className="space-y-1.5">
            <span className="text-[11px] font-semibold text-pa-coral uppercase tracking-wider flex items-center space-x-1">
              <AlertTriangle className="w-3 h-3" />
              <span>Caveats / Tradeoffs</span>
            </span>
            <ul className="space-y-1">
              {item.cons.slice(0, 1).map((con, i) => (
                <li key={i} className="text-xs text-muted-foreground flex items-start space-x-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-pa-coral mt-1.5 shrink-0" />
                  <span className="line-clamp-1">{con}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Interactive Action Bar */}
      <div className="border-t border-border pt-3.5 mt-1">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center flex-wrap gap-1.5">
            {/* Specs Button */}
            <button
              onClick={() => onOpenDetails(item)}
              className="px-2.5 py-1.5 rounded-lg bg-surface-100 hover:bg-surface-200 hover:-translate-y-px active:translate-y-0 active:scale-95 border border-border text-xs text-foreground font-medium flex items-center space-x-1 transition-all cursor-pointer"
            >
              <Layers className="w-3.5 h-3.5 text-accent" />
              <span>Specs</span>
            </button>


            {/* Reviews Button */}
            {item.reviews && (
              <button
                onClick={() => onOpenReviews(item)}
                className="px-2.5 py-1.5 rounded-lg bg-surface-100 hover:bg-surface-200 hover:-translate-y-px active:translate-y-0 active:scale-95 border border-border text-xs text-foreground font-medium flex items-center space-x-1 transition-all cursor-pointer"
              >
                <MessageSquare className="w-3.5 h-3.5 text-accent" />
                <span>Reviews</span>
              </button>
            )}

            {/* Compatibility Button */}
            {item.compatibility && (
              <button
                onClick={() => onOpenCompatibility(item)}
                className="px-2.5 py-1.5 rounded-lg bg-surface-100 hover:bg-surface-200 hover:-translate-y-px active:translate-y-0 active:scale-95 border border-border text-xs text-foreground font-medium flex items-center space-x-1 transition-all cursor-pointer"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-accent" />
                <span>Compatibility</span>
              </button>
            )}
          </div>

          {/* Direct Amazon / Flipkart Buy Links & Compare Deals */}
          <div className="flex items-center flex-wrap gap-2">
            <button
              onClick={() => onOpenDetails(item)}
              className="px-2.5 py-1.5 rounded-xl bg-surface-100 hover:bg-surface-200 border border-border text-xs font-semibold text-foreground flex items-center space-x-1 transition-all active:scale-95 cursor-pointer"
              title="Compare Amazon vs Flipkart Deals"
            >
              <span>Compare</span>
            </button>
            {amazonBuyUrl && (
              <a
                href={amazonBuyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3.5 py-1.5 rounded-xl bg-[#FF9900] hover:bg-[#F28B00] text-slate-950 font-bold text-xs flex items-center space-x-1.5 shadow-md shadow-amber-500/20 hover:shadow-lg hover:shadow-amber-500/30 active:scale-95 transition-all cursor-pointer"
                title={`Buy ${item.product_name} directly on Amazon`}
              >
                <ShoppingCart className="w-3.5 h-3.5 text-slate-950" />
                <span>Buy on Amazon</span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-950/70" />
              </a>
            )}
            {flipkartBuyUrl && (
              <a
                href={flipkartBuyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3.5 py-1.5 rounded-xl bg-[#2874F0] hover:bg-blue-600 text-white font-bold text-xs flex items-center space-x-1.5 shadow-md shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/30 active:scale-95 transition-all cursor-pointer"
                title={`Buy ${item.product_name} directly on Flipkart`}
              >
                <ShoppingCart className="w-3.5 h-3.5 text-white" />
                <span>Buy on Flipkart</span>
                <ExternalLink className="w-3.5 h-3.5 text-white/70" />
              </a>
            )}
          </div>
        </div>
      </div>
    </SpotlightCard>
  );
};
