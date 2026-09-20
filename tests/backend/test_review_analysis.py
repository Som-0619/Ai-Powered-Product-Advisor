"""Tests for grounded Phase 9 review analysis."""

from datetime import datetime, timezone

import pytest

from app.agents.review_analysis import ReviewAnalysisAgent, review_analysis_node
from app.schemas.review_analysis import ReviewFinding, ReviewInput
from app.services.model_gateway import ModelResponse


class StubGateway:
    def __init__(self):
        self.structured_calls = 0
        self.reasoning_calls = 0

    async def generate_structured(self, *, schema, **kwargs):
        self.structured_calls += 1
        return ModelResponse(
            content=schema(
                review_ids=["r1", "unknown"],
                per_review=[ReviewFinding(review_id="r1", pros=["Reliable performance"], sentiment="positive")],
            ),
            model="qwen:4b", role="fast", request_id="request", latency_ms=1.0,
        )

    async def generate_reasoning(self, **kwargs):
        self.reasoning_calls += 1
        return ModelResponse(
            content="The supplied reviews disagree on battery life.",
            model="qwen:8b", role="reasoning", request_id="request", latency_ms=1.0,
        )


def review(review_id, body, **kwargs):
    return ReviewInput(review_id=review_id, body=body, **kwargs)


def test_deterministic_suspicious_signal_detection():
    reviews = [
        review("r1", "Great product highly recommend", rating=5, reviewer_id="same"),
        review("r2", "Great product highly recommend", rating=5, reviewer_id="same"),
        review("r3", "Bad", rating=1),
        review("r4", "Fast delivery", reviewed_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
        review("r5", "Works well", reviewed_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
        review("r6", "Useful device", reviewed_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ]
    signal_types = {signal.signal_type for signal in ReviewAnalysisAgent.detect_suspicious_signals(reviews)}

    assert {"near_duplicate_text", "template_like_text", "review_burst", "reviewer_pattern", "extreme_sentiment_without_detail"}.issubset(signal_types)


@pytest.mark.asyncio
async def test_analysis_uses_qwen4_and_retains_only_source_ids():
    gateway = StubGateway()
    source = [review("r1", "Good keyboard and display", rating=5), review("r2", "Battery is average", rating=3)]

    result = await ReviewAnalysisAgent(gateway).analyze_reviews(source, product_id="p1")

    assert gateway.structured_calls == 1
    assert gateway.reasoning_calls == 0
    assert result.product_id == "p1"
    assert result.review_ids == ["r1", "r2"]
    assert {item.review_id for item in result.per_review} == {"r1", "r2"}
    assert '"review_id":"unknown"' not in result.model_dump_json()
    assert "Good keyboard and display" not in result.model_dump_json()


@pytest.mark.asyncio
async def test_deep_reasoning_uses_reasoning_gateway_only_when_requested():
    gateway = StubGateway()
    result = await ReviewAnalysisAgent(gateway).analyze_reviews(
        [review("r1", "Good product", rating=5)], use_deep_reasoning=True
    )

    assert gateway.structured_calls == 1
    assert gateway.reasoning_calls == 1
    assert result.deep_reasoning is not None
    assert result.deep_reasoning.review_ids == ["r1"]


@pytest.mark.asyncio
async def test_review_node_returns_structured_results():
    result = await review_analysis_node(
        {"reviews": [{"review_id": "r1", "body": "Clear sound", "rating": 4}]}, StubGateway()
    )
    assert result["review_results"][0]["review_ids"] == ["r1"]


def test_review_agent_has_no_direct_ollama_import():
    source = open("backend/app/agents/review_analysis.py", encoding="utf-8").read().lower()
    assert "import ollama" not in source
    assert "from ollama" not in source
