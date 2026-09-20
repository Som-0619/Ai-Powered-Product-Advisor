"""Pydantic schemas for data ingestion, web crawling, and normalization."""

import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class SourceMetadata(BaseModel):
    """Metadata tracking external crawled sources."""
    source_url: str
    domain: str
    crawl_time: float = Field(default_factory=time.time)
    last_seen: float = Field(default_factory=time.time)
    content_hash: str
    source_type: str = "retailer"  # retailer, distributor, community, manufacturer, datasheet
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0)


class RawCrawlPayload(BaseModel):
    """Raw crawled web content before parsing."""
    url: str
    status_code: int
    content: str
    content_bytes: int
    content_type: str = "text/html"
    headers: Dict[str, str] = Field(default_factory=dict)
    crawl_time: float = Field(default_factory=time.time)
    content_hash: str


class ExtractedSpecification(BaseModel):
    """Raw extracted key-value specification."""
    group: str = "General"
    key: str
    raw_value: str


class ExtractedEntity(BaseModel):
    """Structured entity extracted from raw webpage HTML/JSON-LD."""
    entity_type: str = "product"  # product, component, document, review
    title: str
    brand: Optional[str] = None
    model_number: Optional[str] = None
    sku: Optional[str] = None
    category_name: Optional[str] = None
    description: Optional[str] = None
    specifications: List[ExtractedSpecification] = Field(default_factory=list)
    price: Optional[float] = None
    currency: str = "USD"
    availability: Optional[str] = None
    raw_text: str = ""
    source_metadata: Optional[SourceMetadata] = None


class NormalizedSpecification(BaseModel):
    """Cleaned, unit-standardized specification."""
    group: str
    key: str
    display_value: str
    normalized_value: Optional[float] = None
    unit: Optional[str] = None


class NormalizedEntity(BaseModel):
    """Normalized and PII-redacted entity ready for PostgreSQL and OpenSearch."""
    entity_type: str = "product"  # product, component, document, review
    title: str
    brand: Optional[str] = None
    model_number: Optional[str] = None
    sku: Optional[str] = None
    category_name: str
    description: str
    specifications: List[NormalizedSpecification] = Field(default_factory=list)
    electrical_parameters: Dict[str, Any] = Field(default_factory=dict)
    price: Optional[float] = None
    currency: str = "USD"
    availability: str = "in_stock"
    cleaned_text: str
    content_hash: str
    source_metadata: SourceMetadata


class DeduplicationResult(BaseModel):
    """Result of content hash and canonical URL deduplication check."""
    status: str  # "new", "duplicate_identical", "duplicate_updated"
    content_hash: str
    existing_id: Optional[str] = None
    message: str


class IngestionJobPayload(BaseModel):
    """Payload enqueued in QueueService for async processing."""
    job_id: str
    url: str
    source_type: Optional[str] = None
    retry_count: int = 0
    enqueued_at: float = Field(default_factory=time.time)


class IngestionJobStatus(BaseModel):
    """Current execution status of an ingestion/crawl job."""
    job_id: str
    url: str
    status: str  # "pending", "processing", "completed", "failed"
    attempts: int = 0
    entity_id: Optional[str] = None
    content_hash: Optional[str] = None
    raw_storage_path: Optional[str] = None
    error_message: Optional[str] = None
