"""Vision-only agent for visual verification of already shortlisted items."""

import json
import re
import uuid
from typing import Any, Dict, List, Optional, Sequence

from pydantic import TypeAdapter

from app.core.exceptions import ModelUnavailableError
from app.core.logging import logger
from app.schemas.vision_analysis import VisionObservation, VisualVerificationResult
from app.services.factory import get_model_gateway
from app.services.model_gateway import ModelGateway

_SYSTEM_PROMPT = """You are a visual-verification assistant. Inspect only the supplied image. Report only ports, connectors, keypad, screen, accessories, board layout, or visible markings that are actually visible. Never infer hidden objects or specifications. For each observation, provide confidence from 0 to 1. Compare a claim only when the image provides evidence; otherwise leave agreement and disagreement null. Return JSON only: a list of observations with observation, confidence, related_claim, agreement, disagreement."""
_OBSERVATIONS = TypeAdapter(List[VisionObservation])


class VisionAgent:
    """Uses the configured vision route through ModelGateway, never a text model."""

    def __init__(self, model_gateway: Optional[ModelGateway] = None):
        self._gateway = model_gateway or get_model_gateway()

    @staticmethod
    def _parse_observations(content: str, image_source: str, claims: Sequence[str]) -> List[VisionObservation]:
        """Validate vision JSON and discard unsupported claim references."""
        match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```|(\[.*\])", content, re.DOTALL)
        if not match:
            return []
        try:
            observations = _OBSERVATIONS.validate_python(json.loads(match.group(1) or match.group(2)))
        except (json.JSONDecodeError, ValueError):
            return []
        allowed_claims = set(claims)
        safe: List[VisionObservation] = []
        for item in observations:
            item.image_source = image_source
            if item.related_claim not in allowed_claims:
                item.related_claim = None
                item.agreement = None
                item.disagreement = None
            safe.append(item)
        return safe

    async def analyze_image(
        self,
        image_bytes: bytes,
        image_source: str,
        related_claims: Optional[Sequence[str]] = None,
        shortlisted: bool = True,
        request_id: Optional[str] = None,
        product_id: Optional[str] = None,
        image_product_id: Optional[str] = None,
        image_id: Optional[str] = None,
        view_type: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> VisualVerificationResult:
        """Analyze only a shortlisted image belonging strictly to candidate product."""
        if not shortlisted:
            return VisualVerificationResult(
                visual_verification_status="not_requested", image_source=image_source
            )
        # Strict Image Identity Validation: image.product_id == candidate.product_id
        if product_id and image_product_id and str(product_id) != str(image_product_id):
            logger.warning(
                "Image rejected: product_id mismatch",
                extra={"candidate_product_id": product_id, "image_product_id": image_product_id}
            )
            return VisualVerificationResult(
                visual_verification_status="unavailable",
                image_source=image_source,
                error="Image product_id mismatch: cross-product image rejected.",
            )
        if not image_bytes:
            return VisualVerificationResult(
                visual_verification_status="unavailable",
                image_source=image_source,
                error="No shortlisted image supplied.",
            )
        claims = list(related_claims or [])
        prompt = f"Inspect this shortlisted {view_type or 'product'} image for {product_id or 'product'}. Candidate claims: " + json.dumps(claims)
        try:
            response = await self._gateway.generate_with_image(
                prompt=prompt,
                image_bytes=image_bytes,
                system_prompt=_SYSTEM_PROMPT,
                temperature=0.0,
                request_id=request_id or str(uuid.uuid4()),
            )
            parsed_obs = self._parse_observations(response.content, image_source, claims)
            for obs in parsed_obs:
                obs.product_id = product_id
                obs.image_id = image_id or f"IMG-{product_id or 'PROD'}-{(view_type or 'VIEW').upper()}"
                obs.view_type = view_type
                obs.angle = view_type
                obs.image_url = image_url
            return VisualVerificationResult(
                visual_verification_status="available",
                image_source=image_source,
                observations=parsed_obs,
            )
        except ModelUnavailableError as exc:
            logger.warning("Vision model unavailable", extra={"error": str(exc)})
            return VisualVerificationResult(
                visual_verification_status="unavailable", image_source=image_source, error=str(exc)
            )
        except Exception as exc:
            logger.error("Vision analysis failed", extra={"error": str(exc)})
            return VisualVerificationResult(
                visual_verification_status="unavailable", image_source=image_source, error=str(exc)
            )


async def vision_node(state: Dict[str, Any], model_gateway: Optional[ModelGateway] = None) -> Dict[str, Any]:
    """Supervisor-compatible node for a preselected image; enforces Image Safety Rule via tool layer."""
    from app.agents import tools

    image_bytes = state.get("image_bytes")
    image_source = state.get("image_source", "")

    # If raw image bytes are directly supplied in state, use agent directly
    if image_bytes:
        result = await VisionAgent(model_gateway).analyze_image(
            image_bytes=image_bytes,
            image_source=image_source,
            related_claims=state.get("related_claims", []),
            shortlisted=bool(state.get("shortlisted", False)),
            request_id=state.get("request_id"),
        )
        return {
            "vision_results": [result.model_dump()],
            "visual_findings": [result.model_dump()],
            "vision_context": {"status": result.visual_verification_status, "observations": [o.model_dump() for o in result.observations]},
        }

    # Otherwise, resolve candidate product from state
    product_id = state.get("product_id")
    if not product_id and state.get("selected_products"):
        product_id = state["selected_products"][0]
    elif not product_id and state.get("search_results"):
        product_id = state["search_results"][0].get("product_id")
    elif not product_id and state.get("candidates"):
        product_id = state["candidates"][0].get("product_id") or state["candidates"][0].get("id")

    if not product_id:
        result = VisualVerificationResult(
            visual_verification_status="unavailable",
            image_source=image_source,
            error="No shortlisted image supplied.",
        )
        return {
            "vision_results": [result.model_dump()],
            "visual_findings": [],
            "vision_context": {"status": "unavailable", "observations": []},
        }

    # Enforce Image Safety Rule via tools.analyze_product_image
    image_id = state.get("image_id")
    claims = state.get("related_claims") or state.get("claims") or []
    if isinstance(claims, list) and claims and isinstance(claims[0], dict):
        claims = [c.get("claim") for c in claims if c.get("claim")]

    tool_res = await tools.analyze_product_image(
        product_id=product_id,
        image_id=image_id,
        claims=claims,
    )

    if tool_res.get("status") == "error":
        result = VisualVerificationResult(
            visual_verification_status="unavailable",
            image_source=tool_res.get("image_url", ""),
            error=tool_res.get("message", "Image analysis failed"),
        )
        return {
            "vision_results": [result.model_dump()],
            "visual_findings": [tool_res],
            "vision_context": {"status": "unavailable", "error": tool_res.get("message")},
            "warnings": [f"Vision warning for product {product_id}: {tool_res.get('message')}"],
        }

    obs_list = tool_res.get("observations", [])
    result = VisualVerificationResult(
        visual_verification_status="available",
        image_source=tool_res.get("image_url", ""),
    )
    return {
        "vision_results": [result.model_dump()],
        "visual_findings": [tool_res],
        "vision_context": {
            "status": "available",
            "product_id": str(product_id),
            "image_id": tool_res.get("image_id"),
            "image_url": tool_res.get("image_url"),
            "observations": obs_list,
        },
    }

