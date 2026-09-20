"""Pricing and Availability models."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Price(Base, UUIDMixin):
    """Historical price observation points."""
    __tablename__ = "prices"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False, index=True) # "USD", "INR", "EUR"
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="prices")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant", back_populates="prices")

    __table_args__ = (
        Index("ix_prices_prod_rec", "product_id", "recorded_at"),
        Index("ix_prices_amount_currency", "amount", "currency"),
    )


class Availability(Base, UUIDMixin, TimestampMixin):
    """Stock and inventory availability."""
    __tablename__ = "availabilities"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(String(40), default="in_stock", nullable=False, index=True) # "in_stock", "out_of_stock", "backorder"
    stock_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="availabilities")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant", back_populates="availabilities")
