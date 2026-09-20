"""Catalog models: Category, Brand, Product, ProductVariant, Specification."""

import uuid
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey, Index, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.components import Component
    from app.models.reviews import Review
    from app.models.pricing import Price, Availability
    from app.models.sources import ProductSource
    from app.models.media import Document, ProductImage
    from app.models.retailer_offers import RetailerOffer


class BrandName(str):
    """String subclass providing .name attribute for backward compatibility."""
    @property
    def name(self) -> str:
        return str(self)


class CategoryName(str):
    """String subclass providing .name and .slug attributes for backward compatibility."""
    @property
    def name(self) -> str:
        return str(self)

    @property
    def slug(self) -> str:
        return str(self).lower().replace(" ", "-")


class BrandType(TypeDecorator):
    """Custom type that returns BrandName for seamless string & object attribute access."""
    impl = String(100)
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None:
            return BrandName(value)
        return None


class CategoryType(TypeDecorator):
    """Custom type that returns CategoryName for seamless string & object attribute access."""
    impl = String(100)
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None:
            return CategoryName(value)
        return None


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
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category_rel")


class Brand(Base, UUIDMixin, TimestampMixin):
    """Product manufacturer / component brand."""
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="brand_rel")


class Product(Base, UUIDMixin, TimestampMixin):
    """Canonical product entity representing the single source of truth for product identity."""
    __tablename__ = "products"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(280), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(BrandType(), nullable=True, index=True)
    model: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    variant: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(CategoryType(), nullable=True, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    external_product_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    model_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    is_component: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    brand_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Canonical alias: product_id maps to id
    product_id = synonym("id")

    # Relationships
    category_rel: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    brand_rel: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    specifications: Mapped[List["Specification"]] = relationship("Specification", back_populates="product", cascade="all, delete-orphan")
    component_profile: Mapped[Optional["Component"]] = relationship("Component", back_populates="product", uselist=False, cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    prices: Mapped[List["Price"]] = relationship("Price", back_populates="product", cascade="all, delete-orphan")
    availabilities: Mapped[List["Availability"]] = relationship("Availability", back_populates="product", cascade="all, delete-orphan")
    sources: Mapped[List["ProductSource"]] = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="product", cascade="all, delete-orphan")
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    retailer_offers: Mapped[List["RetailerOffer"]] = relationship("RetailerOffer", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_category_is_component", "category_id", "is_component"),
        Index("ix_products_brand", "brand"),
        Index("ix_products_category", "category"),
        Index("ix_products_external_product_id", "external_product_id"),
        Index("ix_products_model", "model"),
    )


class ProductVariant(Base, UUIDMixin, TimestampMixin):
    """Specific SKU variation (e.g. RAM/Storage/Color or Package variation)."""
    __tablename__ = "product_variants"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    variant_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    external_variant_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    attributes: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    specifications: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    # Canonical alias: variant_id maps to id
    variant_id = synonym("id")

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    prices: Mapped[List["Price"]] = relationship("Price", back_populates="variant", cascade="all, delete-orphan")
    availabilities: Mapped[List["Availability"]] = relationship("Availability", back_populates="variant", cascade="all, delete-orphan")
    retailer_offers: Mapped[List["RetailerOffer"]] = relationship("RetailerOffer", back_populates="variant", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_product_variants_external_variant_id", "external_variant_id"),
    )


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
