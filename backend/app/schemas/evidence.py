"""Evidence mapping and deterministic verification schemas."""

from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ClaimInput(BaseModel):
    claim_id: str
    claim: str


class EvidenceSource(BaseModel):
    source_id: str
    source_url: str
    evidence_text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_type: Literal["specification", "review", "image", "technical_document", "web"]


class ClaimEvidence(BaseModel):
    claim: str
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    evidence_text: Optional[str] = None
    confidence: float = Field(ge=0, le=1)
    timestamp: Optional[datetime] = None


class UnsupportedClaim(BaseModel):
    claim_id: str
    claim: str
    reason: str


class EvidenceResult(BaseModel):
    evidence: List[ClaimEvidence] = Field(default_factory=list)
    unsupported_claims: List[UnsupportedClaim] = Field(default_factory=list)
    coverage_score: float = Field(ge=0, le=1)


class VerificationFinding(BaseModel):
    check: Literal["budget", "category", "hard_constraints", "compatibility", "unsupported_claims", "contradictions", "source_freshness", "hallucination_risk", "missing_evidence"]
    status: Literal["passed", "failed", "warning"]
    reasoning: str
    claim_ids: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    passed: bool
    evidence_coverage_score: float = Field(ge=0, le=1)
    findings: List[VerificationFinding] = Field(default_factory=list)
    unsupported_claims: List[UnsupportedClaim] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
