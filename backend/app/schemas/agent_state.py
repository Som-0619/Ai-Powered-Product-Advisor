"""Shared LangGraph state for the Product Advisor supervisor workflow."""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """State owned and updated by the supervisor and its routed specialist nodes."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    user_query: str
    intent: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    plan: List[str] = Field(default_factory=list)
    candidates: List[Dict[str, Any]] = Field(default_factory=list)
    review_results: List[Dict[str, Any]] = Field(default_factory=list)
    parts_results: List[Dict[str, Any]] = Field(default_factory=list)
    compatibility_results: List[Dict[str, Any]] = Field(default_factory=list)
    vision_results: List[Dict[str, Any]] = Field(default_factory=list)
    ranking_results: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    verification: Dict[str, Any] = Field(default_factory=dict)
    trace: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    final_response: Optional[str] = None

    # Supervisor control fields. These remain internal to orchestration and are not
    # consumed by downstream product-advisor agents.
    retry_counts: Dict[str, int] = Field(default_factory=dict)
    last_failed_step: Optional[str] = None
