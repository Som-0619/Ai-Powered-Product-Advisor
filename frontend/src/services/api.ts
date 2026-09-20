/**
 * Frontend API client for Product Advisor Backend.
 * Strictly decoupled from vendor SDKs, streaming real backend state.
 */

export interface ServiceStatus {
  name: string;
  status: "ok" | "degraded" | "error" | "healthy";
  latency_ms?: number;
  details?: Record<string, any>;
  error?: string;
}

export interface ReadyResponse {
  status: "ready" | "degraded" | "healthy";
  version: string;
  timestamp: string;
  environment: string;
  services: Record<string, ServiceStatus>;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  environment: string;
}

export interface TraceStep {
  node: string;
  status: "completed" | "skipped" | "failed" | "in_progress" | "retried";
  latency_ms: number;
  details: string;
  timestamp: string;
}

export interface ClaimEvidence {
  claim: string;
  source_url?: string;
  evidence_text?: string;
  confidence?: number;
}

export interface SuspiciousSignal {
  signal_type: string;
  explanation: string;
  review_ids: string[];
}

export interface ReviewData {
  sentiment: "positive" | "negative" | "mixed" | "neutral";
  sentiment_score?: number;
  suspicious_signals?: SuspiciousSignal[];
  pros?: string[];
  cons?: string[];
  summary?: string;
}

export interface CompatibilityData {
  status: "compatible" | "possibly_compatible" | "incompatible" | "unknown";
  reasoning: string;
  checks?: Array<{
    check: string;
    status: string;
    reasoning: string;
  }>;
}

export interface VisionObservation {
  product_id?: string;
  image_id?: string;
  view_type?: string;
  observation: string;
  confidence: number;
  related_claim?: string;
  agreement?: boolean;
  angle?: string;
  image_url?: string;
}

export interface VisualVerificationData {
  visual_verification_status: "available" | "unavailable" | "not_requested";
  image_source?: string;
  observations?: VisionObservation[];
  gallery?: Record<string, string>;
  error?: string;
}

export interface RetailerOffer {
  product_id: string;
  retailer: "Amazon" | "Flipkart" | string;
  external_product_id?: string | null;
  url?: string | null;
  availability_status: "available" | "unavailable" | "unknown" | string;
  verification_status: "verified" | "broken" | "unverified" | string;
  last_verified?: string;
}

export interface RecommendationItem {
  product_id: string;
  external_product_id?: string;
  product_name: string;
  product_image?: string;
  image_url?: string;
  amazon_url?: string | null;
  flipkart_url?: string | null;
  retailer_offers?: RetailerOffer[];
  buy_links?: RetailerOffer[];
  images?: Array<{
    image_id: string;
    product_id: string;
    external_product_id?: string | null;
    image_url: string;
    image_type: string;
    source: string;
    verified: boolean;
  }>;
  brand?: string;
  category?: string;
  price: number;
  currency: string;
  formatted_price: string;
  why_recommended: string;
  pros: string[];
  cons: string[];
  confidence: number;
  rank?: number;
  eligible?: boolean;
  constraint_status?: string;
  evidence: ClaimEvidence[];
  compatibility?: CompatibilityData;
  reviews?: ReviewData;
  visual_verification?: VisualVerificationData;
}

export interface QueryIntent {
  category?: string;
  subcategory?: string;
  budget_min?: number;
  budget_max?: number;
  currency?: string;
  use_case?: string;
  language?: string;
  ambiguity?: boolean;
  clarification_question?: string;
  hard_constraints?: any;
}

export interface VerificationResult {
  passed: boolean;
  evidence_coverage_score: number;
  findings: Array<{
    check: string;
    status: string;
    reasoning: string;
  }>;
  contradictions?: string[];
}

export interface RecommendationResponse {
  status: "success" | "clarification" | "no_results" | "error";
  request_id: string;
  user_query?: string;
  message?: string;
  clarification_question?: string;
  total_latency_ms?: number;
  intent?: QueryIntent;
  recommendations: RecommendationItem[];
  trace: TraceStep[];
  verification?: VerificationResult;
}

export interface ProductDetails {
  status: string;
  id: string;
  product_id?: string;
  external_product_id?: string;
  title: string;
  slug: string;
  description?: string;
  brand?: string;
  category?: string;
  category_slug?: string;
  model_number?: string;
  sku?: string;
  is_component: boolean;
  specifications: Record<string, string>;
  component_profile?: {
    part_number: string;
    package_type?: string;
    pin_count?: number;
    mounting_type?: string;
    datasheet_url?: string;
    specs?: Record<string, any>;
  };
  prices?: Array<{
    amount: number;
    currency: string;
    is_current: boolean;
  }>;
  product_image?: string;
  image_url?: string;
  images?: Array<{
    image_id: string;
    product_id: string;
    external_product_id?: string | null;
    image_url: string;
    image_type: string;
    source: string;
    verified: boolean;
  }>;
  retailer_offers?: RetailerOffer[];
  buy_links?: RetailerOffer[];
  amazon_url?: string | null;
  flipkart_url?: string | null;
}

