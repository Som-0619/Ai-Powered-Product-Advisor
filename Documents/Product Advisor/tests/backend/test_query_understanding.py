"""Unit tests for the Phase 7 query-understanding agent."""

import ast
from pathlib import Path

import pytest

from app.agents.query_understanding import (
    QueryUnderstandingAgent,
    build_query_understanding_graph,
    query_understanding_node,
)
from app.schemas.query_analysis import QueryAnalysis, normalize_hinglish_shorthand
from app.services.model_gateway import ModelResponse


class StubGateway:
    """A schema-aware ModelGateway double; no local model is needed for unit tests."""

    async def generate_structured(self, *, prompt, schema, **kwargs):
        raw_query = prompt.split('Raw query: "', 1)[1].split('"\n', 1)[0].lower()
        if "best laptop under 80000 for ml" in raw_query:
            content = schema(category="Laptop", budget_max=80000.0, use_case="ML")
        elif "50k ke andar gaming laptop" in raw_query:
            content = schema(category="Laptop", subcategory="Gaming Laptop", budget_max=50000.0)
        elif "temperature sensor" in raw_query:
            content = schema(category="Sensor", subcategory="Temperature Sensor")
        elif "relay module" in raw_query:
            content = schema(category="Relay Module", subcategory="Relay Module")
        else:
            content = schema(
                ambiguity=True,
                clarification_question="What is your budget and primary use case?",
            )
        return ModelResponse(
            content=content,
            model="qwen:4b",
            role="fast",
            request_id=kwargs.get("request_id") or "test-request",
            latency_ms=1.0,
        )


@pytest.fixture
def gateway():
    return StubGateway()


def test_normalizes_hinglish_budget_shorthand():
    assert normalize_hinglish_shorthand("50k ke andar") == "50000 ke andar"
    assert normalize_hinglish_shorthand("1.5L laptop") == "150000 laptop"


@pytest.mark.asyncio
async def test_english_laptop_query_analysis(gateway):
    result = await QueryUnderstandingAgent(gateway).analyze_query("best laptop under 80000 for ML")

    assert result.category == "Laptop"
    assert result.budget_max == 80000.0
    assert result.use_case == "ML"
    assert result.language == "en"
    assert result.ambiguity is False


@pytest.mark.asyncio
async def test_hinglish_gaming_laptop_query_analysis(gateway):
    result = await QueryUnderstandingAgent(gateway).analyze_query("bhai 50k ke andar gaming laptop chahiye")

    assert result.category == "Laptop"
    assert "gaming" in result.subcategory.lower()
    assert result.budget_max == 50000.0
    assert result.currency == "INR"
    assert result.language == "hinglish"
    assert result.ambiguity is False


@pytest.mark.asyncio
async def test_hinglish_component_query_preserves_technical_constraints(gateway):
    result = await QueryUnderstandingAgent(gateway).analyze_query(
        "ESP32 ke liye 3.3V temperature sensor chahiye"
    )

    assert result.category == "Sensor"
    assert "temperature" in result.subcategory.lower()
    assert {"3.3V", "ESP32"}.issubset(set(result.hard_constraints))
    assert result.ambiguity is False


@pytest.mark.asyncio
async def test_english_relay_component_query_preserves_technical_constraints(gateway):
    result = await QueryUnderstandingAgent(gateway).analyze_query("5V relay module for Arduino")

    assert result.category in ("Module", "Component", "Relay", "Relay Module")
    assert {"5V", "Arduino"}.issubset(set(result.hard_constraints))
    assert result.ambiguity is False


@pytest.mark.asyncio
async def test_vague_query_returns_exactly_one_clarification_question(gateway):
    result = await QueryUnderstandingAgent(gateway).analyze_query("kuch accha dikhao")

    assert result.ambiguity is True
    assert result.clarification_question is not None
    assert result.clarification_question.count("?") == 1


@pytest.mark.asyncio
async def test_langgraph_graph_execution(gateway):
    graph = build_query_understanding_graph(model_gateway=gateway)
    result = await graph.ainvoke({"raw_query": "bhai 50k ke andar gaming laptop chahiye"})

    assert result["parsed_query"].category == "Laptop"
    assert result["parsed_query"].budget_max == 50000.0
    assert result["error"] is None


@pytest.mark.asyncio
async def test_node_uses_injected_gateway(gateway):
    result = await query_understanding_node(
        {"raw_query": "5V relay module for Arduino"}, model_gateway=gateway
    )
    assert result["parsed_query"].category == "Relay Module"


def test_agent_has_no_direct_ollama_or_vendor_sdk_imports():
    agent_file = Path(__file__).parents[2] / "backend/app/agents/query_understanding.py"
    imports = [node for node in ast.walk(ast.parse(agent_file.read_text())) if isinstance(node, (ast.Import, ast.ImportFrom))]
    modules = [alias.name for node in imports for alias in node.names]
    modules.extend(node.module for node in imports if isinstance(node, ast.ImportFrom) and node.module)
    assert not any("ollama" in module.lower() for module in modules)
