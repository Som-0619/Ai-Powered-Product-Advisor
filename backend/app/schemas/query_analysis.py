"""Pydantic schemas for Query Understanding Agent and LangGraph state."""

import re
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class QueryAnalysis(BaseModel):
    """Structured extraction of user search intent, constraints, and ambiguity."""
    category: Optional[str] = Field(
        default=None,
        description="Broad product or component category (e.g., Laptop, Smartphone, Microcontroller, Sensor, Relay, Module).",
    )
    subcategory: Optional[str] = Field(
        default=None,
        description="Specific subcategory or form factor (e.g., Gaming Laptop, Temperature Sensor, 5V Relay Module, Development Board).",
    )
    budget_min: Optional[float] = Field(
        default=None,
        description="Minimum budget or price constraint if specified, normalized to numeric float.",
    )
    budget_max: Optional[float] = Field(
        default=None,
        description="Maximum budget or upper price limit (e.g. 50000 for 50k, 80000 for 80k).",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Inferred or stated currency (e.g. INR for Indian Rupees / 'k' terms, USD).",
    )
    use_case: Optional[str] = Field(
        default=None,
        description="Primary target use case or workload (e.g., Machine Learning, Gaming, IoT temperature monitoring, Home automation).",
    )
    hard_constraints: List[str] = Field(
        default_factory=list,
        description="Strict non-negotiable specifications (e.g., 'under 80000', '3.3V operating voltage', '5V logic', 'Arduino compatible').",
    )
    soft_preferences: List[str] = Field(
        default_factory=list,
        description="Subjective preferences or nice-to-haves (e.g., 'best performance', 'high battery life', 'fast delivery').",
    )
    brand_preferences: List[str] = Field(
        default_factory=list,
        description="Explicitly mentioned preferred brands (e.g., ASUS, Lenovo, Espressif, Arduino).",
    )
    brand_exclusions: List[str] = Field(
        default_factory=list,
        description="Brands explicitly excluded by the user.",
    )
    language: Literal["en", "hinglish"] = Field(
        default="en",
        description="Detected query language ('en' for English, 'hinglish' for Hindi-English mix).",
    )
    ambiguity: bool = Field(
        default=False,
        description="True if the query is too vague, underspecified, or lacks clear criteria to proceed with product search.",
    )
    intent_type: str = Field(
        default="SEARCH",
        description="Classified query intent: SEARCH, PRODUCT_DETAILS, COMPARISON, RECOMMENDATION, REVIEW, COMPATIBILITY, VISION, RETAILER_SEARCH, GENERAL_CATALOG_QUERY, UNKNOWN.",
    )
    product_mentions: List[str] = Field(
        default_factory=list,
        description="Specific product names, models, or entities mentioned in query.",
    )
    is_follow_up: bool = Field(
        default=False,
        description="Whether this query refers to previous conversational context or products.",
    )
    clarification_question: Optional[str] = Field(
        default=None,
        description="If ambiguity is True, exactly ONE concise clarification question to narrow down user needs. None if query is clear.",
    )

    @model_validator(mode="after")
    def validate_clarification(self) -> "QueryAnalysis":
        """Keep ambiguity output actionable and limited to one question."""
        if self.ambiguity:
            if not self.clarification_question or not self.clarification_question.strip():
                raise ValueError("clarification_question is required when ambiguity is true")
            question = self.clarification_question.strip()
            if question.count("?") != 1 or not question.endswith("?"):
                raise ValueError("clarification_question must contain exactly one question")
            self.clarification_question = question
        else:
            self.clarification_question = None
        return self


class QueryUnderstandingState(BaseModel):
    """LangGraph-compatible state container for query understanding."""
    raw_query: str
    parsed_query: Optional[QueryAnalysis] = None
    clarification_question: Optional[str] = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


def normalize_hinglish_shorthand(text: str) -> str:
    """Normalize common Indian / Hinglish financial shorthand in queries (e.g. 50k -> 50000, 1.5L -> 150000)."""
    # Replace e.g. 50k, 80k, 50K -> 50000, 80000
    text_norm = re.sub(
        r"(?i)\b(\d+(?:\.\d+)?)\s*k\b",
        lambda m: str(int(float(m.group(1)) * 1000)),
        text,
    )
    # Replace e.g. 1.5L, 2 lakh -> 150000, 200000
    text_norm = re.sub(
        r"(?i)\b(\d+(?:\.\d+)?)\s*(?:l|lakh|lac)s?\b",
        lambda m: str(int(float(m.group(1)) * 100000)),
        text_norm,
    )
    return text_norm
