"""Structured input and output models for grounded product-review analysis."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Sentiment = Literal["positive", "negative", "neutral", "mixed", "unknown"]
SignalType = Literal["near_duplicate_text", "template_like_text", "review_burst", "reviewer_pattern", "extreme_sentiment_without_detail"]


class ReviewInput(BaseModel):
    """Trusted review data; its body is input-only and never generated."""
    review_id: str
    body: str = Field(min_length=1)
    rating: Optional[float] = None
    reviewer_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    title: Optional[str] = None


class AttributedFinding(BaseModel):
    finding: str
    review_ids: List[str] = Field(min_length=1)


class ReviewFinding(BaseModel):
    review_id: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    use_case_relevance: List[str] = Field(default_factory=list)
    sentiment: Sentiment = "unknown"


class SuspiciousReviewSignal(BaseModel):
    signal_type: SignalType
    review_ids: List[str] = Field(min_length=1)
    explanation: str
    deterministic: bool = True


class DeepReviewReasoning(BaseModel):
    review_ids: List[str] = Field(min_length=1)
    summary: str


class ReviewAnalysisResult(BaseModel):
    """All findings are tied to source review IDs; no source review text is returned."""
    product_id: Optional[str] = None
    review_ids: List[str] = Field(default_factory=list)
    per_review: List[ReviewFinding] = Field(default_factory=list)
    pros: List[AttributedFinding] = Field(default_factory=list)
    cons: List[AttributedFinding] = Field(default_factory=list)
    recurring_praise: List[AttributedFinding] = Field(default_factory=list)
    recurring_complaints: List[AttributedFinding] = Field(default_factory=list)
    use_case_relevance: List[AttributedFinding] = Field(default_factory=list)
    sentiment: Sentiment = "unknown"
    suspicious_signals: List[SuspiciousReviewSignal] = Field(default_factory=list)
    deep_reasoning: Optional[DeepReviewReasoning] = None
