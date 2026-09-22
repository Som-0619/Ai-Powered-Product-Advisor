"""Recommendation Agent.

Evaluates candidate products retrieved by SearchAgent against user constraints,
compatibility status, customer reviews, and visual observations.
Uses DeterministicRankingEngine for strict constraint gating and score calculation,
and Qwen 8B for trade-off synthesis and grounded explanations.
Never hallucinates products, prices, or specifications.
"""

import json
import uuid
from typing import Any, Dict, List, Optional, Sequence

from app.agents import tools
from app.core.logging import logger
from app.ranking.engine import DeterministicRankingEngine
from app.schemas.ranking import (
    HardConstraint,
    RankingCandidate,
    RankingConstraints,
    RankingResult,
    RankingWeights,
)
from app.services.factory import get_model_gateway
from app.services.model_gateway import ModelGateway


class RecommendationAgent:
    """Specialist agent responsible for evaluating candidates and producing recommendations."""

    def __init__(self, model_gateway: Optional[ModelGateway] = None):
        self._gateway = model_gateway or get_model_gateway()
        self._engine = DeterministicRankingEngine()

    async def recommend(
        self,
        candidates: Sequence[Dict[str, Any]],
        constraints: Dict[str, Any],
        intent: Optional[Dict[str, Any]] = None,
        review_context: Optional[Dict[str, Any]] = None,
        compatibility_results: Optional[List[Dict[str, Any]]] = None,
        vision_findings: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate candidates, rank them deterministically, and generate reasoned recommendations."""
        req_id = request_id or str(uuid.uuid4())
        intent = intent or {}
        review_context = review_context or {}
        compatibility_results = compatibility_results or []
        vision_findings = vision_findings or []

        if not candidates:
            return {
                "ranked_results": [],
                "recommendations": [],
                "summary": "No matching products were found to evaluate.",
                "confidence": 0.0,
            }

        # Build HardConstraints and RankingConstraints
        hard_constraints: List[HardConstraint] = []
        for hc in constraints.get("hard_constraints", []):
            if isinstance(hc, dict) and "key" in hc and "value" in hc:
                hard_constraints.append(
                    HardConstraint(
                        key=hc["key"],
                        value=hc["value"],
                        operator=hc.get("operator", "eq"),
                    )
                )

        # Only enforce budget_max if user explicitly mentioned budget in query/constraints
        raw_query = str(constraints.get("user_query") or intent.get("user_query") or "").lower()
        has_explicit_budget = any(
            w in raw_query for w in ("under", "budget", "price", "below", "rs", "inr", "$", "k", "max", "cost", "cheaper", "less than")
        ) or any(isinstance(c, str) and any(w in c.lower() for w in ("under", "budget", "price", "below", "rs", "inr", "$", "k")) for c in constraints.get("hard_constraints", []))

        budget_max = constraints.get("budget_max") if has_explicit_budget else None

        ranking_constraints = RankingConstraints(
            category=intent.get("category") or constraints.get("category"),
            budget_max=budget_max,
            hard_constraints=hard_constraints,
        )

        # Compatibility lookup by product_id
        compat_map: Dict[str, str] = {}
        for c in compatibility_results:
            status = c.get("status", "unknown")
            for pid in c.get("part_ids", []):
                compat_map[str(pid)] = status

        # Vision lookup by product_id
        vision_map: Dict[str, float] = {}
        for vf in vision_findings:
            pid = vf.get("product_id")
            if pid:
                obs_conf = [o.get("confidence", 0.5) for o in vf.get("observations", [])]
                vision_map[str(pid)] = sum(obs_conf) / len(obs_conf) if obs_conf else 0.8

        # Build RankingCandidates
        ranking_candidates: List[RankingCandidate] = []
        for c in candidates:
            pid = str(c.get("product_id") or c.get("id") or "")
            if not pid:
                continue

            # Normalized relevance score (0.0 to 1.0)
            raw_rel = float(c.get("relevance_score") or 0.5)
            rel_score = min(max(raw_rel if raw_rel <= 1.0 else raw_rel / 10.0, 0.0), 1.0)

            # Review sentiment / trust from review_context or candidate
            rev_quality = 0.5
            rev_trust = 0.5
            if pid in review_context:
                rc = review_context[pid]
                if rc.get("average_rating"):
                    rev_quality = min(max(float(rc["average_rating"]) / 5.0, 0.0), 1.0)
                if rc.get("reviews_count", 0) > 0:
                    rev_trust = min(float(rc["reviews_count"]) / 10.0, 1.0)

            attrs = dict(c.get("specifications") or {})
            attrs["brand"] = c.get("brand", "")
            attrs["category"] = c.get("category", "")

            ranking_candidates.append(
                RankingCandidate(
                    product_id=pid,
                    category=c.get("category"),
                    price=c.get("price"),
                    is_component=bool(c.get("is_component", False)),
                    attributes=attrs,
                    retrieval_relevance=rel_score,
                    use_case_fit=0.8 if rel_score > 0.4 else 0.5,
                    review_quality=rev_quality,
                    review_trust=rev_trust,
                    compatibility_status=compat_map.get(pid, "unknown"),
                    visual_verification_score=vision_map.get(pid),
                )
            )

        # Deterministic Ranking
        ranked_results = self._engine.rank_candidates(ranking_candidates, ranking_constraints)

        # Map back to enriched candidate info
        cand_map = {str(c.get("product_id") or c.get("id")): c for c in candidates}
        recommendations = []
        eligible_count = 0
        for r in ranked_results:
            if r.eligible_for_recommendation:
                eligible_count += 1
            info = cand_map.get(r.product_id, {})
            recommendations.append({
                "product_id": r.product_id,
                "title": info.get("title") or f"{info.get('brand', '')} {info.get('model', '')}".strip(),
                "brand": info.get("brand", ""),
                "model": info.get("model", ""),
                "category": info.get("category", ""),
                "price": info.get("price"),
                "final_score": r.final_score,
                "eligible": r.eligible_for_recommendation,
                "constraint_status": r.constraint_status,
                "ranking_reasons": r.ranking_reasons,
                "score_breakdown": r.score_breakdown.model_dump(),
                "specifications": info.get("specifications", {}),
                "primary_image_url": info.get("primary_image_url"),
            })

        confidence = round(eligible_count / len(candidates), 2) if candidates else 0.0

        # LLM Reasoning with Qwen 8B for synthesis and comparative explanation
        summary = ""
        top_eligible = [rec for rec in recommendations if rec["eligible"]][:3]
        if top_eligible:
            try:
                prompt = (
                    "Based strictly on the following verified candidate products and their deterministic scores, "
                    "provide a concise comparison and recommendation for the user. "
                    "Do not invent prices, specifications, or features. If data is absent, do not guess.\n\n"
                    f"User Intent: {json.dumps(intent)}\n"
                    f"Constraints: {json.dumps(constraints)}\n"
                    f"Top Candidates:\n{json.dumps(top_eligible, indent=2)}\n"
                )
                system_prompt = (
                    "You are a helpful and truthful electronics recommendation specialist. "
                    "Synthesize the trade-offs concisely based strictly on the retrieved specifications and scores."
                )
                reasoning_resp = await self._gateway.generate_reasoning(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.1,
                    request_id=req_id,
                )
                summary = reasoning_resp.content.strip()
            except Exception as exc:
                logger.warning(f"Qwen reasoning fallback in RecommendationAgent: {exc}")
                top_item = top_eligible[0]
                summary = (
                    f"Recommended: {top_item['title']} "
                    f"(Score: {top_item['final_score']:.2f}). "
                    f"Reasons: {'; '.join(top_item['ranking_reasons'][:2])}."
                )
        else:
            summary = "No candidate products fully satisfied the required budget or technical constraints."

        return {
            "ranked_results": [r.model_dump() for r in ranked_results],
            "recommendations": recommendations,
            "summary": summary,
            "confidence": confidence,
        }


async def recommendation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for RecommendationAgent."""
    agent = RecommendationAgent()
    candidates = state.get("search_results") or state.get("candidates") or []
    constraints = state.get("constraints") or {}
    intent = state.get("intent") or {}
    review_context = state.get("review_context") or {}
    compatibility_results = state.get("compatibility_results") or []
    vision_findings = state.get("visual_findings") or state.get("vision_results") or []
    request_id = state.get("request_id")

    res = await agent.recommend(
        candidates=candidates,
        constraints=constraints,
        intent=intent,
        review_context=review_context,
        compatibility_results=compatibility_results,
        vision_findings=vision_findings,
        request_id=request_id,
    )

    return {
        "ranking_results": res["ranked_results"],
        "recommendation_context": res["recommendations"],
        "final_response": res["summary"],
        "final_answer": res["summary"],
        "confidence": res["confidence"],
    }
