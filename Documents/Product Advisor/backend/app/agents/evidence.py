"""Deterministic mapping of recommendation claims to supplied source evidence."""

import re
from typing import Any, Dict, List, Sequence, Set

from app.schemas.evidence import ClaimEvidence, ClaimInput, EvidenceResult, EvidenceSource, UnsupportedClaim

_STOP_WORDS = {"a", "an", "and", "are", "for", "is", "of", "the", "to", "with"}


def _tokens(text: str) -> Set[str]:
    return {token for token in re.findall(r"[a-z0-9.]+", text.lower()) if token not in _STOP_WORDS}


class EvidenceAgent:
    """Maps claims only to text supplied by retrieval, review, vision, or web stages."""

    @staticmethod
    def _best_source(claim: str, sources: Sequence[EvidenceSource]) -> tuple[EvidenceSource | None, float]:
        claim_tokens = _tokens(claim)
        if not claim_tokens:
            return None, 0.0
        best, best_score = None, 0.0
        for source in sources:
            for sentence in re.split(r"(?<=[.!?])\s+", source.evidence_text):
                overlap = len(claim_tokens & _tokens(sentence)) / len(claim_tokens)
                if overlap > best_score:
                    best, best_score = EvidenceSource(
                        source_id=source.source_id, source_url=source.source_url,
                        evidence_text=sentence, timestamp=source.timestamp, source_type=source.source_type,
                    ), overlap
        return best, best_score

    def map_claims(self, claims: Sequence[ClaimInput], sources: Sequence[EvidenceSource]) -> EvidenceResult:
        evidence: List[ClaimEvidence] = []
        unsupported: List[UnsupportedClaim] = []
        for claim in claims:
            source, confidence = self._best_source(claim.claim, sources)
            if source is None or confidence < 0.5:
                evidence.append(ClaimEvidence(claim=claim.claim, confidence=0.0))
                unsupported.append(UnsupportedClaim(claim_id=claim.claim_id, claim=claim.claim, reason="No supplied source has sufficient token overlap."))
                continue
            evidence.append(ClaimEvidence(
                claim=claim.claim, source_id=source.source_id, source_url=source.source_url,
                evidence_text=source.evidence_text, confidence=round(confidence, 3), timestamp=source.timestamp,
            ))
        coverage = sum(item.source_id is not None for item in evidence) / len(claims) if claims else 1.0
        return EvidenceResult(evidence=evidence, unsupported_claims=unsupported, coverage_score=coverage)


async def evidence_node(state: Dict[str, Any]) -> Dict[str, Any]:
    claims = [ClaimInput.model_validate(item) for item in state.get("claims", [])]
    sources = [EvidenceSource.model_validate(item) for item in state.get("evidence_sources", [])]
    return {"evidence": EvidenceAgent().map_claims(claims, sources).model_dump()}
