"""Schemas for Reviewer and Review."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ReviewerBase(BaseModel):
    name: Optional[str] = None
    external_id: Optional[str] = None
    is_verified: bool = False
    trust_score: float = 1.0
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class ReviewerCreate(ReviewerBase):
    pass


class ReviewerRead(ReviewerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReviewBase(BaseModel):
    product_id: uuid.UUID
    reviewer_id: Optional[uuid.UUID] = None
    source_id: Optional[uuid.UUID] = None
    rating: Optional[float] = None
    title: Optional[str] = None
    body: str
    sentiment: Optional[str] = None
    use_case: Optional[str] = None
    is_verified_purchase: bool = False
    fraud_score: float = 0.0
    attributes_analyzed: Dict[str, Any] = Field(default_factory=dict)
    reviewed_at: Optional[datetime] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    reviewer: Optional[ReviewerRead] = None
    model_config = ConfigDict(from_attributes=True)
