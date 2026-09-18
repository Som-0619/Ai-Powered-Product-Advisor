"""Document and Image media models."""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


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


class Image(Base, UUIDMixin, TimestampMixin):
    """Product images and multimodal inspection assets."""
    __tablename__ = "images"

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True
    )
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False) # MinIO/S3 object path
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_type: Mapped[str] = mapped_column(
        String(50), default="product", nullable=False, index=True
    )  # "product", "ports", "board_layout", "schematic", "packaging"
    visual_features: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )  # Detected connectors, ports, layout features
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    product: Mapped[Optional["Product"]] = relationship("Product", back_populates="images")
