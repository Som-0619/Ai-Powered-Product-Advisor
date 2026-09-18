"""Schemas for CompatibilityRule and ProductRelationship."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CompatibilityRuleBase(BaseModel):
    category_a_id: Optional[uuid.UUID] = None
    category_b_id: Optional[uuid.UUID] = None
    rule_type: str
    parameter_key: str
    operator: str
    description: str


class CompatibilityRuleCreate(CompatibilityRuleBase):
    pass


class CompatibilityRuleRead(CompatibilityRuleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductRelationshipBase(BaseModel):
    product_a_id: uuid.UUID
    product_b_id: uuid.UUID
    relationship_type: str
    confidence: float = 1.0
    evidence: Optional[str] = None


class ProductRelationshipCreate(ProductRelationshipBase):
    pass


class ProductRelationshipRead(ProductRelationshipBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
