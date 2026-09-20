"""Grounded review analysis using ModelGateway and deterministic fraud signals."""

import re
import uuid
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

from app.core.logging import logger
from app.schemas.review_analysis import (
    AttributedFinding,
    DeepReviewReasoning,
    ReviewAnalysisResult,
    ReviewFinding,
    ReviewInput,
    SuspiciousReviewSignal,
)
from app.services.factory import get_model_gateway
from app.services.model_gateway import ModelGateway

_DUPLICATE_THRESHOLD = 0.90
_TEMPLATE_PHRASES = ("highly recommend", "must buy", "great product", "excellent product", "value for money")
_SYSTEM_PROMPT = """Analyze only supplied review records. Never invent review text, create direct quotes, or cite an unknown review ID. Return concise grounded paraphrases. Classify every supplied review by ID with pros, cons, use-case relevance, and sentiment. Aggregate findings must retain supporting review IDs. Deterministic suspicious signals are supplied separately; do not guess them."""


def _normalise_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def _word_count(text: str) -> int:
    return len(re.findall(r"[a-z0-9]+", text.lower()))


class ReviewAnalysisAgent:
    """Uses Qwen 4B for structured classification and Qwen 8B only on request."""

    def __init__(self, model_gateway: Optional[ModelGateway] = None):
        self._gateway = model_gateway or get_model_gateway()

    @staticmethod
    def detect_suspicious_signals(reviews: Sequence[ReviewInput]) -> List[SuspiciousReviewSignal]:
        """Detect reproducible duplicate, template, burst, reviewer, and detail signals."""
        signals: List[SuspiciousReviewSignal] = []
        normalised = {review.review_id: _normalise_text(review.body) for review in reviews}
        duplicate_groups: List[Set[str]] = []
        for index, left in enumerate(reviews):
            for right in reviews[index + 1 :]:
                left_text, right_text = normalised[left.review_id], normalised[right.review_id]
                if left_text and right_text and SequenceMatcher(None, left_text, right_text).ratio() >= _DUPLICATE_THRESHOLD:
                    group = next((item for item in duplicate_groups if left.review_id in item or right.review_id in item), None)
                    if group is None:
                        duplicate_groups.append({left.review_id, right.review_id})
                    else:
                        group.update((left.review_id, right.review_id))
        for group in duplicate_groups:
            signals.append(SuspiciousReviewSignal(
                signal_type="near_duplicate_text", review_ids=sorted(group),
                explanation="Review bodies exceed the deterministic near-duplicate threshold.",
            ))

        by_day: Dict[str, List[str]] = defaultdict(list)
        by_reviewer: Dict[str, List[str]] = defaultdict(list)
        for review in reviews:
            text = normalised[review.review_id]
            if any(phrase in text for phrase in _TEMPLATE_PHRASES) and _word_count(text) <= 12:
                signals.append(SuspiciousReviewSignal(
                    signal_type="template_like_text", review_ids=[review.review_id],
                    explanation="Short review contains a generic template-like endorsement phrase.",
                ))
            if review.rating in (1, 5) and _word_count(text) < 8:
                signals.append(SuspiciousReviewSignal(
                    signal_type="extreme_sentiment_without_detail", review_ids=[review.review_id],
                    explanation="Extreme rating has fewer than eight alphanumeric words of detail.",
                ))
            if review.reviewed_at:
                by_day[review.reviewed_at.date().isoformat()].append(review.review_id)
            if review.reviewer_id:
                by_reviewer[review.reviewer_id].append(review.review_id)

        burst_threshold = max(3, (len(reviews) + 1) // 2)
        for day, review_ids in by_day.items():
            if len(review_ids) >= burst_threshold:
                signals.append(SuspiciousReviewSignal(
                    signal_type="review_burst", review_ids=sorted(review_ids),
                    explanation=f"{len(review_ids)} supplied reviews share the date {day}.",
                ))
        for review_ids in by_reviewer.values():
            if len(review_ids) >= 2:
                signals.append(SuspiciousReviewSignal(
                    signal_type="reviewer_pattern", review_ids=sorted(review_ids),
                    explanation="The same reviewer identifier appears more than once in this batch.",
                ))
        return signals

    @staticmethod
    def _serialise_reviews(reviews: Iterable[ReviewInput]) -> str:
        return str([{"review_id": item.review_id, "rating": item.rating, "title": item.title, "body": item.body} for item in reviews])

    @staticmethod
    def _filter_to_supplied_ids(analysis: ReviewAnalysisResult, reviews: Sequence[ReviewInput]) -> ReviewAnalysisResult:
        """Reject model references to unseen IDs and fill missing per-review records."""
        allowed = {review.review_id for review in reviews}
        analysis.review_ids = [review.review_id for review in reviews]
        seen: Set[str] = set()
        analysis.per_review = [
            item for item in analysis.per_review
            if item.review_id in allowed and not (item.review_id in seen or seen.add(item.review_id))
        ]
        for review in reviews:
            if review.review_id not in seen:
                analysis.per_review.append(ReviewFinding(review_id=review.review_id))

        def filter_findings(items: List[AttributedFinding]) -> List[AttributedFinding]:
            result = []
            for item in items:
                ids = [review_id for review_id in item.review_ids if review_id in allowed]
                if ids:
                    result.append(item.model_copy(update={"review_ids": ids}))
            return result

        analysis.pros = filter_findings(analysis.pros)
        analysis.cons = filter_findings(analysis.cons)
        analysis.recurring_praise = filter_findings(analysis.recurring_praise)
        analysis.recurring_complaints = filter_findings(analysis.recurring_complaints)
        analysis.use_case_relevance = filter_findings(analysis.use_case_relevance)
        return analysis

    async def analyze_reviews(
        self,
        reviews: Sequence[ReviewInput],
        product_id: Optional[str] = None,
        request_id: Optional[str] = None,
        use_deep_reasoning: bool = False,
    ) -> ReviewAnalysisResult:
        """Use Qwen 4B structured output, with optional Qwen 8B deep reasoning."""
        request_id = request_id or str(uuid.uuid4())
        source_reviews = list(reviews)
        deterministic_signals = self.detect_suspicious_signals(source_reviews)
        if not source_reviews:
            return ReviewAnalysisResult(product_id=product_id, suspicious_signals=deterministic_signals)
        try:
            response = await self._gateway.generate_structured(
                prompt="Analyze these supplied reviews and return the requested schema.\nReviews: " + self._serialise_reviews(source_reviews),
                schema=ReviewAnalysisResult,
                system_prompt=_SYSTEM_PROMPT,
                temperature=0.1,
                request_id=request_id,
            )
            analysis = self._filter_to_supplied_ids(response.content, source_reviews)
        except Exception as exc:
            logger.error("Review analysis failed", extra={"request_id": request_id, "error": str(exc)})
            analysis = ReviewAnalysisResult(
                product_id=product_id,
                review_ids=[review.review_id for review in source_reviews],
                per_review=[ReviewFinding(review_id=review.review_id) for review in source_reviews],
            )
        analysis.product_id = product_id
        analysis.suspicious_signals = deterministic_signals
        if use_deep_reasoning:
            analysis.deep_reasoning = await self._run_deep_reasoning(source_reviews, request_id)
        return analysis

    async def _run_deep_reasoning(self, reviews: Sequence[ReviewInput], request_id: str) -> DeepReviewReasoning:
        """Invoke the reasoning-model gateway only for explicitly requested deep review work."""
        response = await self._gateway.generate_reasoning(
            prompt="Identify conflicts or caveats in supplied reviews. Do not quote or invent review text.\nReviews: " + self._serialise_reviews(reviews),
            system_prompt="Reason only from supplied reviews and discuss uncertainty explicitly.",
            temperature=0.1,
            request_id=request_id,
        )
        return DeepReviewReasoning(review_ids=[review.review_id for review in reviews], summary=response.content)


async def review_analysis_node(state: Dict[str, Any], model_gateway: Optional[ModelGateway] = None) -> Dict[str, Any]:
    """Supervisor-compatible review node; state must contain trusted ``reviews`` data."""
    reviews = [ReviewInput.model_validate(review) for review in state.get("reviews", [])]
    result = await ReviewAnalysisAgent(model_gateway).analyze_reviews(
        reviews, state.get("product_id"), state.get("request_id"), bool(state.get("use_deep_review_reasoning", False))
    )
    return {"review_results": [result.model_dump()]}
