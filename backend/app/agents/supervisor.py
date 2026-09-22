"""Conditional LangGraph supervisor for Product Advisor specialist agents.

Coordinates SearchAgent, ReviewAgent, CompatibilityAgent, VisionAgent,
and RecommendationAgent via typed LangGraph AgentState.
"""

import inspect
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Mapping, Optional, Union

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.core.logging import logger
from app.agents.query_understanding import query_understanding_node
from app.schemas.agent_state import AgentState
from app.schemas.query_analysis import QueryAnalysis

StateValue = Union[AgentState, Dict[str, Any]]
NodeHandler = Callable[[Dict[str, Any]], Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

_COMPONENT_CATEGORIES = {
    "component",
    "microcontroller",
    "sensor",
    "module",
    "relay",
    "relay module",
    "ic",
    "electronic component",
}
_LAPTOP_CATEGORIES = {"laptop", "notebook", "gaming laptop"}
_WORKER_STEPS = (
    "retrieval",
    "search",
    "review",
    "parts",
    "compatibility",
    "vision",
    "ranking",
    "recommendation",
    "evidence",
    "verification",
)
_STATE_FIELDS = set(AgentState.model_fields)


def _as_dict(state: StateValue) -> Dict[str, Any]:
    return state.model_dump() if isinstance(state, AgentState) else dict(state)


def _trace(state: Mapping[str, Any], node: str, status: str, **details: Any) -> List[Dict[str, Any]]:
    entries = list(state.get("trace", []))
    entries.append(
        {
            "node": node,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **details,
        }
    )
    return entries


def _get_default_worker_nodes() -> Dict[str, NodeHandler]:
    from app.agents.compatibility import compatibility_node
    from app.agents.critic import critic_node
    from app.agents.evidence import evidence_node
    from app.agents.parts import parts_node
    from app.agents.recommendation_agent import recommendation_node
    from app.agents.review_analysis import review_analysis_node
    from app.agents.search_agent import search_node
    from app.agents.vision import vision_node

    return {
        "retrieval": search_node,
        "search": search_node,
        "review": review_analysis_node,
        "parts": parts_node,
        "compatibility": compatibility_node,
        "vision": vision_node,
        "ranking": recommendation_node,
        "recommendation": recommendation_node,
        "evidence": evidence_node,
        "verification": critic_node,
    }


class SupervisorAgent:
    """Plans and conditionally routes query work without invoking unrelated agents."""

    def __init__(
        self,
        worker_nodes: Optional[Mapping[str, NodeHandler]] = None,
        query_node: Optional[NodeHandler] = None,
        max_retries: int = 2,
    ):
        if max_retries < 0:
            raise ValueError("max_retries must be zero or greater")
        unknown = set((worker_nodes or {})) - set(_WORKER_STEPS)
        if unknown:
            raise ValueError(f"Unsupported supervisor worker nodes: {sorted(unknown)}")
        self._worker_nodes = dict(_get_default_worker_nodes() if worker_nodes is None else worker_nodes)
        self._query_node = query_node or query_understanding_node
        self.max_retries = max_retries

    @staticmethod
    def create_plan(intent: Mapping[str, Any], query: str = "") -> List[str]:
        """Select only the stages necessary for the understood request."""
        if intent.get("ambiguity"):
            return ["clarify"]

        q_lower = query.lower().strip()
        category = str(intent.get("category") or "").strip().lower()

        # Visual question specifically targeting product appearance/ports
        if ("image" in q_lower or "photo" in q_lower or "picture" in q_lower) and any(
            w in q_lower for w in ("show", "port", "usb", "look", "connector", "front", "back", "color")
        ) and "compare" not in q_lower:
            return ["vision"]

        # Component compatibility
        if any(w in q_lower for w in ("compatible", "compatibility", "pinout", "voltage match")) or (
            "esp32" in q_lower and "sensor" in q_lower
        ):
            return ["retrieval", "parts", "compatibility", "ranking", "evidence", "verification"]

        # Review sentiment or review comparison
        if "review" in q_lower or "rating" in q_lower or "feedback" in q_lower:
            return ["retrieval", "review", "ranking", "evidence"]

        if category in _LAPTOP_CATEGORIES:
            return ["retrieval", "review", "vision", "ranking", "evidence", "verification"]
        if category in _COMPONENT_CATEGORIES:
            return ["retrieval", "parts", "compatibility", "ranking", "evidence", "verification"]

        return ["retrieval", "ranking", "evidence"]

    async def _query(self, state: StateValue) -> Dict[str, Any]:
        current = _as_dict(state)
        try:
            result = self._query_node(
                {"raw_query": current.get("user_query") or current.get("query") or "", "request_id": current["request_id"]}
            )
            if inspect.isawaitable(result):
                result = await result
            parsed = result.get("parsed_query")
            intent = parsed.model_dump() if isinstance(parsed, QueryAnalysis) else dict(parsed or {})
            constraints = {
                "budget_min": intent.get("budget_min"),
                "budget_max": intent.get("budget_max"),
                "currency": intent.get("currency"),
                "hard_constraints": intent.get("hard_constraints", []),
                "soft_preferences": intent.get("soft_preferences", []),
                "brand_preferences": intent.get("brand_preferences", []),
                "brand_exclusions": intent.get("brand_exclusions", []),
            }
            return {
                "intent": intent,
                "constraints": constraints,
                "trace": _trace(current, "query_understanding", "completed"),
            }
        except Exception as exc:
            error = {"node": "query_understanding", "message": str(exc)}
            return {
                "intent": {"ambiguity": True, "clarification_question": "Could you provide a product category, budget, and use case?"},
                "errors": [*current.get("errors", []), error],
                "trace": _trace(current, "query_understanding", "failed", error=str(exc)),
            }

    async def _plan(self, state: StateValue) -> Dict[str, Any]:
        current = _as_dict(state)
        query = current.get("user_query") or current.get("query") or ""
        plan = self.create_plan(current.get("intent", {}), query=query)
        return {"plan": plan, "trace": _trace(current, "plan", "completed", plan=plan)}

    async def _clarify(self, state: StateValue) -> Dict[str, Any]:
        current = _as_dict(state)
        question = current.get("intent", {}).get("clarification_question") or "Could you provide a product category, budget, and use case?"
        return {
            "plan": [],
            "final_response": question,
            "final_answer": question,
            "trace": _trace(current, "clarify", "completed"),
        }

    async def _route(self, state: StateValue) -> Dict[str, Any]:
        """Record the next selected stage before LangGraph conditionally dispatches it."""
        current = _as_dict(state)
        return {
            "trace": _trace(current, "route", "completed", next_step=self._route_next(current))
        }

    def _worker(self, step: str) -> NodeHandler:
        async def execute(state: StateValue) -> Dict[str, Any]:
            current = _as_dict(state)
            remaining = list(current.get("plan", []))
            handler = self._worker_nodes.get(step)
            if handler is None:
                return {
                    "plan": remaining[1:] if remaining and remaining[0] == step else remaining,
                    "last_failed_step": None,
                    "trace": _trace(current, step, "skipped", reason="no handler registered"),
                }

            try:
                result = handler(current)
                if inspect.isawaitable(result):
                    result = await result
                updates = {key: value for key, value in (result or {}).items() if key in _STATE_FIELDS}
                verification = updates.get("verification")
                if step == "verification" and isinstance(verification, dict) and verification.get("passed") is False:
                    retry_counts = dict(current.get("retry_counts", {}))
                    retry_counts[step] = retry_counts.get(step, 0) + 1
                    error = {"node": step, "message": "Critic verification failed.", "attempt": retry_counts[step]}
                    updates.update({
                        "plan": remaining,
                        "retry_counts": retry_counts,
                        "last_failed_step": step,
                        "errors": [*current.get("errors", []), error],
                        "trace": _trace(current, step, "failed", error=error["message"], attempt=retry_counts[step]),
                    })
                    return updates
                updates["plan"] = remaining[1:] if remaining and remaining[0] == step else remaining
                updates["last_failed_step"] = None
                updates["trace"] = _trace(current, step, "completed")
                return updates
            except Exception as exc:
                retry_counts = dict(current.get("retry_counts", {}))
                retry_counts[step] = retry_counts.get(step, 0) + 1
                error = {"node": step, "message": str(exc), "attempt": retry_counts[step]}
                return {
                    "retry_counts": retry_counts,
                    "last_failed_step": step,
                    "errors": [*current.get("errors", []), error],
                    "trace": _trace(current, step, "failed", error=str(exc), attempt=retry_counts[step]),
                }

        return execute

    async def _retry(self, state: StateValue) -> Dict[str, Any]:
        current = _as_dict(state)
        return {"trace": _trace(current, "retry", "completed", step=current.get("last_failed_step"))}

    async def _inspect(self, state: StateValue) -> Dict[str, Any]:
        """Inspect a completed worker result before routing to the next step."""
        current = _as_dict(state)
        failed_step = current.get("last_failed_step")
        return {
            "trace": _trace(
                current,
                "inspect",
                "failed" if failed_step else "completed",
                step=failed_step,
            )
        }

    async def _replan(self, state: StateValue) -> Dict[str, Any]:
        current = _as_dict(state)
        failed_step = current.get("last_failed_step")
        plan = list(current.get("plan", []))
        if plan and plan[0] == failed_step:
            plan.pop(0)
        return {
            "plan": plan,
            "last_failed_step": None,
            "trace": _trace(current, "replan", "completed", skipped_step=failed_step, plan=plan),
        }

    async def _stop(self, state: StateValue) -> Dict[str, Any]:
        current = _as_dict(state)
        answer = current.get("final_answer") or current.get("final_response")

        if not answer:
            # Generate grounded final summary from state if available
            recs = current.get("recommendation_context", [])
            compat = current.get("compatibility_context", {})
            vision = current.get("vision_context", {})

            if recs:
                top = recs[0]
                answer = f"Recommended: {top.get('title')} (Score: {top.get('final_score', 0):.2f}). Reasons: {'; '.join(top.get('ranking_reasons', [])[:2])}."
            elif compat and compat.get("reasoning"):
                answer = f"Compatibility status: {compat.get('status')}. Reasoning: {compat.get('reasoning')}."
            elif vision and vision.get("observations"):
                obs_text = "; ".join(o.get("observation", "") for o in vision["observations"])
                answer = f"Visual observations: {obs_text}"
            elif current.get("intent", {}).get("ambiguity"):
                answer = current.get("intent", {}).get("clarification_question") or "Could you clarify your request?"
            else:
                answer = "Evaluation completed based on verified product catalog evidence."

        return {
            "final_answer": answer,
            "final_response": answer,
            "trace": _trace(current, "stop", "completed"),
        }

    def _route_next(self, state: StateValue) -> str:
        plan = _as_dict(state).get("plan", [])
        return plan[0] if plan else "stop"

    def _after_execution(self, state: StateValue) -> str:
        current = _as_dict(state)
        failed_step = current.get("last_failed_step")
        if not failed_step:
            return self._route_next(current)
        retries = current.get("retry_counts", {}).get(failed_step, 0)
        return "retry" if retries <= self.max_retries else "replan"

    @staticmethod
    def _after_retry(state: StateValue) -> str:
        return _as_dict(state).get("last_failed_step") or "stop"

    def build_graph(self) -> CompiledStateGraph:
        """Compile the supervisor graph with retry and replan conditional edges."""
        workflow = StateGraph(AgentState)
        workflow.add_node("query_understanding", self._query)
        workflow.add_node("plan", self._plan)
        workflow.add_node("route", self._route)
        workflow.add_node("clarify", self._clarify)
        workflow.add_node("inspect", self._inspect)
        workflow.add_node("retry", self._retry)
        workflow.add_node("replan", self._replan)
        workflow.add_node("stop", self._stop)
        for step in _WORKER_STEPS:
            workflow.add_node(step, self._worker(step))

        workflow.add_edge(START, "query_understanding")
        workflow.add_edge("query_understanding", "plan")
        workflow.add_edge("plan", "route")
        workflow.add_conditional_edges(
            "route",
            self._route_next,
            {step: step for step in ("clarify", *_WORKER_STEPS, "stop")},
        )
        workflow.add_edge("clarify", "stop")
        for step in _WORKER_STEPS:
            workflow.add_edge(step, "inspect")
        workflow.add_conditional_edges(
            "inspect",
            self._after_execution,
            {step: step for step in (*_WORKER_STEPS, "retry", "replan", "stop")},
        )
        workflow.add_conditional_edges(
            "retry", self._after_retry, {step: step for step in (*_WORKER_STEPS, "stop")}
        )
        workflow.add_edge("replan", "route")
        workflow.add_edge("stop", END)
        return workflow.compile()

    async def run(
        self,
        user_query: str,
        request_id: Optional[str] = None,
        initial_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute the LangGraph workflow and return structured Section 32 response.

        Isolated state guarantees multi-user concurrency safety.
        """
        from app.agents import tools

        req_id = request_id or str(uuid.uuid4())
        t_sup = time.perf_counter()
        state = {
            "request_id": req_id,
            "user_query": user_query,
            "query": user_query,
            **(initial_state or {}),
        }
        graph = self.build_graph()
        output = await graph.ainvoke(state)
        final_dict = _as_dict(output)

        # 1. products
        products = []
        cands = final_dict.get("recommendation_context") or final_dict.get("search_results") or final_dict.get("candidates") or []
        for c in cands:
            products.append({
                "product_id": c.get("product_id") or c.get("id"),
                "title": c.get("title") or f"{c.get('brand', '')} {c.get('model', '')}".strip(),
                "brand": c.get("brand", ""),
                "model": c.get("model", ""),
                "category": c.get("category", ""),
                "price": c.get("price"),
                "specifications": c.get("specifications", {}),
                "primary_image_url": c.get("primary_image_url"),
                "final_score": c.get("final_score"),
                "eligible": c.get("eligible", True),
            })

        # 2. evidence
        evidence = final_dict.get("evidence", [])
        if isinstance(evidence, dict):
            evidence = evidence.get("evidence", [])

        # 3. reviews
        reviews = []
        rev_ctx = final_dict.get("review_context", {})
        if rev_ctx:
            reviews = list(rev_ctx.values())
        elif final_dict.get("review_results"):
            reviews = final_dict["review_results"]

        # 4. compatibility
        compatibility = final_dict.get("compatibility_results", [])
        if not compatibility and final_dict.get("compatibility_context"):
            compatibility = [final_dict["compatibility_context"]]

        # 5. visual_findings
        visual_findings = final_dict.get("visual_findings") or final_dict.get("vision_results") or []

        # 6. retailer_offers
        offers = final_dict.get("retailer_offers", [])
        if not offers and products:
            for p in products[:3]:
                pid = p.get("product_id")
                if pid:
                    p_offers = await tools.get_retailer_offers(pid)
                    offers.extend(p_offers)

        # 7. answer
        answer = final_dict.get("final_answer") or final_dict.get("final_response") or ""
        if not answer:
            if final_dict.get("intent", {}).get("ambiguity"):
                answer = final_dict.get("intent", {}).get("clarification_question") or "Could you clarify your request?"
            elif products:
                top_p = products[0]
                answer = f"Found {len(products)} matching option(s). Top match: {top_p['title']}."
            else:
                answer = "No products found matching the given query."

        sup_latency_ms = round((time.perf_counter() - t_sup) * 1000, 2)
        logger.info(
            f"[DEV_TRACE] Supervisor latency: {sup_latency_ms}ms, final product count: {len(products)}",
            extra={
                "supervisor_latency_ms": sup_latency_ms,
                "final_product_count": len(products),
                "request_id": req_id,
            },
        )

        return {
            "answer": answer,
            "products": products,
            "evidence": evidence,
            "reviews": reviews,
            "compatibility": compatibility,
            "visual_findings": visual_findings,
            "retailer_offers": offers,
            "confidence": final_dict.get("confidence", 1.0),
            "warnings": final_dict.get("warnings", []),
            "request_id": req_id,
            # Backward compatibility fields for frontend/orchestrator
            "reply": answer,
            "recommendations": products,
            "trace": final_dict.get("trace", []),
            "verification": final_dict.get("verification", {}),
            "status": "clarification" if final_dict.get("intent", {}).get("ambiguity") else ("no_results" if not products else "success"),
        }


def build_supervisor_graph(
    worker_nodes: Optional[Mapping[str, NodeHandler]] = None,
    query_node: Optional[NodeHandler] = None,
    max_retries: int = 2,
) -> CompiledStateGraph:
    """Convenience factory for the Phase 8 supervisor workflow."""
    return SupervisorAgent(worker_nodes, query_node, max_retries).build_graph()
