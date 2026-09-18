"""Test suite for Phase 6 ModelGateway LLM abstraction and LangChain Ollama adapter."""

import asyncio
import base64
import os
from typing import List, Optional
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from pydantic import BaseModel, Field

from app.adapters.local.ollama_model_gateway import LocalOllamaModelGateway
from app.core.config import settings
from app.core.exceptions import ModelUnavailableError
from app.services.model_gateway import ModelResponse, ModelRole


# Sample test schema for structured outputs
class MicrocontrollerSpec(BaseModel):
    category: str = Field(description="Category of the electronic component")
    operating_voltage: str = Field(description="Typical operating voltage, e.g. 3.3V")
    wireless_protocols: List[str] = Field(description="Supported wireless protocols, e.g. Wi-Fi, Bluetooth")


# 1x1 red PNG test image bytes
TEST_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


@pytest.fixture
def gateway():
    return LocalOllamaModelGateway()


@pytest.mark.asyncio
async def test_validate_models_reporting_exact_problem(gateway):
    """Verify validate_models correctly detects missing/unpulled tags and reports exact problem."""
    val = await gateway.validate_models()
    assert "valid" in val
    assert "available_models" in val
    assert "missing_models" in val

    # Verify qwen:4b and moondream:1.8b are recognized in the local runtime
    available = val["available_models"]
    assert any("qwen:4b" in m for m in available)
    assert any("moondream:1.8b" in m for m in available)

    # When a non-existent model like qwen:8b is configured, verify exact diagnostic report
    original_reasoning = settings.REASONING_MODEL
    try:
        settings.REASONING_MODEL = "qwen:8b"
        val_missing = await gateway.validate_models()
        assert val_missing["valid"] is False
        missing_entries = val_missing["missing_models"]
        assert any(e["model"] == "qwen:8b" for e in missing_entries)
        # Verify actionable remediation command
        remediation = [e["remediation"] for e in missing_entries if e["model"] == "qwen:8b"][0]
        assert remediation == "ollama pull qwen:8b"
    finally:
        settings.REASONING_MODEL = original_reasoning


@pytest.mark.asyncio
async def test_unavailable_model_raises_descriptive_error(gateway):
    """Verify that calling an unpulled or non-existent model raises ModelUnavailableError."""
    original_fast = settings.FAST_MODEL
    try:
        settings.FAST_MODEL = "nonexistent_model:99b"
        with pytest.raises(ModelUnavailableError) as exc_info:
            await gateway.generate("Hello world")
        err_msg = str(exc_info.value)
        assert "nonexistent_model:99b" in err_msg
        assert "is not available in local Ollama runtime" in err_msg
        assert "ollama pull nonexistent_model:99b" in err_msg
    finally:
        settings.FAST_MODEL = original_fast


@pytest.mark.asyncio
async def test_actual_generate_fast(gateway):
    """Test real fast model generation using Qwen 4B for classification."""
    prompt = "Classify this item into one of [Microcontroller, Sensor, Memory, Power]: ESP32-WROOM-32D."
    res = await gateway.generate(prompt=prompt, system_prompt="Answer with only the category name.")
    
    assert isinstance(res, ModelResponse)
    assert res.role == ModelRole.FAST.value
    assert res.model == "qwen:4b"
    assert res.request_id is not None
    assert len(res.request_id) > 10
    assert res.latency_ms > 0
    assert len(res.content.strip()) > 0
    assert res.total_tokens is not None and res.total_tokens > 0


@pytest.mark.asyncio
async def test_actual_generate_structured(gateway):
    """Test structured Pydantic extraction with Qwen 4B."""
    prompt = (
        "Extract specifications for the ESP32-WROOM-32: "
        "It is a Microcontroller operating at 3.3V with Wi-Fi and Bluetooth connectivity."
    )
    res = await gateway.generate_structured(
        prompt=prompt,
        schema=MicrocontrollerSpec,
        system_prompt="Extract hardware attributes accurately into the provided schema. For category, choose from Microcontroller, Sensor, or IC.",
    )

    assert isinstance(res, ModelResponse)
    assert isinstance(res.content, MicrocontrollerSpec)
    assert res.content.category.lower() in ("microcontroller", "mcu", "esp32", "hardware")
    assert "3.3" in res.content.operating_voltage
    assert any("wi-fi" in p.lower() or "wifi" in p.lower() or "bluetooth" in p.lower() for p in res.content.wireless_protocols)
    assert res.metadata.get("schema") == "MicrocontrollerSpec"
    assert res.latency_ms > 0
    assert res.total_tokens is not None and res.total_tokens > 0


