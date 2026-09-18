"use client";

import React, { useState } from "react";
import {
  Search,
  Sparkles,
  ArrowRight,
  Layers,
  MessageSquare,
  HelpCircle,
  AlertCircle,
  Loader2,
  ArrowDownNarrowWide,
  ArrowUpNarrowWide,
} from "lucide-react";
import { RecommendationCard } from "../components/RecommendationCard";
import { ProductDetailsModal } from "../components/ProductDetailsModal";
import { EvidencePanel } from "../components/EvidencePanel";
import { ReviewsPanel } from "../components/ReviewsPanel";
import { CompatibilityPanel } from "../components/CompatibilityPanel";
import { VisualVerificationPanel } from "../components/VisualVerificationPanel";
import { ChatInterface } from "../components/ChatInterface";
import { SpotlightCard } from "../components/SpotlightCard";
import {
  streamRecommendation,
  RecommendationItem,
  RecommendationResponse,
} from "../services/api";

export default function Home() {
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"advisor" | "chat">("advisor");
  const [isLoading, setIsLoading] = useState(false);
  const [recommendationResult, setRecommendationResult] = useState<RecommendationResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<"expensive" | "budget">("expensive");

  // Selected item state for modals
  const [selectedDetailsItem, setSelectedDetailsItem] = useState<RecommendationItem | null>(null);
  const [selectedEvidenceItem, setSelectedEvidenceItem] = useState<RecommendationItem | null>(null);
  const [selectedReviewsItem, setSelectedReviewsItem] = useState<RecommendationItem | null>(null);
  const [selectedCompatibilityItem, setSelectedCompatibilityItem] = useState<RecommendationItem | null>(null);
  const [selectedVisionItem, setSelectedVisionItem] = useState<RecommendationItem | null>(null);

  const sortedRecommendations = React.useMemo(() => {
    if (!recommendationResult?.recommendations) return [];
    const items = [...recommendationResult.recommendations];
    items.sort((a, b) => {
      if (a.eligible !== b.eligible) {
        return a.eligible ? -1 : 1;
      }
      if (sortOrder === "expensive") {
        return b.price - a.price;
      } else {
        return a.price - b.price;
      }
    });
    return items.map((it, idx) => ({ ...it, rank: idx + 1 }));
  }, [recommendationResult, sortOrder]);

  const handleSearch = async (queryText?: string) => {
    const textToSearch = (queryText || query).trim();
    if (!textToSearch || isLoading) return;

    if (queryText) setQuery(queryText);
    setIsLoading(true);
    setErrorMsg(null);
    setRecommendationResult(null);

    await streamRecommendation(textToSearch, {
      onStep: () => {},
      onComplete: (result: RecommendationResponse) => {
        setIsLoading(false);
        setRecommendationResult(result);
      },
      onError: (err) => {
        setIsLoading(false);
        setErrorMsg(err.message || "Failed to find recommendations.");
      },
    });
  };

  return (
    <div className="flex flex-col items-center w-full max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4">
      {/* Mode Switcher Tabs */}
      <div className="flex items-center space-x-1 p-1 bg-surface-100 rounded-2xl border border-slate-200/80 dark:border-white/5 mb-8 shadow-sm">
        <button
          onClick={() => setActiveTab("advisor")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
            activeTab === "advisor"
              ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
              : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Product Advisor</span>
        </button>
        <button
          onClick={() => setActiveTab("chat")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
            activeTab === "chat"
              ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
              : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Interactive Chat</span>
        </button>
      </div>

      {activeTab === "chat" ? (
        <div className="w-full max-w-4xl animate-in fade-in duration-200">
          <ChatInterface
            onOpenDetails={(item) => setSelectedDetailsItem(item)}
            onOpenEvidence={(item) => setSelectedEvidenceItem(item)}
            onOpenReviews={(item) => setSelectedReviewsItem(item)}
            onOpenCompatibility={(item) => setSelectedCompatibilityItem(item)}
            onOpenVision={(item) => setSelectedVisionItem(item)}
          />
        </div>
      ) : (
        <div className="w-full space-y-8 animate-in fade-in duration-200">
          {/* Hero Section */}
          <section className="text-center max-w-3xl mx-auto pt-6 pb-2">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.1]">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-slate-900 dark:from-blue-400 dark:via-indigo-300 dark:to-white">
                AI Product Advisor
              </span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 mt-3 max-w-xl mx-auto font-medium leading-relaxed">
              Find the right product. Backed by search, reviews, compatibility and evidence.
            </p>

            {/* Minimalist Search Bar with Direct Flex Layout */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSearch();
              }}
              className="mt-6 max-w-2xl mx-auto w-full relative z-10"
            >
              <div className="rounded-2xl p-2 flex items-center bg-surface-50 border border-slate-200/80 dark:border-white/10 shadow-lg shadow-blue-500/5 hover:border-blue-500/40 transition-all gap-2">
                <Search className="w-5 h-5 text-slate-400 ml-2 shrink-0 pointer-events-none" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={isLoading}
                  placeholder="Ask in English or Hinglish (e.g., 'Bhai 70k ke andar gaming laptop')..."
                  className="flex-1 min-w-0 bg-transparent px-2 py-1.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
                  autoFocus
                />
                <button
                  type="submit"
                  disabled={isLoading || !query.trim()}
                  className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-all shrink-0 disabled:opacity-40 disabled:cursor-not-allowed active:scale-95 shadow-md shadow-blue-500/20 cursor-pointer"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <span>Explore</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Quick Category Discovery Chips */}
            <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Categories:</span>
              <button
                type="button"
                onClick={() => handleSearch("Smartphones")}
                className="px-3.5 py-1 rounded-full text-xs font-semibold bg-surface-100 hover:bg-blue-600 hover:text-white text-slate-700 dark:text-slate-200 border border-slate-200/80 dark:border-white/10 transition-all cursor-pointer shadow-sm"
              >
                📱 Smartphones
              </button>
              <button
                type="button"
                onClick={() => handleSearch("Laptops")}
                className="px-3.5 py-1 rounded-full text-xs font-semibold bg-surface-100 hover:bg-blue-600 hover:text-white text-slate-700 dark:text-slate-200 border border-slate-200/80 dark:border-white/10 transition-all cursor-pointer shadow-sm"
              >
                💻 Laptops
              </button>
              <button
                type="button"
                onClick={() => handleSearch("Headphones")}
                className="px-3.5 py-1 rounded-full text-xs font-semibold bg-surface-100 hover:bg-blue-600 hover:text-white text-slate-700 dark:text-slate-200 border border-slate-200/80 dark:border-white/10 transition-all cursor-pointer shadow-sm"
              >
                🎧 Headphones
              </button>
              <button
                type="button"
                onClick={() => handleSearch("Electronics ESP32 IoT Components")}
                className="px-3.5 py-1 rounded-full text-xs font-semibold bg-surface-100 hover:bg-blue-600 hover:text-white text-slate-700 dark:text-slate-200 border border-slate-200/80 dark:border-white/10 transition-all cursor-pointer shadow-sm"
              >
                ⚡ Electronics & IoT
              </button>
            </div>

          </section>

          {/* Clean Loading Indicator */}
          {isLoading && (
            <div className="max-w-md mx-auto p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center space-x-3 shadow-sm">
              <Loader2 className="w-5 h-5 animate-spin text-blue-600 dark:text-blue-400 shrink-0" />
              <span className="text-sm font-semibold text-slate-900 dark:text-white">
                Finding the best recommendations...
              </span>
            </div>
          )}

          {/* Error Banner */}
          {errorMsg && (
            <div className="max-w-3xl mx-auto p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-3 text-rose-600 dark:text-rose-300">
              <AlertCircle className="w-5 h-5 text-rose-500 dark:text-rose-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-xs font-bold uppercase tracking-wider block">Pipeline Execution Error</span>
                <p className="text-xs mt-0.5">{errorMsg}</p>
              </div>
            </div>
          )}

          {/* Clarification Notice */}
          {recommendationResult?.status === "clarification" && (
            <div className="max-w-3xl mx-auto p-5 rounded-2xl bg-surface-50 border border-blue-500/30 shadow-md space-y-3">
              <div className="flex items-center space-x-2 text-blue-600 dark:text-blue-400">
                <HelpCircle className="w-5 h-5" />
                <h3 className="text-sm font-bold uppercase tracking-wider">Clarification Required</h3>
              </div>
              <p className="text-sm text-slate-900 dark:text-white font-medium">
                {recommendationResult.clarification_question}
              </p>
            </div>
          )}

          {/* No Results Notice */}
          {recommendationResult?.status === "no_results" && (
            <div className="max-w-3xl mx-auto p-6 rounded-2xl bg-surface-50 border border-slate-200/80 dark:border-white/10 text-center space-y-3">
              <AlertCircle className="w-8 h-8 text-amber-500 mx-auto" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">No Matching Products Found</h3>
              <p className="text-xs text-slate-600 dark:text-slate-300 max-w-md mx-auto">
                {recommendationResult.message || "No products in our catalog met the specified hard gates."}
              </p>
            </div>
          )}

          {/* Recommendations Grid */}
          {sortedRecommendations && sortedRecommendations.length > 0 && (
            <div className="max-w-5xl mx-auto w-full space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200/60 dark:border-white/5">
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight flex items-center space-x-2">
                    <span>Ranked Recommendations</span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                      {sortedRecommendations.length} Results
                    </span>
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Gated deterministically by budget & category • Direct product link on Explore
                  </p>
                </div>

                {/* Interactive Price Sorting Toggle (Expensive First vs Budget First) */}
                <div className="flex items-center space-x-1.5 bg-surface-100 p-1 rounded-xl border border-slate-200/80 dark:border-white/10 text-xs self-start sm:self-auto">
                  <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 px-1.5">Sort:</span>
                  <button
                    type="button"
                    onClick={() => setSortOrder("expensive")}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 cursor-pointer ${
                      sortOrder === "expensive"
                        ? "bg-blue-600 text-white shadow-sm"
                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                    }`}
                  >
                    <ArrowDownNarrowWide className="w-3.5 h-3.5" />
                    <span>Price: High to Low (Expensive First)</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setSortOrder("budget")}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 cursor-pointer ${
                      sortOrder === "budget"
                        ? "bg-blue-600 text-white shadow-sm"
                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                    }`}
                  >
                    <ArrowUpNarrowWide className="w-3.5 h-3.5" />
                    <span>Price: Low to High (Budget First)</span>
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {sortedRecommendations.map((item) => (
                  <RecommendationCard
                    key={item.product_id}
                    item={item}
                    onOpenDetails={(it) => setSelectedDetailsItem(it)}
                    onOpenEvidence={(it) => setSelectedEvidenceItem(it)}
                    onOpenReviews={(it) => setSelectedReviewsItem(it)}
                    onOpenCompatibility={(it) => setSelectedCompatibilityItem(it)}
                    onOpenVision={(it) => setSelectedVisionItem(it)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Interactive Panels / Modals */}
      <ProductDetailsModal
        item={selectedDetailsItem}
        onClose={() => setSelectedDetailsItem(null)}
      />

      <EvidencePanel
        item={selectedEvidenceItem}
        globalVerification={recommendationResult?.verification}
        onClose={() => setSelectedEvidenceItem(null)}
      />

      <ReviewsPanel
        item={selectedReviewsItem}
        onClose={() => setSelectedReviewsItem(null)}
      />

      <CompatibilityPanel
        item={selectedCompatibilityItem}
        onClose={() => setSelectedCompatibilityItem(null)}
      />

      <VisualVerificationPanel
        item={selectedVisionItem}
        onClose={() => setSelectedVisionItem(null)}
      />
    </div>
  );
}
