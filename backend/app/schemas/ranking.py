"""Deterministic ranking input, configuration, and result schemas."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

ConstraintStatus = Literal["satisfied", "violated"]
CompatibilityStatus = Literal["compatible", "possibly_compatible", "incompatible", "unknown"]


class HardConstraint(BaseModel):
    key: str
    value: Any
    operator: Literal["eq", "gte", "lte", "contains"] = "eq"


class RankingConstraints(BaseModel):
    category: Optional[str] = None
    budget_max: Optional[float] = Field(default=None, ge=0)
    budget_min: Optional[float] = Field(default=None, ge=0)
    hard_constraints: List[HardConstraint] = Field(default_factory=list)


class RankingCandidate(BaseModel):
    product_id: str
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    is_component: bool = False
    attributes: Dict[str, Any] = Field(default_factory=dict)
    retrieval_relevance: float = Field(default=0.0, ge=0, le=1)
    use_case_fit: float = Field(default=0.0, ge=0, le=1)
    review_quality: float = Field(default=0.0, ge=0, le=1)
    review_trust: float = Field(default=0.0, ge=0, le=1)
    compatibility_status: CompatibilityStatus = "unknown"
    visual_verification_score: Optional[float] = Field(default=None, ge=0, le=1)


class RankingWeights(BaseModel):
    retrieval_relevance: float = Field(default=0.25, ge=0)
    constraint_fit: float = Field(default=0.25, ge=0)
    use_case_fit: float = Field(default=0.15, ge=0)
    review_quality: float = Field(default=0.12, ge=0)
    review_trust: float = Field(default=0.08, ge=0)
    compatibility: float = Field(default=0.10, ge=0)
    visual_verification: float = Field(default=0.05, ge=0)

    @model_validator(mode="after")
    def has_positive_weight(self) -> "RankingWeights":
        if sum(self.model_dump().values()) <= 0:
            raise ValueError("At least one ranking weight must be positive")
        return self


class ScoreBreakdown(BaseModel):
    retrieval_relevance: float
    constraint_fit: float
    use_case_fit: float
    review_quality: float
    review_trust: float
    compatibility: float
    visual_verification: float


class RankingResult(BaseModel):
    product_id: str
    final_score: float = Field(ge=0, le=1)
    score_breakdown: ScoreBreakdown
    constraint_status: ConstraintStatus
    eligible_for_recommendation: bool
    ranking_reasons: List[str] = Field(default_factory=list)
