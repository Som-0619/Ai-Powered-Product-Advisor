"""Stage 5 LangGraph Agent Integration Test Suite.

Verifies:
1. Supervisor routing
2. Search Agent
3. Review Agent
4. Compatibility Agent
5. Vision Agent
6. Recommendation Agent
7. Product context tool
8. Product identity consistency
9. Agent isolation (no direct infrastructure access)
10. Agent error handling
11. Retry limit (max 2)
12. Missing product handling
13. Missing reviews handling ("No verified review data available.")
14. Missing images handling (Image Safety Rule)
15. Unknown/unavailable retailer status
16. No hallucinated products
17. Multi-user request isolation
18-22. 5 Integration scenarios (Section 35)
23. POST /api/chat endpoint contract (Section 32)
"""

import asyncio
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.agents import tools
from app.agents.search_agent import SearchAgent
from app.agents.review_analysis import ReviewAgent, ReviewAnalysisAgent
from app.agents.compatibility import CompatibilityAgent
from app.agents.vision import VisionAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.supervisor import SupervisorAgent
from app.schemas.agent_state import AgentState
from app.schemas.parts_analysis import PartSpecification
from app.schemas.ranking import HardConstraint, RankingConstraints
from app.schemas.review_analysis import ReviewInput
from app.services.factory import get_search_service, get_model_gateway
from app.services.product_catalog_service import ProductCatalogService


@pytest.fixture
def catalog_service():
    return ProductCatalogService()


# -------------------------------------------------------------
# 1. Supervisor Routing Tests
# -------------------------------------------------------------
def test_supervisor_plan_routing():
    """Verify conditional plan creation based on query intent and category."""
    # Ambiguous query -> clarify
    plan_ambig = SupervisorAgent.create_plan({"ambiguity": True})
    assert plan_ambig == ["clarify"]

    # Laptop -> retrieval, review, vision, ranking, evidence, verification
    plan_laptop = SupervisorAgent.create_plan({"category": "Laptop"})
    assert plan_laptop == ["retrieval", "review", "vision", "ranking", "evidence", "verification"]

    # Component/Sensor -> retrieval, parts, compatibility, ranking, evidence, verification
    plan_comp = SupervisorAgent.create_plan({"category": "Sensor"})
    assert plan_comp == ["retrieval", "parts", "compatibility", "ranking", "evidence", "verification"]

    # Pure visual question
    plan_vis = SupervisorAgent.create_plan({}, query="Does this image show USB-C?")
    assert "vision" in plan_vis

    # Compatibility question
    plan_compat = SupervisorAgent.create_plan({}, query="Is this sensor compatible with this ESP32?")
    assert "compatibility" in plan_compat
    assert "parts" in plan_compat

    # Review query
    plan_rev = SupervisorAgent.create_plan({}, query="Compare these two phones based on reviews")
    assert "review" in plan_rev

    # Simple general search query
    plan_simple = SupervisorAgent.create_plan({"category": "Audio"}, query="wireless headphones")
    assert plan_simple == ["retrieval", "ranking", "evidence"]


# -------------------------------------------------------------
# 2. Search Agent
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_search_agent_retrieval():
    """Verify SearchAgent retrieves canonical structured products without performing recommendation."""
    agent = SearchAgent()
    results = await agent.search(query="laptop", limit=5)
    assert len(results) > 0

    first = results[0]
    # Check Section 6 structured output fields
    assert "product_id" in first
    assert "brand" in first
    assert "model" in first
    assert "category" in first
    assert "relevance_score" in first
    assert "matched_fields" in first
    assert "basic_product_context" in first
    # Verify no premature recommendation fields
    assert "final_score" not in first
    assert "eligible_for_recommendation" not in first


# -------------------------------------------------------------
# 3. Review Agent
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_review_agent_grounding_and_missing_handling():
    """Verify ReviewAgent uses canonical product_id and returns explicit missing string."""
    agent = ReviewAgent()

    # Case A: Reviews provided
    reviews = [
        ReviewInput(review_id="r1", body="Excellent build quality and battery life.", rating=5),
        ReviewInput(review_id="r2", body="A bit heavy to carry daily.", rating=3),
    ]
    res = await agent.analyze_reviews(reviews, product_id="test-p1")
    assert res.product_id == "test-p1"
    assert res.review_ids == ["r1", "r2"]

    # Case B: No reviews available
    empty_res = await agent.analyze_reviews([], product_id="test-p2")
    assert empty_res.sentiment == "unknown"
    assert empty_res.review_ids == []

    # Case C: via tools for non-existent product
    tools_reviews = await tools.get_product_reviews("00000000-0000-0000-0000-000000000000")
    assert tools_reviews == []


