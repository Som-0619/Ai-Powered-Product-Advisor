"""Document and ProductImage media models."""

import uuid
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.catalog import Product, ProductVariant


CANONICAL_IMAGE_TYPES = (
    "primary",
    "front",
    "back",
    "left",
    "right",
    "top",
    "bottom",
    "screen",
    "keyboard",
    "ports",
    "camera",
    "connector",
    "board",
    "accessories",
    "gallery",
)


class Document(Base, UUIDMixin, TimestampMixin):
    """Technical datasheets, manuals, and schematics."""
    __tablename__ = "documents"

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(
        String(50), default="datasheet", nullable=False, index=True
    )  # "datasheet", "manual", "schematic", "whitepaper"
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False) # MinIO/S3 object path
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    product: Mapped[Optional["Product"]] = relationship("Product", back_populates="documents")


class ProductImage(Base, UUIDMixin, TimestampMixin):
    """Canonical product images and multimodal inspection assets."""
    __tablename__ = "product_images"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    storage_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # MinIO/S3 object path
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # e.g. "Amazon", "Flipkart", "Manufacturer"
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_type: Mapped[str] = mapped_column(
        String(50), default="primary", nullable=False, index=True
    )
    visual_features: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Canonical alias
    image_id = synonym("id")

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="images")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant")

    __table_args__ = (
        Index("ix_product_images_product_id", "product_id"),
        Index("ix_product_images_variant_id", "variant_id"),
        Index("ix_product_images_image_type", "image_type"),
        Index(
            "ix_product_images_unique_primary",
            "product_id",
            unique=True,
            postgresql_where=text("is_primary = true"),
        ),
    )


# Backward-compatible alias
Image = ProductImage
