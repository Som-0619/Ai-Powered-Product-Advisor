"""Tests for Phase 13 evidence coverage and deterministic critic checks."""

from datetime import datetime, timedelta, timezone

from app.agents.critic import CriticAgent
from app.agents.evidence import EvidenceAgent
from app.schemas.evidence import ClaimEvidence, ClaimInput, EvidenceResult, EvidenceSource
from app.schemas.ranking import RankingResult, ScoreBreakdown


def source(source_id, text, **kwargs):
    return EvidenceSource(source_id=source_id, source_url=f"https://example.test/{source_id}", evidence_text=text, source_type="specification", **kwargs)


def test_supported_claim_is_mapped_to_supplied_source():
    result = EvidenceAgent().map_claims(
        [ClaimInput(claim_id="c1", claim="Laptop has 16 GB RAM")],
        [source("s1", "Specification: Laptop has 16 GB RAM and a 1 TB SSD.")],
    )
    assert result.coverage_score == 1
    assert result.evidence[0].source_id == "s1"
    assert result.evidence[0].evidence_text == "Specification: Laptop has 16 GB RAM and a 1 TB SSD."


def test_unsupported_claim_is_retained_not_silently_removed():
    result = EvidenceAgent().map_claims(
        [ClaimInput(claim_id="c1", claim="Laptop includes a stylus")],
        [source("s1", "Laptop has 16 GB RAM.")],
    )
    assert result.coverage_score == 0
    assert result.unsupported_claims[0].claim_id == "c1"
    verification = CriticAgent().verify(result)
    assert verification.passed is False
    assert any(item.check == "unsupported_claims" for item in verification.findings)


def test_contradictory_sources_fail_verification():
    evidence = EvidenceResult(evidence=[
        ClaimEvidence(claim="Battery capacity", source_id="s1", source_url="u1", evidence_text="Battery capacity is 5000 mAh.", confidence=1, timestamp=datetime.now(timezone.utc)),
        ClaimEvidence(claim="Battery capacity", source_id="s2", source_url="u2", evidence_text="Battery capacity is 6000 mAh.", confidence=1, timestamp=datetime.now(timezone.utc)),
    ], coverage_score=1)
    result = CriticAgent().verify(evidence)
    assert result.passed is False
    assert result.contradictions


def test_budget_violation_fails_verification():
    breakdown = ScoreBreakdown(retrieval_relevance=0, constraint_fit=0, use_case_fit=0, review_quality=0, review_trust=0, compatibility=0, visual_verification=0)
    ranking = RankingResult(product_id="p1", final_score=0, score_breakdown=breakdown, constraint_status="violated", eligible_for_recommendation=False, ranking_reasons=["Budget constraint violated: price 55000 exceeds maximum."])
    result = CriticAgent().verify(EvidenceResult(coverage_score=1), [ranking])
    assert result.passed is False
    assert any(item.check == "budget" and item.status == "failed" for item in result.findings)


def test_missing_evidence_and_stale_sources_are_reported():
    stale = datetime.now(timezone.utc) - timedelta(days=365)
    evidence = EvidenceResult(evidence=[ClaimEvidence(claim="Old claim", source_id="s1", source_url="u", evidence_text="Old claim", confidence=0.6, timestamp=stale)], coverage_score=0.5)
    result = CriticAgent().verify(evidence, max_source_age_days=30)
    assert result.passed is False
    assert {item.check for item in result.findings}.issuperset({"missing_evidence", "source_freshness", "hallucination_risk"})
