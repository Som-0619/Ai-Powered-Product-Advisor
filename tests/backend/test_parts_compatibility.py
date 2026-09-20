"""Tests for Phase 10 deterministic parts and compatibility agents."""

import pytest

from app.agents.compatibility import CompatibilityAgent
from app.agents.parts import PartsAgent, parts_node
from app.core.exceptions import ModelUnavailableError
from app.schemas.parts_analysis import PartInput, PartSpecification
from app.services.model_gateway import ModelResponse


class StubGateway:
    def __init__(self):
        self.structured_calls = 0
        self.reasoning_calls = 0

    async def generate_structured(self, *, schema, **kwargs):
        self.structured_calls += 1
        return ModelResponse(
            content=schema(part_id="model-id", interfaces=["I2C"], protocols=["I2C"]),
            model="qwen:4b", role="fast", request_id="request", latency_ms=1.0,
        )

    async def generate_reasoning(self, **kwargs):
        self.reasoning_calls += 1
        return ModelResponse(
            content="Confirm address selection and pull-up resistor requirements.",
            model="qwen:8b", role="reasoning", request_id="request", latency_ms=1.0,
        )


def test_parts_agent_normalizes_explicit_electrical_specs():
    source = """Manufacturer: Acme
Part Number: TMP-1
Operating voltage: 3.3V
Current: 20mA
10kΩ +/- 5%, 100nF, Power: 0.25W
I2C, QFN-16, 4 x 4 mm, 400kHz, -40C to 85C"""
    spec = PartsAgent.extract_deterministic(PartInput(part_id="p1", source_text=source))

    assert spec.manufacturer == "Acme"
    assert spec.part_number == "TMP-1"
    assert (spec.voltage_min, spec.voltage_max) == (3.3, 3.3)
    assert spec.current_max == pytest.approx(0.02)
    assert spec.resistance_ohms == 10000
    assert spec.capacitance_farads == pytest.approx(100e-9)
    assert spec.power_watts == pytest.approx(0.25)
    assert spec.tolerance_percent == 5
    assert spec.interfaces == ["I2C"]
    assert spec.package == "QFN-16"
    assert spec.dimensions_mm == [4.0, 4.0]
    assert spec.frequency_hz == 400000
    assert (spec.temperature_min_c, spec.temperature_max_c) == (-40, 85)


@pytest.mark.asyncio
async def test_parts_agent_uses_qwen4_only_for_missing_non_numeric_fields():
    gateway = StubGateway()
    result = await PartsAgent(gateway).analyze_part(PartInput(part_id="p1", source_text="I2C sensor"))

    assert gateway.structured_calls == 1
    assert result.interfaces == ["I2C"]
    assert result.part_id == "p1"


@pytest.mark.asyncio
async def test_voltage_mismatch_is_deterministically_incompatible_without_llm():
    gateway = StubGateway()
    first = PartSpecification(part_id="three-v", voltage_min=3.3, voltage_max=3.3)
    second = PartSpecification(part_id="five-v", voltage_min=5.0, voltage_max=5.0)

    result = await CompatibilityAgent(gateway).check_compatibility(first, second, use_deep_reasoning=True)

    assert result.status == "incompatible"
    assert any(item.check == "voltage" and item.status == "incompatible" for item in result.evidence)
    assert gateway.reasoning_calls == 0


@pytest.mark.asyncio
async def test_i2c_pair_is_possibly_compatible_and_uses_deep_reasoning_for_unknowns():
    gateway = StubGateway()
    controller = PartSpecification(part_id="controller", voltage_min=3.3, voltage_max=3.3, interfaces=["I2C"], protocols=["I2C"])
    sensor = PartSpecification(part_id="sensor", voltage_min=3.3, voltage_max=3.3, interfaces=["I2C"], protocols=["I2C"])

    result = await CompatibilityAgent(gateway).check_compatibility(controller, sensor)

    assert result.status == "possibly_compatible"
    assert any(item.check == "interface" and item.status == "possibly_compatible" for item in result.evidence)
    assert any(item.check == "reasoning" and not item.deterministic for item in result.evidence)
    assert gateway.reasoning_calls == 1


@pytest.mark.asyncio
async def test_missing_reasoning_model_preserves_deterministic_compatibility_result():
    class UnavailableReasoningGateway(StubGateway):
        async def generate_reasoning(self, **kwargs):
            raise ModelUnavailableError("reasoning model unavailable")

    first = PartSpecification(part_id="one", interfaces=["I2C"])
    second = PartSpecification(part_id="two", interfaces=["I2C"])
    result = await CompatibilityAgent(UnavailableReasoningGateway()).check_compatibility(first, second)

    assert result.status == "possibly_compatible"
    assert any("unavailable" in item.reasoning for item in result.evidence if item.check == "reasoning")


@pytest.mark.asyncio
async def test_parts_node_returns_structured_part_results():
    output = await parts_node({"parts": [{"part_id": "p1", "source_text": "3.3V I2C"}]}, StubGateway())
    assert output["parts_results"][0]["part_id"] == "p1"