@pytest.mark.asyncio
async def test_actual_generate_with_image(gateway):
    """Test multimodal vision call with vision-capable model (moondream:1.8b)."""
    res = await gateway.generate_with_image(
        prompt="Describe this image.",
        image_bytes=TEST_PNG_BYTES,
    )

    assert isinstance(res, ModelResponse)
    assert res.role == ModelRole.VISION.value
    assert res.model == "moondream:1.8b"
    assert res.request_id is not None
    assert res.latency_ms > 0
    assert len(res.content.strip()) > 0
    assert "red" in res.content.lower()
    assert res.metadata.get("image_size_bytes") == len(TEST_PNG_BYTES)



@pytest.mark.asyncio
async def test_actual_generate_reasoning(gateway):
    """Test deep reasoning generation with reasoning role."""
    # When reasoning model is pointed to qwen:4b in local runtime
    original_reasoning = settings.REASONING_MODEL
    try:
        settings.REASONING_MODEL = "qwen:4b"
        prompt = (
            "Evaluate technical compatibility: Can an I2C sensor running on 3.3V logic communicate "
            "safely with a 5V Arduino Uno microcontroller without bidirectional level shifting?"
        )
        res = await gateway.generate_reasoning(prompt=prompt)
        assert isinstance(res, ModelResponse)
        assert res.role == ModelRole.REASONING.value
        assert res.model == "qwen:4b"
        assert res.latency_ms > 0
        assert len(res.content.strip()) > 0
    finally:
        settings.REASONING_MODEL = original_reasoning


@pytest.mark.asyncio
async def test_bounded_retries_transient_failure_recovery(gateway):
    """Verify bounded retry loop recovers after transient network/timeout failures."""
    call_count = 0

    async def flaky_invoker():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.ConnectTimeout("Transient connection timeout")
        # Succeeded on 3rd attempt
        mock_msg = AsyncMock()
        mock_msg.content = "Success after retries"
        mock_msg.response_metadata = {"prompt_eval_count": 10, "eval_count": 5}
        mock_msg.usage_metadata = {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
        return mock_msg

    res = await gateway._invoke_with_retry(
        invoker_fn=flaky_invoker,
        operation_name="test_retry",
        request_id="test-retry-uuid",
        max_retries=3,
    )

    assert call_count == 3
    assert res.content == "Success after retries"


@pytest.mark.asyncio
async def test_bounded_retries_exhaustion(gateway):
    """Verify bounded retry loop raises error once max_retries is reached."""
    call_count = 0

    async def failing_invoker():
        nonlocal call_count
        call_count += 1
        raise httpx.ReadTimeout("Persistent read timeout")

    with pytest.raises(httpx.ReadTimeout):
        await gateway._invoke_with_retry(
            invoker_fn=failing_invoker,
            operation_name="test_exhaustion",
            request_id="test-exhaustion-uuid",
            max_retries=2,
        )

    # 1 initial attempt + 2 retries = 3 calls
    assert call_count == 3


def test_agent_decoupling_strict():
    """Verify architectural decoupling: no agent code imports ollama directly.
    
    All agents must interact exclusively through ModelGateway.
    """
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "app"))
    agents_dir = os.path.join(backend_root, "agents")
    
    # If agents directory exists, scan all python files
    if os.path.exists(agents_dir):
        for root, _, files in os.walk(agents_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        assert "import ollama" not in content, f"Direct ollama import found in {file}"
                        assert "from ollama" not in content, f"Direct ollama import found in {file}"
                        assert "from langchain_ollama" not in content, f"Direct langchain_ollama import in {file}"
