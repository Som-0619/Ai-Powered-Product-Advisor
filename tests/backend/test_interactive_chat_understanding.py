"""Verification script for interactive chat understanding and routing.

Tests all 12 required queries, follow-up conversational context, session isolation,
and grounded catalog evidence.
"""

import asyncio
import time
import pytest
from app.agents.supervisor import SupervisorAgent
from app.agents.query_understanding import QueryUnderstandingAgent
from app.services.session_context import SessionContextManager

QUERIES = [
    ("show laptops", "SEARCH", ["retrieval"]),
    ("show smartphones", "SEARCH", ["retrieval"]),
    ("compare these phones", "COMPARISON", ["retrieval", "ranking", "evidence"]),
    ("which one has better battery?", "COMPARISON", []),  # context follow-up
    ("recommend headphones for travel", "RECOMMENDATION", ["retrieval", "ranking", "evidence"]),
    ("summarize reviews for this laptop", "REVIEW", ["retrieval", "review", "evidence"]),
    ("is this ESP32 compatible with this sensor?", "COMPATIBILITY", ["retrieval", "parts", "compatibility", "ranking", "evidence", "verification"]),
    ("search Amazon for RTX 4060 laptop", "RETAILER_SEARCH", ["retrieval"]),
    ("what is this product?", "PRODUCT_DETAILS", []),  # context follow-up
    ("which one is cheaper?", "COMPARISON", []),  # context follow-up
    ("show me IoT components", "SEARCH", ["retrieval"]),
    ("tell me something about this product", "PRODUCT_DETAILS", []),  # context follow-up
]


@pytest.mark.asyncio
async def test_intent_classification():
    agent = QueryUnderstandingAgent()
    for query, expected_intent, _ in QUERIES:
        intent, is_follow_up, mentions = agent.classify_intent(query)
        assert intent == expected_intent, f"Query '{query}' classified as {intent}, expected {expected_intent}"


@pytest.mark.asyncio
async def test_all_12_queries_routing_and_context():
    supervisor = SupervisorAgent()
    session_a = "user_a_session_123"
    session_b = "user_b_session_456"

    # Step 1: User A searches laptops
    res_1 = await supervisor.run("show laptops", session_id=session_a)
    assert res_1["status"] == "success"
    assert len(res_1["products"]) > 0
    assert any("laptop" in p["category"].lower() or "laptop" in p["title"].lower() for p in res_1["products"])

    # Step 2: User B searches smartphones
    res_2 = await supervisor.run("show smartphones", session_id=session_b)
    assert res_2["status"] == "success"
    assert len(res_2["products"]) > 0
    assert any("phone" in p["category"].lower() or "phone" in p["title"].lower() for p in res_2["products"])

    # Step 3: User B asks follow-up: "which one is cheaper?" -> MUST evaluate User B's smartphones (with verified prices)
    res_3b = await supervisor.run("which one is cheaper?", session_id=session_b)
    assert res_3b["status"] == "success"
    assert all("phone" in p["category"].lower() or "phone" in p["title"].lower() for p in res_3b["products"])
    assert "cheaper" in res_3b["answer"].lower()
    assert "redmi" in res_3b["answer"].lower()

    # Step 3a: User A asks follow-up: "which one is cheaper?" -> laptops with unverified prices MUST NOT hallucinate
    res_3a = await supervisor.run("which one is cheaper?", session_id=session_a)
    assert res_3a["status"] == "success"
    assert all("laptop" in p["category"].lower() or "laptop" in p["title"].lower() for p in res_3a["products"])
    assert "i don't have enough verified information" in res_3a["answer"].lower()

    # Step 4: User A asks follow-up: "which one has better battery?" -> must not hallucinate if missing
    res_4 = await supervisor.run("which one has better battery?", session_id=session_a)
    assert res_4["status"] == "success"
    assert "I don't have enough verified information to determine that." in res_4["answer"] or "battery" in res_4["answer"].lower()

    # Step 5: User B asks follow-up: "compare these phones" -> MUST evaluate User B's smartphones
    res_5 = await supervisor.run("compare these phones", session_id=session_b)
    assert res_5["status"] == "success"
    assert all("phone" in p["category"].lower() or "phone" in p["title"].lower() for p in res_5["products"])

    # Step 6: Recommend headphones for travel
    res_6 = await supervisor.run("recommend headphones for travel", session_id=session_a)
    assert res_6["status"] == "success"

    # Step 7: Summarize reviews for this laptop
    res_7 = await supervisor.run("summarize reviews for this laptop", session_id=session_a)
    assert res_7["status"] == "success"
    assert "verified" in res_7["answer"].lower() or "information" in res_7["answer"].lower()

    # Step 8: Compatibility query
    res_8 = await supervisor.run("is this ESP32 compatible with this sensor?", session_id=session_a)
    assert res_8["status"] in ("success", "clarification")

    # Step 9: Retailer search
    res_9 = await supervisor.run("search Amazon for RTX 4060 laptop", session_id=session_a)
    assert res_9["status"] == "success"

    # Step 10: Show me IoT components
    res_10 = await supervisor.run("show me IoT components", session_id=session_a)
    assert res_10["status"] == "success"

    # Step 11 & 12: Tell me something about this product / What is this product?
    res_11 = await supervisor.run("tell me something about this product", session_id=session_a)
    assert res_11["status"] == "success"
    assert len(res_11["products"]) > 0

    res_12 = await supervisor.run("what is this product?", session_id=session_a)
    assert res_12["status"] == "success"
    assert len(res_12["products"]) > 0

    # Test ambiguous question without context
    res_ambig = await supervisor.run("Which is better?", session_id="fresh_empty_session_999")
    assert res_ambig["status"] == "clarification"
    assert "Which products would you like to compare?" in res_ambig["answer"]


if __name__ == "__main__":
    asyncio.run(test_intent_classification())
    asyncio.run(test_all_12_queries_routing_and_context())
    print("ALL TESTS PASSED!")
