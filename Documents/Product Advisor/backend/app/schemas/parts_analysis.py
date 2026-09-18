"""Structured parts extraction and compatibility models for Phase 10."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

CompatibilityStatus = Literal["compatible", "possibly_compatible", "incompatible", "unknown"]
PowerRole = Literal["supply", "load", "bidirectional", "unknown"]


class PartInput(BaseModel):
    """Trusted source material for a part; source text is never generated."""
    part_id: str
    source_text: str
    manufacturer: Optional[str] = None
    part_number: Optional[str] = None
    power_role: PowerRole = "unknown"


class PartEvidence(BaseModel):
    field: str
    value: str
    method: Literal["deterministic", "model"]


class PartSpecification(BaseModel):
    part_id: str
    manufacturer: Optional[str] = None
    part_number: Optional[str] = None
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None
    current_min: Optional[float] = None
    current_max: Optional[float] = None
    resistance_ohms: Optional[float] = None
    capacitance_farads: Optional[float] = None
    power_watts: Optional[float] = None
    tolerance_percent: Optional[float] = None
    interfaces: List[str] = Field(default_factory=list)
    protocols: List[str] = Field(default_factory=list)
    connector: Optional[str] = None
    package: Optional[str] = None
    dimensions_mm: List[float] = Field(default_factory=list)
    frequency_hz: Optional[float] = None
    temperature_min_c: Optional[float] = None
    temperature_max_c: Optional[float] = None
    power_role: PowerRole = "unknown"
    i2c_address: Optional[int] = None
    evidence: List[PartEvidence] = Field(default_factory=list)


class CompatibilityEvidence(BaseModel):
    check: Literal["voltage", "current", "interface", "protocol", "connector", "form_factor", "power", "operating_conditions", "i2c_address", "reasoning"]
    status: CompatibilityStatus
    reasoning: str
    part_ids: List[str] = Field(min_length=1)
    deterministic: bool = True


class CompatibilityResult(BaseModel):
    status: CompatibilityStatus
    part_ids: List[str] = Field(min_length=2)
    evidence: List[CompatibilityEvidence] = Field(min_length=1)
    reasoning: str
    requires_further_validation: bool = False
