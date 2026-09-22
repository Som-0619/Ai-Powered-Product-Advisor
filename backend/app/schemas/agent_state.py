"""Shared LangGraph state for the Product Advisor supervisor workflow."""

from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """State owned and updated by the supervisor and its routed specialist nodes."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    user_query: str
    query: Optional[str] = None
    intent: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    plan: List[str] = Field(default_factory=list)

    # Retrieval and Product Context
    candidates: List[Dict[str, Any]] = Field(default_factory=list)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    selected_products: List[str] = Field(default_factory=list)
    product_context: Dict[str, Any] = Field(default_factory=dict)

    # Specialist Findings
    review_results: List[Dict[str, Any]] = Field(default_factory=list)
    review_context: Dict[str, Any] = Field(default_factory=dict)
    parts_results: List[Dict[str, Any]] = Field(default_factory=list)
    compatibility_results: List[Dict[str, Any]] = Field(default_factory=list)
    compatibility_context: Dict[str, Any] = Field(default_factory=dict)
    vision_results: List[Dict[str, Any]] = Field(default_factory=list)
    vision_context: Dict[str, Any] = Field(default_factory=dict)
    visual_findings: List[Dict[str, Any]] = Field(default_factory=list)
    ranking_results: List[Dict[str, Any]] = Field(default_factory=list)
    recommendation_context: List[Dict[str, Any]] = Field(default_factory=list)

    # Grounding and Outputs
    evidence: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(default_factory=list)
    retailer_offers: List[Dict[str, Any]] = Field(default_factory=list)
    verification: Dict[str, Any] = Field(default_factory=dict)
    trace: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    final_response: Optional[str] = None
    final_answer: Optional[str] = None
    confidence: Optional[float] = 1.0
    warnings: List[str] = Field(default_factory=list)

    # Supervisor control fields.
    retry_counts: Dict[str, int] = Field(default_factory=dict)
    last_failed_step: Optional[str] = None

