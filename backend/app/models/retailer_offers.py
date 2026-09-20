"""Retailer offer model mapping canonical products to retailer listings."""

import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Index, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.catalog import Product, ProductVariant


class RetailerOffer(Base, UUIDMixin, TimestampMixin):
    """External retailer offer attached to a canonical product or variant."""
    __tablename__ = "retailer_offers"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True
    )

    retailer: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # "amazon", "flipkart"
    external_product_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True) # ASIN / FSN
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    availability_status: Mapped[str] = mapped_column(
        String(40), default="available", nullable=False, index=True
    ) # "available", "unavailable", "unknown"
    verification_status: Mapped[str] = mapped_column(
        String(40), default="unverified", nullable=False, index=True
    ) # "verified", "unverified", "broken", "not_available"
    last_verified: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Alias for canonical identity
    offer_id = synonym("id")

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="retailer_offers")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant", back_populates="retailer_offers")

    __table_args__ = (
        CheckConstraint("retailer IN ('amazon', 'flipkart')", name="check_retailer_offer_retailer"),
        CheckConstraint("availability_status IN ('available', 'unavailable', 'unknown')", name="check_retailer_offer_availability"),
        CheckConstraint("verification_status IN ('verified', 'unverified', 'broken', 'not_available')", name="check_retailer_offer_verification"),
        Index("ix_retailer_offers_prod_retailer", "product_id", "retailer", "external_product_id"),
    )
