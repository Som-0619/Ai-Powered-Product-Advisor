"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  Search,
  Sparkles,
  ArrowRight,
  MessageSquare,
  HelpCircle,
  AlertCircle,
  Loader2,
  ArrowDownNarrowWide,
  ArrowUpNarrowWide,
} from "lucide-react";
import { RecommendationCard } from "../../components/RecommendationCard";
import { ProductDetailsModal } from "../../components/ProductDetailsModal";
import { EvidencePanel } from "../../components/EvidencePanel";
import { ReviewsPanel } from "../../components/ReviewsPanel";
import { CompatibilityPanel } from "../../components/CompatibilityPanel";
import { ChatInterface } from "../../components/ChatInterface";
import {
  streamRecommendation,
  RecommendationItem,
  RecommendationResponse,
} from "../../services/api";

function AdvisorScreen() {
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("mode") === "chat" ? "chat" : "advisor";

  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"advisor" | "chat">(initialTab);
  const [isLoading, setIsLoading] = useState(false);
  const [recommendationResult, setRecommendationResult] = useState<RecommendationResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<"expensive" | "budget">("expensive");

  // Selected item state for modals
  const [selectedDetailsItem, setSelectedDetailsItem] = useState<RecommendationItem | null>(null);
  const [selectedEvidenceItem, setSelectedEvidenceItem] = useState<RecommendationItem | null>(null);
  const [selectedReviewsItem, setSelectedReviewsItem] = useState<RecommendationItem | null>(null);
  const [selectedCompatibilityItem, setSelectedCompatibilityItem] = useState<RecommendationItem | null>(null);

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

  // Auto-run the real search when arriving from the home hero's search box
  // (?q=...) -- reuses the exact same handleSearch/streamRecommendation path
  // as a manual search, never a fake/demo result.
  //
  // Guarded with a ref (not just the empty dep array) because Next.js dev
  // mode runs with React Strict Mode, which deliberately double-invokes
  // effects on mount -- without this guard, that fired the search twice,
  // opening two concurrent Browserbase sessions for the same query and
  // roughly doubling the wait before results appeared.
  const didAutoSearch = React.useRef(false);
  useEffect(() => {
    if (didAutoSearch.current) return;
    didAutoSearch.current = true;
    const initialQuery = searchParams.get("q");
    if (initialQuery && initialQuery.trim()) {
      setQuery(initialQuery);
      handleSearch(initialQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex flex-col items-center w-full max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-2">
      {/* Mode Switcher Tabs */}
      <div className="flex items-center space-x-1 p-1 bg-surface-100 rounded-xl border border-border mb-6 shadow-sm">
        <button
          onClick={() => setActiveTab("advisor")}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-2 cursor-pointer ${
            activeTab === "advisor"
              ? "bg-card text-foreground shadow-sm font-bold border border-border"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-pa-violet" />
          <span>Product Advisor</span>
        </button>
        <button
          onClick={() => setActiveTab("chat")}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-2 cursor-pointer ${
            activeTab === "chat"
              ? "bg-card text-foreground shadow-sm font-bold border border-border"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5 text-pa-violet" />
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
          />
        </div>
      ) : (
        <div className="w-full space-y-8 animate-in fade-in duration-200">
          {/* Hero Section */}
          <section className="relative text-center max-w-2xl mx-auto pt-6 pb-4">
            <div className="pointer-events-none absolute inset-x-0 -top-6 h-56 bg-grid-fade -z-10" aria-hidden="true" />

            <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground animate-fade-up">
              Find the right product.
            </h1>

            <p className="text-sm sm:text-base text-muted-foreground mt-2.5 max-w-xl mx-auto leading-relaxed animate-fade-up [animation-delay:60ms]">
              Compare products using reviews, compatibility, visual evidence, and real product data.
            </p>

            {/* Search Bar — primary interaction, glow on focus */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSearch();
              }}
              className="mt-6 max-w-xl mx-auto w-full relative z-10 animate-fade-up [animation-delay:120ms]"
            >
              <div className="focus-glow rounded-xl p-1.5 flex items-center bg-card border border-border shadow-sm hover:border-slate-300 dark:hover:border-white/20 transition-all gap-2">
                <Search
                  className={`w-4 h-4 ml-2.5 shrink-0 pointer-events-none transition-colors duration-200 ${
                    query ? "text-pa-blue" : "text-muted-foreground"
                  }`}
                />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={isLoading}
                  placeholder="Search products or ask a question (e.g. gaming laptop under 70k)..."
                  className="flex-1 min-w-0 bg-transparent px-2 py-1.5 text-sm text-foreground placeholder-muted-foreground focus:outline-none"
                  autoFocus
                />
                <button
                  type="submit"
                  disabled={isLoading || !query.trim()}
                  className="px-4 py-2 rounded-lg bg-pa-blue hover:brightness-110 active:scale-[0.97] text-white text-xs font-semibold flex items-center space-x-1.5 transition-all shrink-0 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <span>Explore</span>
                      <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Quick Category Discovery Chips */}
            <div className="flex flex-wrap items-center justify-center gap-1.5 mt-3.5 animate-fade-up [animation-delay:180ms]">
              <span className="text-xs font-medium text-muted-foreground">Categories:</span>
              <button
                type="button"
                onClick={() => handleSearch("Smartphones")}
                className="px-3 py-1 rounded-full text-xs font-medium bg-surface-100 hover:bg-surface-200 hover:scale-[1.03] active:scale-[0.97] text-foreground border border-border transition-all cursor-pointer"
              >
                Smartphones
              </button>
              <button
                type="button"
                onClick={() => handleSearch("Laptops")}
                className="px-3 py-1 rounded-full text-xs font-medium bg-surface-100 hover:bg-surface-200 hover:scale-[1.03] active:scale-[0.97] text-foreground border border-border transition-all cursor-pointer"
              >
                Laptops
              </button>
              <button
                type="button"
                onClick={() => handleSearch("Headphones")}
                className="px-3 py-1 rounded-full text-xs font-medium bg-surface-100 hover:bg-surface-200 hover:scale-[1.03] active:scale-[0.97] text-foreground border border-border transition-all cursor-pointer"
              >
                Headphones
              </button>
              <button
                type="button"
                onClick={() => handleSearch("Electronics ESP32 IoT Components")}
                className="px-3 py-1 rounded-full text-xs font-medium bg-surface-100 hover:bg-surface-200 hover:scale-[1.03] active:scale-[0.97] text-foreground border border-border transition-all cursor-pointer"
              >
                Electronics & IoT
              </button>
            </div>
          </section>

          {/* Loading state — inline status + skeleton result cards */}
          {isLoading && (
            <div className="max-w-5xl mx-auto w-full space-y-4 animate-fade-up">
              <div className="max-w-md mx-auto p-4 rounded-xl bg-surface-100 border border-border flex items-center justify-center space-x-3 shadow-sm">
                <Loader2 className="w-4 h-4 animate-spin text-pa-blue shrink-0" />
                <span className="text-sm font-semibold text-foreground">
                  Finding the best recommendations...
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[0, 1].map((i) => (
                  <div
                    key={i}
                    className="rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-4 animate-rise-in"
                    style={{ animationDelay: `${i * 80}ms` }}
                  >
                    <div className="flex items-start gap-3">
                      <div className="skeleton w-16 h-16 sm:w-20 sm:h-20 rounded-xl shrink-0" />
                      <div className="flex-1 space-y-2 pt-1">
                        <div className="skeleton h-3 w-1/3 rounded" />
                        <div className="skeleton h-4 w-4/5 rounded" />
                        <div className="skeleton h-3 w-1/4 rounded" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="skeleton h-10 rounded-lg" />
                      <div className="skeleton h-10 rounded-lg" />
                    </div>
                    <div className="skeleton h-9 w-full rounded-xl" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Banner */}
          {errorMsg && (
            <div className="max-w-3xl mx-auto p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start space-x-3 text-rose-600 dark:text-rose-300">
              <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
              <div>
                <span className="text-xs font-bold uppercase tracking-wider block">Search Error</span>
                <p className="text-xs mt-0.5">{errorMsg}</p>
              </div>
            </div>
          )}

          {/* Clarification Notice */}
          {recommendationResult?.status === "clarification" && (
            <div className="max-w-3xl mx-auto p-5 rounded-xl bg-card border border-border shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-pa-violet">
                <HelpCircle className="w-5 h-5" />
                <h3 className="text-sm font-bold uppercase tracking-wider">Clarification Required</h3>
              </div>
              <p className="text-sm text-foreground font-medium">
                {recommendationResult.clarification_question}
              </p>
            </div>
          )}

          {/* No Results Notice */}
          {recommendationResult?.status === "no_results" && (
            <div className="max-w-3xl mx-auto p-6 rounded-xl bg-card border border-border text-center space-y-3">
              <AlertCircle className="w-7 h-7 text-amber-500 mx-auto" />
              <h3 className="text-base font-bold text-foreground">No Matching Products Found</h3>
              <p className="text-xs text-muted-foreground max-w-md mx-auto">
                {recommendationResult.message || "No products in our catalog met the specified requirements."}
              </p>
            </div>
          )}

          {/* Recommendations Grid */}
          {sortedRecommendations && sortedRecommendations.length > 0 && (
            <div className="max-w-5xl mx-auto w-full space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-border">
                <div>
                  <h3 className="text-lg font-bold text-foreground tracking-tight flex items-center space-x-2">
                    <span>Ranked Recommendations</span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-surface-100 text-muted-foreground border border-border">
                      {sortedRecommendations.length} Results
                    </span>
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Gated by budget & category • Direct verified product offers
                  </p>
                </div>

                {/* Price Sorting Toggle */}
                <div className="flex items-center space-x-1 bg-surface-100 p-1 rounded-lg border border-border text-xs self-start sm:self-auto">
                  <span className="text-[11px] font-medium text-muted-foreground px-1.5">Sort:</span>
                  <button
                    type="button"
                    onClick={() => setSortOrder("expensive")}
                    className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all flex items-center space-x-1.5 cursor-pointer ${
                      sortOrder === "expensive"
                        ? "bg-card text-foreground shadow-sm border border-border font-bold"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <ArrowDownNarrowWide className="w-3.5 h-3.5" />
                    <span>Price: High to Low</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setSortOrder("budget")}
                    className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all flex items-center space-x-1.5 cursor-pointer ${
                      sortOrder === "budget"
                        ? "bg-card text-foreground shadow-sm border border-border font-bold"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <ArrowUpNarrowWide className="w-3.5 h-3.5" />
                    <span>Price: Low to High</span>
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sortedRecommendations.map((item, idx) => (
                  <div
                    key={item.product_id}
                    className="animate-rise-in"
                    style={{ animationDelay: `${Math.min(idx, 6) * 60}ms` }}
                  >
                    <RecommendationCard
                      item={item}
                      onOpenDetails={(it) => setSelectedDetailsItem(it)}
                      onOpenEvidence={(it) => setSelectedEvidenceItem(it)}
                      onOpenReviews={(it) => setSelectedReviewsItem(it)}
                      onOpenCompatibility={(it) => setSelectedCompatibilityItem(it)}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modals */}
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
    </div>
  );
}

export default function AdvisorPage() {
  return (
    <Suspense fallback={null}>
      <AdvisorScreen />
    </Suspense>
  );
}
