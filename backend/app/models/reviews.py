"""Review models: Reviewer and Review."""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from app.models.base import Base, UUIDMixin, TimestampMixin


class Reviewer(Base, UUIDMixin, TimestampMixin):
    """Review author profile with trust metrics."""
    __tablename__ = "reviewers"

    name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, unique=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trust_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    reviews: Mapped[List["ProductReview"]] = relationship("ProductReview", back_populates="reviewer")


class ProductReview(Base, UUIDMixin, TimestampMixin):
    """Canonical customer or expert review record with trust and provenance metrics."""
    __tablename__ = "product_reviews"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviewers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True
    )

    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True) # "positive", "neutral", "negative"
    use_case: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True) # e.g. "Gaming", "Coding", "Robotics"
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fraud_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)          # 0.0 (clean) to 1.0 (suspected fake/burst)
    attributes_analyzed: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Canonical synonyms matching Section 8 requirements
    review_id = synonym("id")
    content = synonym("body")
    verified_purchase = synonym("is_verified_purchase")

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    reviewer: Mapped[Optional["Reviewer"]] = relationship("Reviewer", back_populates="reviews")
    source_rel: Mapped[Optional["Source"]] = relationship("Source", back_populates="reviews")

    __table_args__ = (
        Index("ix_product_reviews_product_rating", "product_id", "rating"),
        Index("ix_product_reviews_fraud_score", "fraud_score"),
    )


# Backward-compatible alias
Review = ProductReview
