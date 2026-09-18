"""Deterministic critic for recommendation constraints and evidence coverage."""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence

from app.schemas.evidence import EvidenceResult, VerificationFinding, VerificationResult
from app.schemas.ranking import RankingResult


class CriticAgent:
    """Makes verification failures explicit for supervisor retry/replan handling."""

    @staticmethod
    def _contradictions(evidence: EvidenceResult) -> List[str]:
        grouped: Dict[str, List[str]] = {}
        for item in evidence.evidence:
            grouped.setdefault(item.claim, []).append(item.evidence_text or "")
        contradictions = []
        for claim, texts in grouped.items():
            numbers = {number for text in texts for number in re.findall(r"\d+(?:\.\d+)?", text)}
            if len(texts) > 1 and len(numbers) > 1:
                contradictions.append(f"Conflicting numeric evidence for claim: {claim}")
        return contradictions

    def verify(
        self,
        evidence: EvidenceResult,
        ranking_results: Sequence[RankingResult] = (),
        compatibility_statuses: Sequence[str] = (),
        max_source_age_days: int = 180,
        now: datetime | None = None,
    ) -> VerificationResult:
        now = now or datetime.now(timezone.utc)
        findings: List[VerificationFinding] = []
        failed = False
        violations = [r for r in ranking_results if r.constraint_status == "violated"]
        if violations:
            failed = True
            for r in violations:
                reasons = " ".join(r.ranking_reasons)
                check_name = "budget" if "budget" in reasons.lower() else "hard_constraints"
                findings.append(VerificationFinding(
                    check=check_name,
                    status="failed",
                    reasoning=f"Candidate {r.product_id} violated mandatory constraints: {reasons or 'constraint gating failure'}",
                ))
        else:
            findings.append(VerificationFinding(
                check="hard_constraints",
                status="passed",
                reasoning="All recommended candidate products strictly satisfy budget parameters, category isolation, and mandatory hardware gates.",
            ))

        if max_source_age_days and any(
            item.timestamp and (now - item.timestamp).days > max_source_age_days
            for item in evidence.evidence
        ):
            failed = True
            findings.append(VerificationFinding(
                check="source_freshness",
                status="failed",
                reasoning=f"Source timestamp exceeds maximum allowable age of {max_source_age_days} days.",
            ))

        if evidence.coverage_score < 0.7:
            failed = True
            findings.append(VerificationFinding(
                check="missing_evidence",
                status="failed",
                reasoning=f"Evidence coverage score ({evidence.coverage_score:.2f}) is below threshold.",
            ))

        if any(status == "incompatible" for status in compatibility_statuses):
            failed = True
            findings.append(VerificationFinding(check="compatibility", status="failed", reasoning="A component compatibility check failed due to voltage or protocol mismatch."))
        elif compatibility_statuses:
            findings.append(VerificationFinding(check="compatibility", status="passed", reasoning="Component electrical ratings, logic levels, and communication protocols verified."))

        if evidence.unsupported_claims:
            failed = True
            findings.append(VerificationFinding(check="unsupported_claims", status="failed", reasoning="Some claims lacked grounded datasheet support.", claim_ids=[item.claim_id for item in evidence.unsupported_claims]))
        else:
            findings.append(VerificationFinding(check="unsupported_claims", status="passed", reasoning="Product specifications and technical claims are grounded in official product datasheets."))

        contradictions = self._contradictions(evidence)
        if contradictions:
            failed = True
            findings.append(VerificationFinding(check="contradictions", status="failed", reasoning="; ".join(contradictions)))

        if any(item.confidence <= 0.6 for item in evidence.evidence):
            findings.append(VerificationFinding(check="hallucination_risk", status="warning", reasoning="Some claims have lower evidence overlap confidence."))

        return VerificationResult(
            passed=not failed,
            evidence_coverage_score=evidence.coverage_score,
            findings=findings,
            unsupported_claims=evidence.unsupported_claims,
            contradictions=contradictions,
        )


async def critic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    evidence = EvidenceResult.model_validate(state.get("evidence", {}))
    rankings = [RankingResult.model_validate(item) for item in state.get("ranking_results", [])]
    verification = CriticAgent().verify(evidence, rankings, state.get("compatibility_statuses", []))
    return {"verification": verification.model_dump()}
