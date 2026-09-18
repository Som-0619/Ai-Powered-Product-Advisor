"""Schemas for Electronic Components and Electrical Specifications."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ComponentSpecificationBase(BaseModel):
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None
    voltage_unit: str = "V"
    current_min: Optional[float] = None
    current_max: Optional[float] = None
    current_unit: str = "A"
    resistance: Optional[float] = None
    resistance_unit: Optional[str] = None
    capacitance: Optional[float] = None
    capacitance_unit: Optional[str] = None
    power: Optional[float] = None
    power_unit: Optional[str] = None
    tolerance: Optional[str] = None
    interface: Optional[str] = None
    package: Optional[str] = None
    frequency: Optional[float] = None
    frequency_unit: Optional[str] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    extra_specs: Dict[str, Any] = Field(default_factory=dict)


class ComponentSpecificationCreate(ComponentSpecificationBase):
    component_id: uuid.UUID


class ComponentSpecificationRead(ComponentSpecificationBase):
    id: uuid.UUID
    component_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ComponentBase(BaseModel):
    part_number: str
    package_type: Optional[str] = None
    pin_count: Optional[int] = None
    mounting_type: Optional[str] = None
    lifecycle_status: str = "active"
    datasheet_url: Optional[str] = None


class ComponentCreate(ComponentBase):
    product_id: uuid.UUID


class ComponentRead(ComponentBase):
    id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    specification: Optional[ComponentSpecificationRead] = None
    model_config = ConfigDict(from_attributes=True)
