"""Routing tests for the Phase 8 LangGraph supervisor."""

import pytest

from app.agents.supervisor import SupervisorAgent
from app.schemas.query_analysis import QueryAnalysis


def query_node(category: str, *, ambiguity: bool = False):
    async def handler(_state):
        analysis = QueryAnalysis(
            category=category if not ambiguity else None,
            ambiguity=ambiguity,
            clarification_question="What is your budget and primary use case?" if ambiguity else None,
        )
        return {"parsed_query": analysis}

    return handler


def worker(name, calls):
    async def handler(_state):
        calls.append(name)
        return {}

    return handler


@pytest.mark.asyncio
async def test_laptop_routes_to_review_and_vision_only():
    calls = []
    graph = SupervisorAgent(
        {name: worker(name, calls) for name in ("retrieval", "review", "vision", "ranking", "evidence", "verification")},
        query_node("Laptop"),
    ).build_graph()

    result = await graph.ainvoke({"user_query": "laptop for gaming"})

    assert calls == ["retrieval", "review", "vision", "ranking", "evidence", "verification"]
    assert not any(entry["node"] in {"parts", "compatibility"} for entry in result["trace"])


@pytest.mark.asyncio
async def test_component_routes_to_parts_and_compatibility_only():
    calls = []
    graph = SupervisorAgent(
        {name: worker(name, calls) for name in ("retrieval", "parts", "compatibility", "ranking", "evidence", "verification")},
        query_node("Sensor"),
    ).build_graph()

    result = await graph.ainvoke({"user_query": "3.3V temperature sensor"})

    assert calls == ["retrieval", "parts", "compatibility", "ranking", "evidence", "verification"]
    assert not any(entry["node"] in {"review", "vision"} for entry in result["trace"])


@pytest.mark.asyncio
async def test_simple_query_avoids_specialist_agents():
    calls = []
    graph = SupervisorAgent(
        {name: worker(name, calls) for name in ("retrieval", "ranking", "evidence")},
        query_node("Headphones"),
    ).build_graph()

    result = await graph.ainvoke({"user_query": "wireless headphones"})

    assert calls == ["retrieval", "ranking", "evidence"]
    assert result["plan"] == []


@pytest.mark.asyncio
async def test_ambiguous_query_clarifies_without_retrieval():
    graph = SupervisorAgent(query_node=query_node("", ambiguity=True)).build_graph()

    result = await graph.ainvoke({"user_query": "something good"})

    assert result["final_response"] == "What is your budget and primary use case?"
    assert [entry["node"] for entry in result["trace"]] == ["query_understanding", "plan", "route", "clarify", "stop"]


@pytest.mark.asyncio
async def test_failed_worker_retries_up_to_configured_limit():
    attempts = 0

    async def flaky_retrieval(_state):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("temporary failure")
        return {"candidates": []}

    graph = SupervisorAgent(
        {"retrieval": flaky_retrieval}, query_node("Headphones"), max_retries=1
    ).build_graph()
    result = await graph.ainvoke({"user_query": "headphones"})

    assert attempts == 2
    assert any(entry["node"] == "retry" for entry in result["trace"])
    assert any(entry["node"] == "retrieval" and entry["status"] == "completed" for entry in result["trace"])
