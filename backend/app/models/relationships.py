"""CompatibilityRule and ProductRelationship models."""

import uuid
from typing import Optional
from sqlalchemy import String, Text, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class CompatibilityRule(Base, UUIDMixin, TimestampMixin):
    """Deterministic rule governing compatibility between product/component categories."""
    __tablename__ = "compatibility_rules"

    category_a_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True
    )
    category_b_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True
    )

    rule_type: Mapped[str] = mapped_column(
        String(60), nullable=False, index=True
    )  # "voltage_match", "interface_match", "form_factor", "socket_match", "power_budget"
    parameter_key: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "operating_voltage", "socket", "ram_type"
    operator: Mapped[str] = mapped_column(String(30), nullable=False)      # "eq", "lte", "gte", "contains", "compatible_range"
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    category_a: Mapped[Optional["Category"]] = relationship("Category", foreign_keys=[category_a_id])
    category_b: Mapped[Optional["Category"]] = relationship("Category", foreign_keys=[category_b_id])


class ProductRelationship(Base, UUIDMixin, TimestampMixin):
    """Direct relationship between two products/components (compatibility, accessory, alternative)."""
    __tablename__ = "product_relationships"

    product_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # "compatible", "incompatible", "accessory", "alternative", "upgrade"
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    product_a: Mapped["Product"] = relationship("Product", foreign_keys=[product_a_id])
    product_b: Mapped["Product"] = relationship("Product", foreign_keys=[product_b_id])

    __table_args__ = (
        Index("ix_prod_rel_unique", "product_a_id", "product_b_id", "relationship_type", unique=True),
    )