# -------------------------------------------------------------
# 4. Compatibility Agent
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_compatibility_agent_checks():
    """Verify CompatibilityAgent distinguishes compatible, incompatible, and unknown with evidence."""
    agent = CompatibilityAgent()

    # Compatible pair
    p1 = PartSpecification(part_id="p1", voltage_min=3.3, voltage_max=3.3, interfaces=["I2C"], protocols=["I2C"])
    p2 = PartSpecification(part_id="p2", voltage_min=3.3, voltage_max=3.3, interfaces=["I2C"], protocols=["I2C"])
    res_comp = await agent.check_compatibility(p1, p2, use_deep_reasoning=False)
    assert res_comp.status in ("compatible", "possibly_compatible")
    assert any(e.check == "voltage" and e.status == "compatible" for e in res_comp.evidence)

    # Incompatible voltage pair
    p3 = PartSpecification(part_id="p3", voltage_min=5.0, voltage_max=5.0)
    res_incomp = await agent.check_compatibility(p1, p3, use_deep_reasoning=False)
    assert res_incomp.status == "incompatible"
    assert any(e.check == "voltage" and e.status == "incompatible" for e in res_incomp.evidence)


# -------------------------------------------------------------
# 5. Vision Agent & Image Safety Rule
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_vision_agent_image_safety_rule():
    """Verify Image Safety Rule: Vision rejects mismatched product_id or non-existent images."""
    agent = VisionAgent()

    # Image ownership mismatch
    res_mismatch = await agent.analyze_image(
        image_bytes=b"dummy",
        image_source="http://storage/img1.webp",
        shortlisted=True,
        product_id="prod-AAA",
        image_product_id="prod-BBB",
    )
    assert res_mismatch.visual_verification_status == "unavailable"
    assert "mismatch" in (res_mismatch.error or "").lower()

    # Non-existent product image via tools
    tool_res = await tools.analyze_product_image("00000000-0000-0000-0000-000000000000")
    assert tool_res.get("status") == "error"
    assert tool_res.get("error_type") == "image_not_found"


# -------------------------------------------------------------
# 6. Recommendation Agent
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_recommendation_agent_evaluation():
    """Verify RecommendationAgent gates candidates and scores them deterministically."""
    agent = RecommendationAgent()
    candidates = [
        {
            "product_id": "p1",
            "title": "Laptop Alpha",
            "brand": "AlphaBrand",
            "category": "Laptop",
            "price": 50000.0,
            "relevance_score": 0.9,
            "specifications": {"ram": "16GB", "ssd": "512GB"},
        },
        {
            "product_id": "p2",
            "title": "Laptop Beta",
            "brand": "BetaBrand",
            "category": "Laptop",
            "price": 120000.0,
            "relevance_score": 0.85,
            "specifications": {"ram": "32GB", "ssd": "1TB"},
        },
    ]

    # Constraint: max budget 80000
    res = await agent.recommend(
        candidates=candidates,
        constraints={"budget_max": 80000.0},
        intent={"category": "Laptop"},
    )
    recs = res["recommendations"]
    assert len(recs) == 2

    # p1 is within budget, p2 violates budget
    p1_rec = next(r for r in recs if r["product_id"] == "p1")
    p2_rec = next(r for r in recs if r["product_id"] == "p2")

    assert p1_rec["eligible"] is True
    assert p1_rec["constraint_status"] == "satisfied"
    assert p2_rec["eligible"] is False
    assert p2_rec["constraint_status"] == "violated"


# -------------------------------------------------------------
# 7. Product Context Tool
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_product_context_tool(catalog_service):
    """Verify tools.get_product_context returns compact Section 20 structured summary."""
    products = await catalog_service.get_products(limit=1)
    assert len(products) > 0
    pid = str(products[0].id)

    ctx = await tools.get_product_context(pid)
    assert ctx["found"] is True
    assert ctx["product_id"] == pid
    assert "title" in ctx
    assert "brand" in ctx
    assert "category" in ctx
    assert "key_specifications" in ctx
    assert "availability_status" in ctx
    assert "images_count" in ctx
    assert "reviews_count" in ctx


