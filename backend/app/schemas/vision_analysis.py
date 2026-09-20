"""Structured visual-verification schemas for shortlisted products and components."""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


VisualStatus = Literal["available", "unavailable", "not_requested"]


class VisionObservation(BaseModel):
    """One observation supported by the supplied image, not a product-text assertion."""
    product_id: Optional[str] = None
    image_id: Optional[str] = None
    view_type: Optional[str] = None
    observation: str
    confidence: float = Field(ge=0.0, le=1.0)
    image_source: str = ""
    related_claim: Optional[str] = None
    agreement: Optional[Union[bool, str]] = None
    disagreement: Optional[Union[bool, str]] = None
    angle: Optional[str] = None
    image_url: Optional[str] = None


class VisualVerificationResult(BaseModel):
    visual_verification_status: VisualStatus
    image_source: str
    observations: List[VisionObservation] = Field(default_factory=list)
    gallery: Optional[Dict[str, str]] = None
    error: Optional[str] = None
