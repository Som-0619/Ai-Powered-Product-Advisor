"""Search Agent.

Responsible solely for product retrieval using the search tool layer.
Retrieves candidate products matching the user query with canonical hydration.
Never generates recommendations.
"""

import time
from typing import Any, Dict, List, Optional
from app.agents import tools
from app.core.logging import logger


class SearchAgent:
    """Retrieval specialist agent decoupled from underlying search/storage infrastructure."""

    def __init__(self):
        pass

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        mode: str = "hybrid",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search products catalog using canonical OpenSearch + PostgreSQL tool.

        Returns structured candidate dictionaries containing:
        - product_id (canonical UUID)
        - brand
        - model
        - category
        - relevance_score
        - matched_fields
        - basic_product_context
        - price
        - specifications
        - primary_image_url
        """
        logger.info("SearchAgent executing retrieval", extra={"query": query, "category": category, "brand": brand, "mode": mode})
        t0 = time.perf_counter()
        results = await tools.search_products(
            query=query,
            category=category,
            brand=brand,
            filters=filters,
            mode=mode,
            limit=limit,
        )
        sa_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        logger.info(
            f"[DEV_TRACE] SearchAgent latency: {sa_latency_ms}ms, candidates returned: {len(results)}",
            extra={"search_agent_latency_ms": sa_latency_ms, "search_agent_result_count": len(results)},
        )
        return results


async def search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for SearchAgent."""
    agent = SearchAgent()
    query = state.get("query") or state.get("user_query") or ""
    intent = state.get("intent") or {}
    constraints = state.get("constraints") or {}

    category = intent.get("category")
    brand = intent.get("brand") or (constraints.get("brand_preferences", [None])[0] if constraints.get("brand_preferences") else None)
    
    # Check if hard_constraints contains brand or category
    filters = {}
    for hc in constraints.get("hard_constraints", []):
        if isinstance(hc, dict) and hc.get("key") in ("brand", "category"):
            filters[hc["key"]] = hc.get("value")

    search_results = await agent.search(
        query=query,
        category=category,
        brand=brand,
        filters=filters if filters else None,
        mode="hybrid",
        limit=10,
    )

    selected_products = [r["product_id"] for r in search_results]

    # Pre-populate product context map for retrieved candidates
    product_context = dict(state.get("product_context", {}))
    for r in search_results:
        pid = r["product_id"]
        if pid not in product_context:
            product_context[pid] = {
                "product_id": pid,
                "title": f"{r.get('brand', '')} {r.get('model', '')}".strip() or r.get("title", ""),
                "brand": r.get("brand", ""),
                "model": r.get("model", ""),
                "category": r.get("category", ""),
                "price": r.get("price"),
                "specifications": r.get("specifications", {}),
                "primary_image_url": r.get("primary_image_url"),
                "relevance_score": r.get("relevance_score", 0.0),
                "basic_product_context": r.get("basic_product_context", ""),
            }

    return {
        "search_results": search_results,
        "candidates": search_results,  # backward compatibility
        "selected_products": selected_products,
        "product_context": product_context,
    }
