"""Catalog schemas for Category, Brand, Product, Variant, and Specification."""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    category_type: str = "consumer_electronics"
    parent_id: Optional[uuid.UUID] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BrandBase(BaseModel):
    name: str
    slug: str
    website: Optional[str] = None
    country: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandRead(BrandBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SpecificationBase(BaseModel):
    spec_group: str
    key: str
    value: str
    raw_value: Optional[Dict[str, Any]] = None


class SpecificationCreate(SpecificationBase):
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None


class SpecificationRead(SpecificationBase):
    id: uuid.UUID
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductVariantBase(BaseModel):
    sku: str
    title: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ProductVariantCreate(ProductVariantBase):
    product_id: uuid.UUID


class ProductVariantRead(ProductVariantBase):
    id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    model_number: Optional[str] = None
    sku: Optional[str] = None
    status: str = "active"
    is_component: bool = False
    category_id: uuid.UUID
    brand_id: Optional[uuid.UUID] = None


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProductDetail(ProductRead):
    category: Optional[CategoryRead] = None
    brand: Optional[BrandRead] = None
    variants: List[ProductVariantRead] = Field(default_factory=list)
    specifications: List[SpecificationRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