# -------------------------------------------------------------
# 8. Product Identity Consistency
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_product_identity_consistency(catalog_service):
    """Verify canonical product_id (UUID) is strictly preserved across all tool responses."""
    products = await catalog_service.get_products(limit=3)
    pids = [str(p.id) for p in products]

    for pid in pids:
        # Check get_product
        prod = await tools.get_product(pid)
        assert prod is not None
        assert prod["product_id"] == pid

        # Check get_product_images
        imgs = await tools.get_product_images(pid)
        for img in imgs:
            assert img["product_id"] == pid

        # Check get_retailer_offers
        offers = await tools.get_retailer_offers(pid)
        for off in offers:
            assert off["product_id"] == pid


# -------------------------------------------------------------
# 9. Agent Isolation
# -------------------------------------------------------------
def test_agent_isolation_no_direct_infrastructure_imports():
    """Verify agents never directly import or access PostgreSQL or MinIO clients."""
    agent_files = [
        "backend/app/agents/search_agent.py",
        "backend/app/agents/recommendation_agent.py",
        "backend/app/agents/review_analysis.py",
        "backend/app/agents/compatibility.py",
        "backend/app/agents/vision.py",
        "backend/app/agents/supervisor.py",
    ]

    prohibited = ["psycopg", "asyncpg", "minio", "boto3", "opensearchpy"]
    for path in agent_files:
        content = open(path, encoding="utf-8").read().lower()
        for term in prohibited:
            assert f"import {term}" not in content, f"Forbidden import '{term}' found in {path}"
            assert f"from {term}" not in content, f"Forbidden from-import '{term}' found in {path}"


# -------------------------------------------------------------
# 10. Agent Error Handling & 11. Retry Limit
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_agent_error_handling_and_retry_limit():
    """Verify supervisor handles worker node failures with max 2 retries and skips/replans."""
    attempts = 0

    async def failing_worker(_state):
        nonlocal attempts
        attempts += 1
        raise RuntimeError(f"Simulated failure attempt {attempts}")

    supervisor = SupervisorAgent(
        worker_nodes={"retrieval": failing_worker},
        max_retries=2,
    )
    graph = supervisor.build_graph()
    result = await graph.ainvoke({"user_query": "laptop query", "request_id": str(uuid.uuid4())})

    # Should attempt initial + 2 retries = 3 attempts total
    assert attempts == 3
    # Graph completes without throwing unhandled exception
    assert result is not None
    # Errors recorded in state
    assert len(result.get("errors", [])) >= 3
    retry_traces = [t for t in result.get("trace", []) if t["node"] == "retry"]
    assert len(retry_traces) == 2


# -------------------------------------------------------------
# 12. Missing Product Handling
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_missing_product_graceful_handling():
    """Verify querying non-existent product UUID returns None or not-found status."""
    non_existent = str(uuid.uuid4())
    p = await tools.get_product(non_existent)
    assert p is None

    ctx = await tools.get_product_context(non_existent)
    assert ctx.get("found") is False


# -------------------------------------------------------------
# 13. Missing Reviews Handling
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_missing_reviews_returns_canonical_notice():
    """Verify products without reviews return 'No verified review data available.'"""
    from app.agents.review_analysis import review_analysis_node

    non_existent_pid = str(uuid.uuid4())
    res = await review_analysis_node({"product_id": non_existent_pid})

    rev_ctx = res.get("review_context", {})
    assert non_existent_pid in rev_ctx
    assert rev_ctx[non_existent_pid]["summary"] == "No verified review data available."
    assert rev_ctx[non_existent_pid]["reviews_count"] == 0


# -------------------------------------------------------------
# 14. Missing Images Handling
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_missing_image_returns_integrity_error():
    """Verify requesting image analysis on product with no images returns integrity error."""
    non_existent_pid = str(uuid.uuid4())
    res = await tools.analyze_product_image(non_existent_pid)
    assert res["status"] == "error"
    assert res["error_type"] == "image_not_found"


# -------------------------------------------------------------
# 15. Unknown Retailer Availability
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_retailer_offer_availability_states(catalog_service):
    """Verify retailer offers strictly categorize as available, unavailable, or unknown."""
    products = await catalog_service.get_products(limit=5)
    for p in products:
        offers = await tools.get_retailer_offers(p.id)
        for o in offers:
            assert o["availability_status"] in ("available", "unavailable", "unknown")


