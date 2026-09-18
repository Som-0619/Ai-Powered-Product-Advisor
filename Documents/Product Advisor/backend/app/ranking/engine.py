"""Pure deterministic product and component ranking engine."""

from typing import Any, Dict, Iterable, List, Tuple

from app.schemas.ranking import (
    HardConstraint,
    RankingCandidate,
    RankingConstraints,
    RankingResult,
    RankingWeights,
    ScoreBreakdown,
)


class DeterministicRankingEngine:
    """Applies mandatory gates before configurable, normalized weighted scoring."""

    def __init__(self, weights: RankingWeights | None = None):
        self.weights = weights or RankingWeights()

    @staticmethod
    def _compatibility_score(status: str) -> float:
        return {"compatible": 1.0, "possibly_compatible": 0.6, "unknown": 0.3, "incompatible": 0.0}[status]

    @staticmethod
    def _matches_constraint(candidate: RankingCandidate, constraint: HardConstraint) -> bool:
        value = candidate.attributes.get(constraint.key)
        if value is None and hasattr(candidate, constraint.key):
            value = getattr(candidate, constraint.key)
        if value is None:
            return False
        required = constraint.value
        if constraint.operator == "eq":
            return str(value).lower() == str(required).lower()
        if constraint.operator == "gte":
            return float(value) >= float(required)
        if constraint.operator == "lte":
            return float(value) <= float(required)
        if constraint.operator == "contains":
            return str(required).lower() in {str(item).lower() for item in value} if isinstance(value, (list, tuple, set)) else str(required).lower() in str(value).lower()
        return False

    def _evaluate_gates(self, candidate: RankingCandidate, constraints: RankingConstraints) -> Tuple[bool, List[str]]:
        reasons: List[str] = []
        if constraints.budget_max is not None and (candidate.price is None or candidate.price > constraints.budget_max):
            price = "unknown" if candidate.price is None else f"{candidate.price:g}"
            reasons.append(f"Budget constraint violated: price {price} exceeds or lacks the maximum {constraints.budget_max:g}.")
        if constraints.category:
            c_cat = " ".join((candidate.category or "").lower().replace("-", " ").replace("&", " ").split())
            req_cat = " ".join(constraints.category.lower().replace("-", " ").replace("&", " ").split())
            c_words = set(c_cat.split())
            req_words = set(req_cat.split())
            # Allow match if either string contains the other (e.g. 'laptop' in 'laptops ultrabooks')
            # or if primary category words overlap
            if req_cat not in c_cat and c_cat not in req_cat and not (c_words & req_words):
                reasons.append(f"Category constraint violated: expected {constraints.category}.")
        for constraint in constraints.hard_constraints:
            if not self._matches_constraint(candidate, constraint):
                reasons.append(f"Hard constraint violated: {constraint.key} {constraint.operator} {constraint.value}.")
        if candidate.is_component and candidate.compatibility_status == "incompatible":
            reasons.append("Component compatibility constraint violated: deterministic compatibility result is incompatible.")
        return not reasons, reasons

    def rank_candidate(self, candidate: RankingCandidate, constraints: RankingConstraints) -> RankingResult:
        """Gate a candidate, then calculate its score with no LLM or nondeterministic work."""
        eligible, reasons = self._evaluate_gates(candidate, constraints)
        compatibility = self._compatibility_score(candidate.compatibility_status)
        visual = candidate.visual_verification_score if candidate.visual_verification_score is not None else 0.5
        breakdown = ScoreBreakdown(
            retrieval_relevance=candidate.retrieval_relevance,
            constraint_fit=1.0 if eligible else 0.0,
            use_case_fit=candidate.use_case_fit,
            review_quality=candidate.review_quality,
            review_trust=candidate.review_trust,
            compatibility=compatibility,
            visual_verification=visual,
        )
        if not eligible:
            return RankingResult(
                product_id=candidate.product_id, final_score=0.0, score_breakdown=breakdown,
                constraint_status="violated", eligible_for_recommendation=False,
                ranking_reasons=reasons,
            )
        values = breakdown.model_dump()
        weights = self.weights.model_dump()
        final_score = sum(values[key] * weights[key] for key in values) / sum(weights.values())
        reasons.extend([
            "All mandatory constraints are satisfied.",
            f"Retrieval relevance: {candidate.retrieval_relevance:.2f}.",
            f"Compatibility status: {candidate.compatibility_status}.",
        ])
        return RankingResult(
            product_id=candidate.product_id, final_score=round(final_score, 6), score_breakdown=breakdown,
            constraint_status="satisfied", eligible_for_recommendation=True, ranking_reasons=reasons,
        )

    def rank_candidates(self, candidates: Iterable[RankingCandidate], constraints: RankingConstraints) -> List[RankingResult]:
        """Sort by eligibility, score, then product ID to resolve ties deterministically."""
        ranked = [self.rank_candidate(candidate, constraints) for candidate in candidates]
        return sorted(ranked, key=lambda result: (not result.eligible_for_recommendation, -result.final_score, result.product_id))


async def ranking_node(state: Dict[str, Any], weights: RankingWeights | None = None) -> Dict[str, Any]:
    """Supervisor-compatible deterministic ranking node with no external calls."""
    candidates = [RankingCandidate.model_validate(item) for item in state.get("candidates", [])]
    constraints = RankingConstraints.model_validate(state.get("ranking_constraints", {}))
    results = DeterministicRankingEngine(weights).rank_candidates(candidates, constraints)
    return {"ranking_results": [result.model_dump() for result in results]}
