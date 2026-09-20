"""Unit tests for deterministic Phase 12 ranking."""

from app.ranking.engine import DeterministicRankingEngine
from app.schemas.ranking import HardConstraint, RankingCandidate, RankingConstraints, RankingWeights


def candidate(product_id="p1", **kwargs):
    payload = {
        "product_id": product_id, "category": "Laptop", "price": 49000,
        "retrieval_relevance": 0.8, "use_case_fit": 0.8, "review_quality": 0.8,
        "review_trust": 0.8, "compatibility_status": "compatible",
        "visual_verification_score": 0.8,
    }
    payload.update(kwargs)
    return RankingCandidate(**payload)


def test_budget_is_a_mandatory_gate():
    result = DeterministicRankingEngine().rank_candidate(candidate(price=55000), RankingConstraints(budget_max=50000))
    assert result.constraint_status == "violated"
    assert result.eligible_for_recommendation is False
    assert result.final_score == 0


def test_category_is_a_mandatory_gate():
    result = DeterministicRankingEngine().rank_candidate(candidate(category="Phone"), RankingConstraints(category="Laptop"))
    assert result.eligible_for_recommendation is False
    assert "Category constraint violated" in result.ranking_reasons[0]


def test_declared_hard_constraint_is_a_mandatory_gate():
    result = DeterministicRankingEngine().rank_candidate(
        candidate(attributes={"ram_gb": 8}),
        RankingConstraints(hard_constraints=[HardConstraint(key="ram_gb", operator="gte", value=16)]),
    )
    assert result.constraint_status == "violated"


def test_incompatible_component_is_not_recommendable():
    result = DeterministicRankingEngine().rank_candidate(
        candidate(is_component=True, compatibility_status="incompatible"), RankingConstraints()
    )
    assert result.eligible_for_recommendation is False
    assert result.score_breakdown.compatibility == 0


def test_ranking_uses_configurable_weights():
    engine = DeterministicRankingEngine(RankingWeights(retrieval_relevance=1, constraint_fit=0, use_case_fit=0, review_quality=0, review_trust=0, compatibility=0, visual_verification=0))
    result = engine.rank_candidate(candidate(retrieval_relevance=0.73), RankingConstraints())
    assert result.final_score == 0.73


def test_ties_are_resolved_by_product_id():
    engine = DeterministicRankingEngine()
    results = engine.rank_candidates([candidate("b"), candidate("a")], RankingConstraints())
    assert [result.product_id for result in results] == ["a", "b"]