# -------------------------------------------------------------
# 16. No Hallucinated Products
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_no_hallucinated_products(catalog_service):
    """Verify that SearchAgent only returns products that exist in canonical PostgreSQL catalog."""
    agent = SearchAgent()
    results = await agent.search("development board ESP32", limit=3)
    for r in results:
        db_prod = await catalog_service.get_product(r["product_id"])
        assert db_prod is not None
        assert str(db_prod.id) == r["product_id"]


# -------------------------------------------------------------
# 17. Multi-User Request Isolation
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_multi_user_request_isolation():
    """Verify concurrent requests with different queries execute with isolated LangGraph states."""
    supervisor = SupervisorAgent()

    req_id_1 = str(uuid.uuid4())
    req_id_2 = str(uuid.uuid4())

    task1 = supervisor.run("Dell laptop", request_id=req_id_1)
    task2 = supervisor.run("ESP32 development board", request_id=req_id_2)

    res1, res2 = await asyncio.gather(task1, task2)

    assert res1["request_id"] == req_id_1
    assert res2["request_id"] == req_id_2
    assert res1["request_id"] != res2["request_id"]

    # Verify no state leaking across concurrent runs
    pids_1 = {p["product_id"] for p in res1["products"]}
    pids_2 = {p["product_id"] for p in res2["products"]}
    assert pids_1.isdisjoint(pids_2)
    assert len(res1["trace"]) > 0
    assert len(res2["trace"]) > 0


# -------------------------------------------------------------
# 18-22. Section 35 Integration Scenarios
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_scenario_1_laptop_search_recommendation():
    """Scenario 1: 'Show me laptops for AI development' -> Search -> Recommendation -> Final."""
    supervisor = SupervisorAgent()
    res = await supervisor.run("Show me laptops for AI development")
    assert res["status"] in ("success", "clarification")
    assert len(res["products"]) > 0 or res["answer"]
    trace_nodes = [t["node"] for t in res["trace"]]
    assert "query_understanding" in trace_nodes
    assert "plan" in trace_nodes


@pytest.mark.asyncio
async def test_scenario_2_phone_review_comparison():
    """Scenario 2: 'Compare these two phones based on reviews' -> Search -> Review -> Reasoning."""
    supervisor = SupervisorAgent()
    res = await supervisor.run("Compare these two phones based on reviews")
    assert res["answer"]
    trace_nodes = [t["node"] for t in res["trace"]]
    assert "query_understanding" in trace_nodes


@pytest.mark.asyncio
async def test_scenario_3_sensor_esp32_compatibility():
    """Scenario 3: 'Is this sensor compatible with this ESP32?' -> Search -> Compatibility -> Qwen 8B."""
    supervisor = SupervisorAgent()
    res = await supervisor.run("Is this sensor compatible with this ESP32?")
    assert res["answer"]
    trace_nodes = [t["node"] for t in res["trace"]]
    assert "query_understanding" in trace_nodes


@pytest.mark.asyncio
async def test_scenario_4_image_usb_c_vision():
    """Scenario 4: 'Does this image show USB-C?' -> Vision -> Final."""
    supervisor = SupervisorAgent()
    res = await supervisor.run("Does this image show USB-C?")
    assert res["answer"]
    trace_nodes = [t["node"] for t in res["trace"]]
    assert "query_understanding" in trace_nodes


@pytest.mark.asyncio
async def test_scenario_5_headphones_anc_reviews():
    """Scenario 5: 'Find headphones with ANC and summarize their reviews' -> Search -> Review -> Recommendation."""
    supervisor = SupervisorAgent()
    res = await supervisor.run("Find headphones with ANC and summarize their reviews")
    assert res["answer"]
    trace_nodes = [t["node"] for t in res["trace"]]
    assert "query_understanding" in trace_nodes


# -------------------------------------------------------------
# 23. POST /api/chat Endpoint Contract (Section 32)
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_api_chat_endpoint_contract():
    """Verify POST /api/chat returns exact Section 32 structured output."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "query": "laptop for programming under 80000",
            "conversation_id": str(uuid.uuid4()),
        }
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()

        # Section 32 required keys
        assert "answer" in data
        assert "products" in data
        assert "evidence" in data
        assert "reviews" in data
        assert "compatibility" in data
        assert "visual_findings" in data
        assert "retailer_offers" in data
        assert "warnings" in data
        assert isinstance(data["products"], list)
        assert isinstance(data["warnings"], list)
