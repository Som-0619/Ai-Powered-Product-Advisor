"""Source, ProductSource, and CrawlJob models."""

import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Source(Base, UUIDMixin, TimestampMixin):
    """External data, retail, or distributor source."""
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(50), default="retailer", nullable=False, index=True
    )  # "retailer", "distributor", "community", "manufacturer"
    trust_rating: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    product_sources: Mapped[List["ProductSource"]] = relationship("ProductSource", back_populates="source", cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="source")
    crawl_jobs: Mapped[List["CrawlJob"]] = relationship("CrawlJob", back_populates="source")


class ProductSource(Base, UUIDMixin, TimestampMixin):
    """Junction mapping products to their external crawled sources."""
    __tablename__ = "product_sources"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    external_sku: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    crawl_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="sources")
    source: Mapped["Source"] = relationship("Source", back_populates="product_sources")

    __table_args__ = (
        Index("ix_product_sources_prod_source", "product_id", "source_id", unique=True),
    )


class CrawlJob(Base, UUIDMixin, TimestampMixin):
    """Asynchronous web crawl execution log."""
    __tablename__ = "crawl_jobs"

    url: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True) # "pending", "processing", "completed", "failed"
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True) # MinIO/S3 raw HTML/payload key

    # Relationships
    source: Mapped[Optional["Source"]] = relationship("Source", back_populates="crawl_jobs")
