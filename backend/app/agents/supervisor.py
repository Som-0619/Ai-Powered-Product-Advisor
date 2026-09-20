"""Conditional LangGraph supervisor for Product Advisor specialist agents."""

import inspect
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Mapping, Optional, Union

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

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
_WORKER_STEPS = ("retrieval", "review", "parts", "compatibility", "vision", "ranking", "evidence", "verification")
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
        self._worker_nodes = dict(worker_nodes or {})
        self._query_node = query_node or query_understanding_node
        self.max_retries = max_retries

    @staticmethod
    def create_plan(intent: Mapping[str, Any]) -> List[str]:
        """Select only the stages necessary for the understood request."""
        if intent.get("ambiguity"):
            return ["clarify"]

        category = str(intent.get("category") or "").strip().lower()
        if category in _LAPTOP_CATEGORIES:
            return ["retrieval", "review", "vision", "ranking", "evidence", "verification"]
        if category in _COMPONENT_CATEGORIES:
            return ["retrieval", "parts", "compatibility", "ranking", "evidence", "verification"]
        return ["retrieval", "ranking", "evidence"]

    async def _query(self, state: StateValue) -> Dict[str, Any]:
        current = _as_dict(state)
        try:
            result = self._query_node(
                {"raw_query": current["user_query"], "request_id": current["request_id"]}
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
        plan = self.create_plan(current.get("intent", {}))
        return {"plan": plan, "trace": _trace(current, "plan", "completed", plan=plan)}

    async def _clarify(self, state: StateValue) -> Dict[str, Any]:
        current = _as_dict(state)
        question = current.get("intent", {}).get("clarification_question") or "Could you provide a product category, budget, and use case?"
        return {
            "plan": [],
            "final_response": question,
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
        return {"trace": _trace(current, "stop", "completed")}

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


def build_supervisor_graph(
    worker_nodes: Optional[Mapping[str, NodeHandler]] = None,
    query_node: Optional[NodeHandler] = None,
    max_retries: int = 2,
) -> CompiledStateGraph:
    """Convenience factory for the Phase 8 supervisor workflow."""
    return SupervisorAgent(worker_nodes, query_node, max_retries).build_graph()
