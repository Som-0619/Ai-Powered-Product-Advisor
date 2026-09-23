"use client";

import React, { useEffect, useState } from "react";
import {
  X,
  Cpu,
  Layers,
  ExternalLink,
  ShieldCheck,
  FileText,
  Loader2,
  ShoppingCart,
  TrendingDown,
  Clock,
  Star,
  Tag,
  CheckCircle2,
  Sparkles,
} from "lucide-react";
import {
  RecommendationItem,
  ProductDetails,
  RetailerOffer,
  fetchProductDetails,
  fetchProductBuyLinks,
  fetchProductImages,
  fetchProductReviews,
  validateProductImage,
  validateProductReview,
  validateProductBuyLink,
} from "../services/api";
import { getProductStoreComparison, ProductStoreComparison } from "../services/storeComparison";
import { resolveProductImage, IMAGE_UNAVAILABLE_PLACEHOLDER } from "../services/productImages";

interface ProductDetailsModalProps {
  item: RecommendationItem | null;
  onClose: () => void;
}

export const ProductDetailsModal: React.FC<ProductDetailsModalProps> = ({ item, onClose }) => {
  const [details, setDetails] = useState<ProductDetails | null>(null);
  const [buyLinks, setBuyLinks] = useState<RetailerOffer[]>([]);
  const [images, setImages] = useState<any[]>([]);
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"compare" | "specs" | "evidence">("compare");

  useEffect(() => {
    if (!item?.product_id) return;
    const targetId = item.product_id;
    setLoading(true);

    // 1. Fetch Canonical Product Details: GET /products/{product_id}
    fetchProductDetails(targetId)
      .then((data) => {
        if (data && data.product_id && data.product_id !== targetId) {
          console.error(`[Data Integrity Error] Mismatched product details: expected ${targetId}, got ${data.product_id}`);
          setDetails(null);
        } else {
          setDetails(data);
        }
      })
      .catch((err) => {
        console.warn("Could not fetch extended details from DB, using item payload", err);
        setDetails(null);
      });

    // 2. Buy Buttons: GET /products/{product_id}/buy-links (Requirement 5)
    fetchProductBuyLinks(targetId)
      .then((res) => {
        if (res.product_id !== targetId) {
          console.error(`[Data Integrity Error] Mismatched buy-links product_id: expected ${targetId}, got ${res.product_id}`);
          setBuyLinks([]);
          return;
        }
        // Requirement 8: Validate product.product_id === buyLink.product_id
        const validLinks = (res.verified_buy_links || res.buy_links || []).filter((l) => {
          return validateProductBuyLink(targetId, l);
        });
        setBuyLinks(validLinks);
      })
      .catch((err) => {
        console.warn("Could not fetch buy-links, falling back to item retailer offers", err);
        const fallbackLinks = (item.retailer_offers || item.buy_links || []).filter((l) =>
          validateProductBuyLink(targetId, l)
        );
        setBuyLinks(fallbackLinks);
      });

    // 3. Image Gallery: GET /products/{product_id}/images (Requirement 6)
    fetchProductImages(targetId)
      .then((res) => {
        if (res.product_id !== targetId) {
          console.error(`[Data Integrity Error] Mismatched images product_id: expected ${targetId}, got ${res.product_id}`);
          setImages([]);
          return;
        }
        // Requirement 8: Validate product.product_id === image.product_id
        const validImages = (res.images || []).filter((img: any) => {
          return validateProductImage(targetId, img);
        });
        setImages(validImages);
      })
      .catch((err) => {
        console.warn("Could not fetch images, falling back to item images", err);
        const fallbackImgs = (item.images || []).filter((img: any) =>
          validateProductImage(targetId, img)
        );
        setImages(fallbackImgs);
      });

    // 4. Reviews: GET /products/{product_id}/reviews (Requirement 7)
    fetchProductReviews(targetId)
      .then((res) => {
        if (res.product_id !== targetId) {
          console.error(`[Data Integrity Error] Mismatched reviews product_id: expected ${targetId}, got ${res.product_id}`);
          setReviews([]);
          return;
        }
        // Requirement 8: Validate product.product_id === review.product_id
        const validReviews = (res.reviews || []).filter((rev: any) => {
          return validateProductReview(targetId, rev);
        });
        setReviews(validReviews);
      })
      .catch((err) => {
        console.warn("Could not fetch reviews", err);
        setReviews([]);
      })
      .finally(() => setLoading(false));
  }, [item?.product_id]);

  if (!item) return null;

  // Resolve verified buy link URLs strictly from GET /products/{product_id}/buy-links
  const amazonBuyLink = buyLinks.find((l) =>
    l.retailer === "Amazon" &&
    l.verification_status === "verified" &&
    (l.availability_status === "available" || !l.availability_status)
  );
  const flipkartBuyLink = buyLinks.find((l) =>
    l.retailer === "Flipkart" &&
    l.verification_status === "verified" &&
    (l.availability_status === "available" || !l.availability_status)
  );

  const effectiveAmazonUrl = amazonBuyLink ? amazonBuyLink.url : null;
  const effectiveFlipkartUrl = flipkartBuyLink ? flipkartBuyLink.url : null;

  const comparison: ProductStoreComparison = getProductStoreComparison(
    item.product_id,
    item.product_name,
    item.price,
    item.currency,
    effectiveAmazonUrl,
    effectiveFlipkartUrl
  );

  // Validate primary image strictly belongs to product_id
  const verifiedPrimaryImg = images.find((im) => (im.image_type === "front" || im.image_type === "primary") && im.verified);
  const fallbackVerifiedImg = images.find((im) => im.verified);
  const productImage = verifiedPrimaryImg?.image_url || fallbackVerifiedImg?.image_url || resolveProductImage(item);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-surface-50 border border-border rounded-2xl max-w-3xl w-full max-h-[92vh] overflow-y-auto shadow-2xl p-5 sm:p-7 relative transition-colors duration-200 animate-rise-in">
        {/* Close Button */}
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-4 right-4 p-2 rounded-xl bg-surface-100 hover:bg-surface-200 text-muted-foreground hover:text-foreground dark:hover:text-white transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header with Product Image */}
        <div className="flex items-start space-x-4 mb-6 pr-8">
          <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-surface-100 border border-border flex items-center justify-center shrink-0 overflow-hidden shadow-md">
            <img
              src={productImage}
              alt={item.product_name}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src = IMAGE_UNAVAILABLE_PLACEHOLDER;
              }}
            />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-1.5 mb-1">
              {item.brand && (
                <span className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
                  {item.brand}
                </span>
              )}
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-surface-100 text-muted-foreground border border-border">
                {item.category || "Electronics"}
              </span>
              {item.rank && (
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 font-bold border border-indigo-500/20">
                  Rank #{item.rank}
                </span>
              )}
            </div>
            <h3 className="text-lg sm:text-xl font-bold text-foreground tracking-tight leading-snug">
              {item.product_name}
            </h3>
            <p className="text-sm sm:text-base font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">
              Ref Price: {item.formatted_price || `$${item.price.toFixed(2)}`}
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-1 p-1 bg-surface-100 rounded-xl border border-border mb-6">
          <button
            onClick={() => setActiveTab("compare")}
            className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1.5 ${
              activeTab === "compare"
                ? "bg-surface-50 text-indigo-600 dark:text-indigo-400 shadow-sm border border-border"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <ShoppingCart className="w-3.5 h-3.5" />
            <span>Amazon vs Flipkart Comparison</span>
          </button>
          <button
            onClick={() => setActiveTab("specs")}
            className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1.5 ${
              activeTab === "specs"
                ? "bg-surface-50 text-indigo-600 dark:text-indigo-400 shadow-sm border border-border"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Specifications</span>
          </button>
          <button
            onClick={() => setActiveTab("evidence")}
            className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1.5 ${
              activeTab === "evidence"
                ? "bg-surface-50 text-indigo-600 dark:text-indigo-400 shadow-sm border border-border"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Evidence & Citations ({item.evidence?.length || 0})</span>
          </button>
        </div>

        {/* Tab 1: Amazon vs Flipkart Store Comparison */}
        {activeTab === "compare" && (
          <div className="space-y-6 animate-in fade-in duration-150">
            {/* Best Deal Banner */}
            <div className="p-3.5 rounded-xl bg-gradient-to-r from-emerald-500/10 via-indigo-500/10 to-indigo-500/10 border border-emerald-500/20 flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
                <span className="text-xs font-bold text-foreground">
                  {comparison.bestDealStore !== "Both" ? (
                    <>
                      <span className="font-extrabold text-emerald-600 dark:text-emerald-400">
                        {comparison.bestDealStore}
                      </span>{" "}
                      has the Lowest Price! Save {comparison.formattedSavings} ({comparison.savingsPercent}%)
                    </>
                  ) : (
                    "Identical pricing found on both platforms!"
                  )}
                </span>
              </div>
              <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold">
                Direct Buying Available
              </span>
            </div>

            {/* Side-by-Side Marketplace Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Amazon Card */}
              <div
                className={`rounded-2xl p-4 sm:p-5 border transition-all ${
                  comparison.deals.amazon.isLowestPrice
                    ? "border-amber-500/50 dark:border-amber-400/50 bg-amber-500/[0.03] shadow-md shadow-amber-500/5"
                    : "border-border bg-surface-100/50"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="px-3 py-1 rounded-lg font-black text-xs bg-[#FF9900] text-foreground uppercase tracking-wide">
                      Amazon
                    </span>
                    {comparison.deals.amazon.isLowestPrice && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
                        <TrendingDown className="w-3 h-3" />
                        <span>Lowest Price</span>
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-1 text-amber-500 text-xs font-bold">
                    <Star className="w-3.5 h-3.5 fill-current" />
                    <span>{comparison.deals.amazon.rating}</span>
                    <span className="text-[10px] text-muted-foreground font-normal">
                      ({comparison.deals.amazon.reviewCount})
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-baseline space-x-2">
                    <span className="text-2xl font-black text-foreground">
                      {comparison.deals.amazon.formattedPrice}
                    </span>
                    {comparison.deals.amazon.formattedOriginalPrice && (
                      <span className="text-xs text-muted-foreground line-through">
                        {comparison.deals.amazon.formattedOriginalPrice}
                      </span>
                    )}
                    {comparison.deals.amazon.discountPercent && (
                      <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
                        {comparison.deals.amazon.discountPercent}% OFF
                      </span>
                    )}
                  </div>
                  <div className="mt-2 flex items-center space-x-1.5 text-xs text-muted-foreground">
                    <Clock className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                    <span>{comparison.deals.amazon.deliveryBadge} • {comparison.deals.amazon.deliveryTime}</span>
                  </div>
                </div>

                {/* Offer Callout */}
                <div className="bg-surface-50 p-2.5 rounded-xl border border-border/70 mb-4">
                  <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-0.5">
                    Bank / Card Offers
                  </span>
                  <p className="text-[11px] text-foreground leading-snug">
                    {comparison.deals.amazon.bankOffer}
                  </p>
                </div>

                {/* Direct Buy Button */}
                {comparison.deals.amazon.isVerified && comparison.deals.amazon.url ? (
                  <a
                    href={comparison.deals.amazon.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-md shadow-amber-500/20 active:scale-[0.98]"
                  >
                    <span>Buy on Amazon</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                ) : (
                  <div className="w-full py-2.5 px-3 rounded-xl bg-surface-100 dark:bg-surface-200/50 text-muted-foreground text-center text-xs font-medium border border-border/70">
                    Currently unavailable on Amazon
                  </div>
                )}
              </div>

              {/* Flipkart Card */}
              <div
                className={`rounded-2xl p-4 sm:p-5 border transition-all ${
                  comparison.deals.flipkart.isLowestPrice
                    ? "border-blue-500/50 dark:border-blue-400/50 bg-blue-500/[0.03] shadow-md shadow-blue-500/5"
                    : "border-border bg-surface-100/50"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="px-3 py-1 rounded-lg font-black text-xs bg-[#2874F0] text-white uppercase tracking-wide">
                      Flipkart
                    </span>
                    {comparison.deals.flipkart.isLowestPrice && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
                        <TrendingDown className="w-3 h-3" />
                        <span>Lowest Price</span>
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-1 text-amber-500 text-xs font-bold">
                    <Star className="w-3.5 h-3.5 fill-current" />
                    <span>{comparison.deals.flipkart.rating}</span>
                    <span className="text-[10px] text-muted-foreground font-normal">
                      ({comparison.deals.flipkart.reviewCount})
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-baseline space-x-2">
                    <span className="text-2xl font-black text-foreground">
                      {comparison.deals.flipkart.formattedPrice}
                    </span>
                    {comparison.deals.flipkart.formattedOriginalPrice && (
                      <span className="text-xs text-muted-foreground line-through">
                        {comparison.deals.flipkart.formattedOriginalPrice}
                      </span>
                    )}
                    {comparison.deals.flipkart.discountPercent && (
                      <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
                        {comparison.deals.flipkart.discountPercent}% OFF
                      </span>
                    )}
                  </div>
                  <div className="mt-2 flex items-center space-x-1.5 text-xs text-muted-foreground">
                    <Clock className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                    <span>{comparison.deals.flipkart.deliveryBadge} • {comparison.deals.flipkart.deliveryTime}</span>
                  </div>
                </div>

                {/* Offer Callout */}
                <div className="bg-surface-50 p-2.5 rounded-xl border border-border/70 mb-4">
                  <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-0.5">
                    Bank / Card Offers
                  </span>
                  <p className="text-[11px] text-foreground leading-snug">
                    {comparison.deals.flipkart.bankOffer}
                  </p>
                </div>

                {/* Direct Buy Button */}
                {comparison.deals.flipkart.isVerified && comparison.deals.flipkart.url ? (
                  <a
                    href={comparison.deals.flipkart.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-md shadow-blue-500/20 active:scale-[0.98]"
                  >
                    <span>Buy on Flipkart</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                ) : (
                  <div className="w-full py-2.5 px-3 rounded-xl bg-surface-100 dark:bg-surface-200/50 text-muted-foreground text-center text-xs font-medium border border-border/70">
                    Currently unavailable on Flipkart
                  </div>
                )}
              </div>
            </div>

            {/* Quick Feature Comparison Matrix */}
            <div className="bg-surface-100/60 rounded-xl border border-border overflow-hidden">
              <div className="p-3 border-b border-border flex items-center justify-between">
                <span className="text-xs font-bold text-foreground">
                  Feature & Policy Comparison
                </span>
                <span className="text-[10px] text-muted-foreground">
                  Live Market Analysis
                </span>
              </div>
              <div className="divide-y divide-border text-xs">
                <div className="grid grid-cols-3 p-2.5 items-center">
                  <span className="text-muted-foreground font-medium">Selling Price</span>
                  <span className={`font-bold ${comparison.deals.amazon.isLowestPrice ? "text-emerald-600 dark:text-emerald-400 font-extrabold" : "text-foreground"}`}>
                    {comparison.deals.amazon.formattedPrice}
                  </span>
                  <span className={`font-bold ${comparison.deals.flipkart.isLowestPrice ? "text-emerald-600 dark:text-emerald-400 font-extrabold" : "text-foreground"}`}>
                    {comparison.deals.flipkart.formattedPrice}
                  </span>
                </div>
                <div className="grid grid-cols-3 p-2.5 items-center">
                  <span className="text-muted-foreground font-medium">Estimated Delivery</span>
                  <span className="text-foreground">{comparison.deals.amazon.deliveryTime}</span>
                  <span className="text-foreground">{comparison.deals.flipkart.deliveryTime}</span>
                </div>
                <div className="grid grid-cols-3 p-2.5 items-center">
                  <span className="text-muted-foreground font-medium">Customer Rating</span>
                  <span className="text-foreground">★ {comparison.deals.amazon.rating} / 5</span>
                  <span className="text-foreground">★ {comparison.deals.flipkart.rating} / 5</span>
                </div>
                <div className="grid grid-cols-3 p-2.5 items-center">
                  <span className="text-muted-foreground font-medium">Warranty</span>
                  <span className="text-foreground">{comparison.deals.amazon.warranty}</span>
                  <span className="text-foreground">{comparison.deals.flipkart.warranty}</span>
                </div>
                <div className="grid grid-cols-3 p-2.5 items-center">
                  <span className="text-muted-foreground font-medium">Replacement Policy</span>
                  <span className="text-foreground">{comparison.deals.amazon.returnPolicy}</span>
                  <span className="text-foreground">{comparison.deals.flipkart.returnPolicy}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Specifications & Component Profile */}
        {activeTab === "specs" && (
          <div className="space-y-6 animate-in fade-in duration-150">
            {loading ? (
              <div className="flex items-center justify-center py-12 text-muted-foreground space-x-2">
                <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
                <span className="text-sm">Fetching detailed specifications...</span>
              </div>
            ) : (
              <>
                {/* Description */}
                {details?.description && (
                  <div>
                    <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2">
                      Description
                    </h4>
                    <p className="text-xs text-foreground leading-relaxed bg-surface-100/50 p-3 rounded-xl border border-border">
                      {details.description}
                    </p>
                  </div>
                )}

                {/* Component Profile */}
                {details?.component_profile && (
                  <div>
                    <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                      <Cpu className="w-3.5 h-3.5 text-indigo-500" />
                      <span>Component Specifications</span>
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      <div className="bg-surface-100 p-2.5 rounded-xl border border-border">
                        <span className="text-[10px] text-muted-foreground block uppercase">
                          Part Number
                        </span>
                        <span className="text-xs font-mono font-semibold text-foreground">
                          {details.component_profile.part_number}
                        </span>
                      </div>
                      {details.component_profile.package_type && (
                        <div className="bg-surface-100 p-2.5 rounded-xl border border-border">
                          <span className="text-[10px] text-muted-foreground block uppercase">
                            Package Type
                          </span>
                          <span className="text-xs font-semibold text-foreground">
                            {details.component_profile.package_type}
                          </span>
                        </div>
                      )}
                      {details.component_profile.pin_count !== undefined && details.component_profile.pin_count > 0 && (
                        <div className="bg-surface-100 p-2.5 rounded-xl border border-border">
                          <span className="text-[10px] text-muted-foreground block uppercase">
                            Pin Count
                          </span>
                          <span className="text-xs font-semibold text-foreground">
                            {details.component_profile.pin_count} Pins
                          </span>
                        </div>
                      )}
                      {details.component_profile.mounting_type && (
                        <div className="bg-surface-100 p-2.5 rounded-xl border border-border">
                          <span className="text-[10px] text-muted-foreground block uppercase">
                            Mounting
                          </span>
                          <span className="text-xs font-semibold text-foreground">
                            {details.component_profile.mounting_type}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Technical Attributes Table */}
                {details?.specifications && Object.keys(details.specifications).length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                      <Layers className="w-3.5 h-3.5 text-indigo-500" />
                      <span>Technical Attributes</span>
                    </h4>
                    <div className="bg-surface-100/60 rounded-xl border border-border overflow-hidden">
                      <table className="w-full text-left text-xs">
                        <tbody>
                          {Object.entries(details.specifications).map(([key, value], idx) => (
                            <tr
                              key={key}
                              className={idx % 2 === 0 ? "bg-foreground/[0.02]" : ""}
                            >
                              <td className="py-2 px-3 font-semibold text-muted-foreground uppercase tracking-wider w-1/3 border-b border-border/70">
                                {key.replace(/_/g, " ")}
                              </td>
                              <td className="py-2 px-3 text-foreground border-b border-border/70 font-mono">
                                {String(value)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Tab 3: Grounded Evidence & Citations */}
        {activeTab === "evidence" && (
          <div className="space-y-3 animate-in fade-in duration-150">
            {item.evidence && item.evidence.length > 0 ? (
              item.evidence.map((ev, i) => (
                <div
                  key={i}
                  className="bg-surface-100/50 p-3.5 rounded-xl border border-border"
                >
                  <div className="flex items-center space-x-1.5 mb-1 text-emerald-600 dark:text-emerald-400 text-xs font-bold">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Verified Claim #{i + 1}</span>
                  </div>
                  <p className="text-xs text-foreground font-medium mb-1">{ev.claim}</p>
                  {ev.evidence_text && (
                    <p className="text-[11px] text-muted-foreground italic bg-surface-50 p-2 rounded-lg border border-border/70">
                      "{ev.evidence_text}"
                    </p>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No extra claim citations mapped for this item.
              </div>
            )}

            {/* Requirement 7: Grounded Customer Reviews for this product_id */}
            {reviews && reviews.length > 0 && (
              <div className="mt-4 pt-4 border-t border-border">
                <h4 className="text-xs font-bold text-foreground uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Star className="w-3.5 h-3.5 text-amber-500" />
                  <span>Verified Customer Reviews ({reviews.length})</span>
                </h4>
                <div className="space-y-2">
                  {reviews.map((rev, idx) => (
                    <div key={rev.id || idx} className="bg-surface-100/60 p-3 rounded-xl border border-border/70">
                      <div className="flex items-center justify-between text-xs font-semibold mb-1">
                        <span className="text-foreground">{rev.title || "Customer Review"}</span>
                        {rev.rating && (
                          <span className="text-amber-500 font-bold flex items-center space-x-0.5">
                            <span>★</span>
                            <span>{rev.rating}</span>
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">{rev.body}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