const API_BASE =
  typeof window !== "undefined"
    ? ""
    : process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/api/v1/health`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchReady(): Promise<ReadyResponse> {
  const res = await fetch(`${API_BASE}/api/v1/ready`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Readiness check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchProductDetails(productId: string): Promise<ProductDetails> {
  const res = await fetch(`${API_BASE}/api/v1/products/${productId}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch product details for ${productId}`);
  }
  return res.json();
}

export async function fetchProductImages(productId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/products/${productId}/images`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch product images for ${productId}`);
  }
  return res.json();
}

export async function fetchProductCompare(productId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/products/${productId}/compare`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch product comparison for ${productId}`);
  }
  return res.json();
}

export interface BuyLinksResponse {
  status: string;
  product_id: string;
  buy_links: RetailerOffer[];
  verified_buy_links: RetailerOffer[];
}

export async function fetchProductBuyLinks(productId: string): Promise<BuyLinksResponse> {
  const res = await fetch(`${API_BASE}/api/v1/products/${productId}/buy-links`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch buy links for ${productId}`);
  }
  return res.json();
}

export interface ProductReviewsResponse {
  status: string;
  product_id: string;
  count: number;
  reviews: Array<{
    id?: string;
    product_id?: string;
    title?: string;
    rating?: number;
    body?: string;
    sentiment?: string;
    sentiment_score?: number;
    verified_purchase?: boolean;
    is_suspicious?: boolean;
    fraud_score?: number;
  }>;
}

export async function fetchProductReviews(productId: string): Promise<ProductReviewsResponse> {
  const res = await fetch(`${API_BASE}/api/v1/products/${productId}/reviews`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch product reviews for ${productId}`);
  }
  return res.json();
}

/**
 * Requirement 8 & 9: Strict runtime validation before rendering.
 * Discards mismatched data, logs a clear error, and prevents cross-product pollution.
 */
export function validateProductImage(productId: string, image: any): boolean {
  if (!productId || !image || typeof image !== "object") return false;
  const imgProdId = image.product_id;
  if (!imgProdId || imgProdId !== productId) {
    console.error(`[Data Integrity Error] Mismatched image.product_id (${imgProdId}) for canonical product (${productId})`);
    return false;
  }
  return true;
}

export function validateProductReview(productId: string, review: any): boolean {
  if (!productId || !review || typeof review !== "object") return false;
  const revProdId = review.product_id;
  if (revProdId && revProdId !== productId) {
    console.error(`[Data Integrity Error] Mismatched review.product_id (${revProdId}) for canonical product (${productId})`);
    return false;
  }
  return true;
}

export function validateProductBuyLink(productId: string, buyLink: any): boolean {
  if (!productId || !buyLink || typeof buyLink !== "object") return false;
  const linkProdId = buyLink.product_id;
  if (!linkProdId || linkProdId !== productId) {
    console.error(`[Data Integrity Error] Mismatched buyLink.product_id (${linkProdId}) for canonical product (${productId})`);
    return false;
  }
  const isAvailable = buyLink.availability_status === "available" || (!buyLink.availability_status && buyLink.verification_status === "verified");
  const isVerified = buyLink.verification_status === "verified";
  if (!isAvailable || !isVerified || !buyLink.url) {
    return false;
  }
  return true;
}

export async function fetchRunTrace(requestId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/runs/${requestId}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch trace for ${requestId}`);
  }
  return res.json();
}

/**
 * Stream real backend recommendation state transitions via Server-Sent Events (SSE).
 */
export async function streamRecommendation(
  query: string,
  callbacks: {
    onStep?: (stepEvent: { step: string; status: string; message?: string; latency_ms?: number; intent?: any; count?: number }) => void;
    onComplete?: (result: RecommendationResponse) => void;
    onError?: (error: Error) => void;
  }
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/api/v1/recommend/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`Streaming failed: HTTP ${response.status} ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error("No response stream body available");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data: ")) continue;

        try {
          const payload = JSON.parse(trimmed.slice(6));
          if (payload.type === "step" && callbacks.onStep) {
            callbacks.onStep(payload);
          } else if (payload.type === "complete" && callbacks.onComplete) {
            callbacks.onComplete(payload.data);
          }
        } catch (parseErr) {
          console.error("Error parsing SSE line:", parseErr, trimmed);
        }
      }
    }
  } catch (err: any) {
    if (callbacks.onError) {
      callbacks.onError(err instanceof Error ? err : new Error(String(err)));
    } else {
      console.error("Stream recommendation error:", err);
    }
  }
}

/**
 * Send a chat message with full multi-agent conversational evaluation.
 */
export async function sendChatMessage(message: string, sessionId?: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!res.ok) {
    throw new Error(`Chat request failed: ${res.statusText}`);
  }
  return res.json();
}
