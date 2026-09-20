"""Normalized Pydantic v2 schemas for search requests, filters, and responses."""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    """Normalized individual search result."""

    id: str = Field(..., description="Unique document ID in the index")
    score: float = Field(..., description="Relevance / similarity score")
    index: str = Field(..., description="Source OpenSearch index name")
    source: Dict[str, Any] = Field(default_factory=dict, description="Original indexed document payload")
    highlights: Optional[Dict[str, List[str]]] = Field(
        default=None, description="Matched snippets with highlight markers"
    )


class SearchResponse(BaseModel):
    """Standardized search response across all query modes."""

    total: int = Field(..., description="Total matching documents count")
    hits: List[SearchHit] = Field(default_factory=list, description="Ranked list of hits")
    search_mode: Literal["keyword", "vector", "hybrid"] = Field(
        ..., description="Search mode executed"
    )
    latency_ms: float = Field(..., description="Query execution latency in milliseconds")


class SearchFilters(BaseModel):
    """Generic query filter options."""

    custom_filters: Dict[str, Any] = Field(default_factory=dict)


class ProductFilters(BaseModel):
    """Filter parameters for product searches."""

    category: Optional[str] = Field(None, description="Category slug or name")
    subcategory: Optional[str] = Field(None, description="Subcategory slug or name")
    brand: Optional[str] = Field(None, description="Brand name or slug")
    min_price: Optional[float] = Field(None, ge=0.0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0.0, description="Maximum price")
    is_component: Optional[bool] = Field(None, description="True for components, False for consumer")


class ComponentFilters(BaseModel):
    """Filter parameters for electronic component searches."""

    component_type: Optional[str] = Field(None, description="Component category (mcus, sensors, etc.)")
    min_voltage: Optional[float] = Field(None, description="Minimum operating voltage")
    max_voltage: Optional[float] = Field(None, description="Maximum operating voltage")
    max_current: Optional[float] = Field(None, description="Maximum current draw")
    package_type: Optional[str] = Field(None, description="Physical package or footprint")
    interface: Optional[str] = Field(None, description="Communication interface (I2C, SPI, UART)")
    mounting_type: Optional[str] = Field(None, description="Surface Mount, Through-Hole, etc.")


class ReviewFilters(BaseModel):
    """Filter parameters for review retrieval."""

    product_id: Optional[str] = Field(None, description="Filter reviews for specific product ID")
    min_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Minimum star rating")
    sentiment: Optional[str] = Field(None, description="positive, neutral, or negative")
    verified_only: Optional[bool] = Field(None, description="Only verified purchase reviews")
    max_fraud_score: Optional[float] = Field(
        0.5, ge=0.0, le=1.0, description="Threshold above which reviews are excluded as spam"
    )


class DocumentFilters(BaseModel):
    """Filter parameters for technical document retrieval."""

    product_id: Optional[str] = Field(None, description="Product ID associated with the document")
    doc_type: Optional[str] = Field(None, description="Document type (datasheet, manual, schematic)")
