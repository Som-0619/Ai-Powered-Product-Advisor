"""Schemas for Price and Availability."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PriceBase(BaseModel):
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    source_id: uuid.UUID
    amount: float
    currency: str = "USD"


class PriceCreate(PriceBase):
    pass


class PriceRead(PriceBase):
    id: uuid.UUID
    recorded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AvailabilityBase(BaseModel):
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    source_id: uuid.UUID
    status: str = "in_stock"
    stock_quantity: Optional[int] = None


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityRead(AvailabilityBase):
    id: uuid.UUID
    last_checked_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
