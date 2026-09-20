"""Tests for Phase 11 vision verification through ModelGateway."""

import base64

import pytest

from app.agents.vision import VisionAgent, vision_node
from app.core.exceptions import ModelUnavailableError
from app.services.model_gateway import ModelResponse

IMAGE_FIXTURE = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


class StubVisionGateway:
    def __init__(self, unavailable=False):
        self.unavailable = unavailable
        self.calls = 0

    async def generate_with_image(self, **kwargs):
        self.calls += 1
        if self.unavailable:
            raise ModelUnavailableError("VISION_MODEL is unavailable")
        return ModelResponse(
            content='[{"observation":"One USB-C port is visible.","confidence":0.92,"image_source":"wrong","related_claim":"USB-C port","agreement":"Visible port supports the claim.","disagreement":null}]',
            model="moondream:1.8b", role="vision", request_id="request", latency_ms=1.0,
        )


@pytest.mark.asyncio
async def test_vision_uses_image_gateway_and_returns_structured_observations():
    gateway = StubVisionGateway()
    result = await VisionAgent(gateway).analyze_image(
        IMAGE_FIXTURE, "fixture://one-pixel.png", ["USB-C port"], shortlisted=True
    )

    assert gateway.calls == 1
    assert result.visual_verification_status == "available"
    assert result.observations[0].image_source == "fixture://one-pixel.png"
    assert result.observations[0].related_claim == "USB-C port"


@pytest.mark.asyncio
async def test_unavailable_vision_model_does_not_crash_pipeline():
    result = await VisionAgent(StubVisionGateway(unavailable=True)).analyze_image(
        IMAGE_FIXTURE, "fixture://one-pixel.png"
    )

    assert result.visual_verification_status == "unavailable"
    assert result.observations == []


@pytest.mark.asyncio
async def test_non_shortlisted_image_is_not_sent_to_vision_model():
    gateway = StubVisionGateway()
    result = await VisionAgent(gateway).analyze_image(IMAGE_FIXTURE, "fixture://one-pixel.png", shortlisted=False)

    assert result.visual_verification_status == "not_requested"
    assert gateway.calls == 0


@pytest.mark.asyncio
async def test_vision_node_handles_missing_image():
    result = await vision_node({"image_source": "missing", "shortlisted": True}, StubVisionGateway())
    assert result["vision_results"][0]["visual_verification_status"] == "unavailable"


def test_vision_agent_has_no_direct_vendor_imports():
    source = open("backend/app/agents/vision.py", encoding="utf-8").read().lower()
    assert "import ollama" not in source
    assert "from ollama" not in source
