"""Catalog models: Category, Brand, Product, ProductVariant, Specification."""

import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class Category(Base, UUIDMixin, TimestampMixin):
    """Hierarchical product and component category."""
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="consumer_electronics", index=True
    )  # "consumer_electronics" or "electronic_component"
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side="Category.id", back_populates="subcategories")
    subcategories: Mapped[List["Category"]] = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")


class Brand(Base, UUIDMixin, TimestampMixin):
    """Product manufacturer / component brand."""
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="brand")


class Product(Base, UUIDMixin, TimestampMixin):
    """Core product or electronic component record."""
    __tablename__ = "products"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(280), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    is_component: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    brand_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    brand: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    specifications: Mapped[List["Specification"]] = relationship("Specification", back_populates="product", cascade="all, delete-orphan")
    component_profile: Mapped[Optional["Component"]] = relationship("Component", back_populates="product", uselist=False, cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    prices: Mapped[List["Price"]] = relationship("Price", back_populates="product", cascade="all, delete-orphan")
    availabilities: Mapped[List["Availability"]] = relationship("Availability", back_populates="product", cascade="all, delete-orphan")
    sources: Mapped[List["ProductSource"]] = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="product", cascade="all, delete-orphan")
    images: Mapped[List["Image"]] = relationship("Image", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_category_is_component", "category_id", "is_component"),
    )


class ProductVariant(Base, UUIDMixin, TimestampMixin):
    """Specific SKU variation (e.g. RAM/Storage/Color or Package variation)."""
    __tablename__ = "product_variants"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    attributes: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    prices: Mapped[List["Price"]] = relationship("Price", back_populates="variant", cascade="all, delete-orphan")
    availabilities: Mapped[List["Availability"]] = relationship("Availability", back_populates="variant", cascade="all, delete-orphan")


class Specification(Base, UUIDMixin, TimestampMixin):
    """Structured specification key-value with JSONB value support."""
    __tablename__ = "specifications"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    spec_group: Mapped[str] = mapped_column(String(80), nullable=False, index=True)  # "Display", "Processor", "Battery", "Wireless"
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)        # "screen_size", "ram_type", "battery_wh"
    value: Mapped[str] = mapped_column(String(255), nullable=False)                   # Human-readable string e.g. "16 GB"
    raw_value: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True) # Normalized numeric e.g. {"val": 16, "unit": "GB"}

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="specifications")

    __table_args__ = (
        Index("ix_specifications_product_group_key", "product_id", "spec_group", "key"),
    )
