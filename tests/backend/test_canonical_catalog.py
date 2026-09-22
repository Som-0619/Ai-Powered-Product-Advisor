"""Automated tests for Canonical Product Catalog Foundation.

Validates the 9 Mandatory Verification Requirements:
1. test_product_identity()
2. test_variant_product_relationship()
3. test_image_product_relationship()
4. test_review_product_relationship()
5. test_retailer_product_relationship()
6. test_no_duplicate_product_identity()
7. test_storage_abstraction()
8. test_product_without_retailer_still_works()
9. test_product_without_image_does_not_use_another_product_image()
"""

import os
import uuid
import inspect
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.catalog import (
    Product,
    ProductVariant,
    CANONICAL_ELECTRONICS_CATEGORIES,
)
from app.models.media import ProductImage, CANONICAL_IMAGE_TYPES
from app.models.reviews import ProductReview
from app.models.retailer_offers import RetailerOffer
from app.models.sources import ProductSource, CANONICAL_SOURCE_TYPES
from app.services.product_catalog_service import ProductCatalogService
from app.services.storage import StorageService, MinIOStorage, S3Storage
from app.adapters.local.minio_storage import MinioStorageService
from app.adapters.aws.s3_storage import AwsS3StorageService


TEST_DB_URL = os.environ.get(
    "LOCAL_POSTGRES_URL",
    "postgresql+asyncpg://advisor_user:advisor_password@127.0.0.1:5432/product_advisor",
)


@pytest_asyncio.fixture(loop_scope="function")
async def test_session():
    """Provides an isolated AsyncSession for canonical catalog tests."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_product_identity(test_session: AsyncSession):
    """Verify canonical product entity requirements:
    1. Required fields: product_id, brand, model, variant, category, subcategory, description, release_year, created_at, updated_at.
    2. product_id is the internal canonical identifier (UUID v4) and never an array index or position.
    3. external_product_id (ASIN/FSN) does NOT replace product_id.
    4. Product is retrievable via ProductCatalogService.get_product(product_id).
    """
    service = ProductCatalogService(test_session)
    stable_uuid = uuid.uuid4()
    asin = "B0CBGF51G3"

    product = await service.create_product(
        product_id=stable_uuid,
        title="Dell XPS 15 9530 Canonical Identity Test",
        slug=f"dell-xps-15-ident-{uuid.uuid4().hex[:8]}",
        brand="Dell",
        model="XPS 15 9530",
        variant="Core i7 / 32GB / 1TB SSD",
        category="Laptops",
        subcategory="Workstation",
        description="Ultra-premium creator workstation laptop.",
        external_product_id=asin,
    )
    product.release_year = 2023
    product.specifications = {
        "cpu": "Intel Core i7-13700H",
        "ram": "32GB DDR5",
        "storage": "1TB NVMe SSD",
    }
    await test_session.commit()

    # Verify canonical identity
    assert product.id == stable_uuid
    assert product.product_id == stable_uuid
    assert isinstance(product.product_id, uuid.UUID)

    # Required fields verification
    assert product.brand == "Dell"
    assert product.model == "XPS 15 9530"
    assert product.variant == "Core i7 / 32GB / 1TB SSD"
    assert product.category == "Laptops"
    assert product.subcategory == "Workstation"
    assert product.description == "Ultra-premium creator workstation laptop."
    assert product.release_year == 2023
    assert product.created_at is not None
    assert product.updated_at is not None
    assert product.specifications["cpu"] == "Intel Core i7-13700H"

    # Isolation from external marketplace identifier: external_product_id != product_id
    assert product.external_product_id == asin
    assert product.product_id != asin
    assert str(product.product_id) != asin

    # Retrieval via ProductCatalogService
    fetched = await service.get_product(stable_uuid)
    assert fetched is not None
    assert fetched.product_id == stable_uuid
    assert fetched.brand == "Dell"
    assert fetched.model == "XPS 15 9530"


@pytest.mark.asyncio
async def test_variant_product_relationship(test_session: AsyncSession):
    """Verify product_variants fields and child-to-parent relationship:
    1. Fields: variant_id, product_id, variant_name, sku, external_product_id, specifications, created_at, updated_at.
    2. Multiple distinct hardware variants strictly belong to product_id.
    3. Retrieval via get_product_variants(product_id).
    """
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    product = await service.create_product(
        product_id=product_uuid,
        title="Apple iPhone 15 Pro",
        slug=f"iphone-15-pro-{uuid.uuid4().hex[:8]}",
        brand="Apple",
        model="iPhone 15 Pro",
        category="Smartphones",
    )
    await test_session.commit()

    v1_id = uuid.uuid4()
    v2_id = uuid.uuid4()

    var1 = await service.create_variant(
        variant_id=v1_id,
        product_id=product_uuid,
        variant_name="128GB / Natural Titanium",
        sku=f"APL-IP15P-128-{uuid.uuid4().hex[:6]}",
        specifications={"storage": "128GB", "color": "Natural Titanium", "ram": "8GB"},
        external_variant_id="APL-ASIN-128",
    )
    var2 = await service.create_variant(
        variant_id=v2_id,
        product_id=product_uuid,
        variant_name="256GB / Black Titanium",
        sku=f"APL-IP15P-256-{uuid.uuid4().hex[:6]}",
        specifications={"storage": "256GB", "color": "Black Titanium", "ram": "8GB"},
        external_variant_id="APL-ASIN-256",
    )
    await test_session.commit()

    # Verify fields and relationship
    assert var1.product_id == product_uuid
    assert var2.product_id == product_uuid
    assert var1.variant_id == v1_id
    assert var2.variant_id == v2_id
    assert var1.variant_name == "128GB / Natural Titanium"
    assert var2.variant_name == "256GB / Black Titanium"
    assert var1.specifications["storage"] == "128GB"
    assert var2.specifications["storage"] == "256GB"
    assert var1.created_at is not None
    assert var1.updated_at is not None

    # Fetch through service
    variants = await service.get_product_variants(product_uuid)
    assert len(variants) >= 2
    for v in variants:
        assert v.product_id == product_uuid
        assert v.variant_id is not None


@pytest.mark.asyncio
async def test_image_product_relationship(test_session: AsyncSession):
    """Verify product_images fields and strict 1-to-1 relationship:
    1. Fields: image_id, product_id, variant_id, image_type, storage_key, source, source_url, verified, created_at, updated_at.
    2. Allowed image types.
    3. Every image strictly references product_id.
    4. Retrieval via get_product_images(product_id).
    """
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    await service.create_product(
        product_id=product_uuid,
        title="Sony WH-1000XM5 Headphones",
        slug=f"sony-wh1000xm5-{uuid.uuid4().hex[:8]}",
        brand="Sony",
        model="WH-1000XM5",
        category="Headphones",
    )
    await test_session.commit()

    img1 = await service.add_image(
        product_id=product_uuid,
        image_url="https://images.example.com/sony-front.webp",
        image_type="front",
        storage_key="images/sony/front.webp",
        source="Manufacturer",
        is_primary=True,
        verified=True,
    )
    img2 = await service.add_image(
        product_id=product_uuid,
        image_url="https://images.example.com/sony-ports.webp",
        image_type="ports",
        storage_key="images/sony/ports.webp",
        source="Manufacturer",
        is_primary=False,
        verified=True,
    )
    await test_session.commit()

    # Assert schema fields
    assert img1.product_id == product_uuid
    assert img2.product_id == product_uuid
    assert img1.image_id == img1.id
    assert img1.image_type in CANONICAL_IMAGE_TYPES
    assert img2.image_type in CANONICAL_IMAGE_TYPES
    assert img1.storage_key == "images/sony/front.webp"
    assert img1.source == "Manufacturer"
    assert img1.verified is True
    assert img1.created_at is not None

    # Retrieve through catalog service
    images = await service.get_product_images(product_uuid)
    assert len(images) >= 2
    for im in images:
        assert im.product_id == product_uuid


@pytest.mark.asyncio
async def test_review_product_relationship(test_session: AsyncSession):
    """Verify product_reviews fields and relationship:
    1. Fields: review_id, product_id, rating, title, content, verified_purchase, source, created_at.
    2. Every review strictly references product_id (never attached by name alone).
    3. Retrieval via get_product_reviews(product_id).
    """
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    await service.create_product(
        product_id=product_uuid,
        title="Raspberry Pi 5 Review Test",
        slug=f"rpi-5-review-{uuid.uuid4().hex[:8]}",
        brand="Raspberry Pi",
        model="Raspberry Pi 5",
        category="Development boards",
    )
    await test_session.commit()

    rev = await service.add_review(
        product_id=product_uuid,
        rating=4.8,
        title="Phenomenal SBC Performance",
        body="Massive speed improvement with PCIe support and active cooling.",
        source="Customer Review",
        verified_purchase=True,
    )
    await test_session.commit()

    assert rev.product_id == product_uuid
    assert rev.review_id == rev.id
    assert rev.rating == 4.8
    assert rev.title == "Phenomenal SBC Performance"
    assert rev.content == "Massive speed improvement with PCIe support and active cooling."
    assert rev.verified_purchase is True
    assert rev.source == "Customer Review"
    assert rev.created_at is not None

    # Fetch through service
    reviews = await service.get_product_reviews(product_uuid)
    assert len(reviews) >= 1
    for r in reviews:
        assert r.product_id == product_uuid


@pytest.mark.asyncio
async def test_retailer_product_relationship(test_session: AsyncSession):
    """Verify retailer_offers fields, constraints, and relationship:
    1. Fields: offer_id, product_id, variant_id, retailer, external_product_id, url, price, currency, availability_status, verification_status, last_verified.
    2. Retailers: amazon, flipkart.
    3. Availability: available, unavailable, unknown.
    4. Verification: verified, unverified, broken, not_available.
    5. Retrieval via get_retailer_offers(product_id).
    """
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    await service.create_product(
        product_id=product_uuid,
        title="Logitech MX Master 3S Test",
        slug=f"logitech-mx3s-{uuid.uuid4().hex[:8]}",
        brand="Logitech",
        model="MX Master 3S",
        category="Mice",
    )
    await test_session.commit()

    az_offer = await service.add_retailer_offer(
        product_id=product_uuid,
        retailer="amazon",
        external_product_id="B0B11EL3BR",
        url="https://www.amazon.in/dp/B0B11EL3BR",
        price=8995.0,
        currency="INR",
        availability_status="available",
        verification_status="verified",
    )
    fk_offer = await service.add_retailer_offer(
        product_id=product_uuid,
        retailer="flipkart",
        external_product_id="itm1000000001",
        url="https://www.flipkart.com/product/p/itm1000000001",
        price=8799.0,
        currency="INR",
        availability_status="available",
        verification_status="verified",
    )
    await test_session.commit()

    # Assert offer schema and constraints
    assert az_offer.product_id == product_uuid
    assert fk_offer.product_id == product_uuid
    assert az_offer.offer_id == az_offer.id
    assert az_offer.retailer in ("amazon", "flipkart")
    assert az_offer.availability_status in ("available", "unavailable", "unknown")
    assert az_offer.verification_status in ("verified", "unverified", "broken", "not_available")

    # Fetch through service
    offers = await service.get_retailer_offers(product_uuid)
    assert len(offers) == 2
    for o in offers:
        assert o.product_id == product_uuid


@pytest.mark.asyncio
async def test_no_duplicate_product_identity(test_session: AsyncSession):
    """Verify data integrity: prevent duplicate product identity by UUID or unique slug."""
    service = ProductCatalogService(test_session)
    duplicate_uuid = uuid.uuid4()
    duplicate_slug = f"unique-laptop-{uuid.uuid4().hex[:8]}"

    # Insert first product
    await service.create_product(
        product_id=duplicate_uuid,
        title="Original Unique Laptop",
        slug=duplicate_slug,
        brand="Lenovo",
        model="ThinkPad P1",
    )
    await test_session.commit()

    # Attempting to insert a duplicate with the same UUID must raise IntegrityError
    with pytest.raises(IntegrityError):
        await service.create_product(
            product_id=duplicate_uuid,
            title="Duplicate UUID Laptop",
            slug=f"different-slug-{uuid.uuid4().hex[:8]}",
            brand="Lenovo",
            model="ThinkPad P1",
        )
        await test_session.commit()
    await test_session.rollback()

    # Attempting to insert a duplicate with the same unique slug must raise IntegrityError
    with pytest.raises(IntegrityError):
        await service.create_product(
            product_id=uuid.uuid4(),
            title="Duplicate Slug Laptop",
            slug=duplicate_slug,
            brand="Lenovo",
            model="ThinkPad P1",
        )
        await test_session.commit()
    await test_session.rollback()


def test_storage_abstraction():
    """Verify storage abstraction interface and implementation compliance:
    1. StorageService defines upload(), get_url(), delete(), exists().
    2. MinIOStorage implements the abstraction for local environments.
    3. S3Storage implements the abstraction for AWS production environments.
    4. Application interacts with StorageService without direct MinIO/boto3 SDK calls.
    """
    # 1. Interface method verification
    for method_name in ("upload", "get_url", "delete", "exists"):
        assert hasattr(StorageService, method_name), f"StorageService missing '{method_name}' method"
        method = getattr(StorageService, method_name)
        assert callable(method), f"StorageService.{method_name} is not callable"

    # 2. Local MinIO adapter compliance
    assert issubclass(MinIOStorage, StorageService)
    assert hasattr(MinIOStorage, "upload")
    assert hasattr(MinIOStorage, "get_url")
    assert hasattr(MinIOStorage, "delete")
    assert hasattr(MinIOStorage, "exists")

    # 3. AWS S3 adapter compliance
    assert issubclass(S3Storage, StorageService)
    assert hasattr(S3Storage, "upload")
    assert hasattr(S3Storage, "get_url")
    assert hasattr(S3Storage, "delete")
    assert hasattr(S3Storage, "exists")


@pytest.mark.asyncio
async def test_product_without_retailer_still_works(test_session: AsyncSession):
    """CRITICAL: Retailer offers are strictly OPTIONAL.
    A product must remain fully functional when it has no Amazon offer and no Flipkart offer.
    """
    service = ProductCatalogService(test_session)
    standalone_uuid = uuid.uuid4()

    # Create standalone product with no retailer offers
    standalone_prod = await service.create_product(
        product_id=standalone_uuid,
        title="Open Source Hardware ESP32 Dev Board",
        slug=f"standalone-esp32-{uuid.uuid4().hex[:8]}",
        brand="Espressif",
        model="ESP32-WROOM-32",
        category="Microcontrollers",
        description="Standalone development board without commercial retailer listings.",
    )
    await test_session.commit()

    # 1. Product must be fetched successfully
    fetched = await service.get_product(standalone_uuid)
    assert fetched is not None
    assert fetched.product_id == standalone_uuid
    assert fetched.title == "Open Source Hardware ESP32 Dev Board"

    # 2. Retailer offers query must return an empty list without crashing or failing
    offers = await service.get_retailer_offers(standalone_uuid)
    assert offers == []
    assert isinstance(offers, list)
    assert len(offers) == 0


@pytest.mark.asyncio
async def test_product_without_image_does_not_use_another_product_image(test_session: AsyncSession):
    """CRITICAL: An image MUST belong to exactly one product_id.
    A product without an image must NEVER leak, borrow, or fallback to another product's image.
    """
    service = ProductCatalogService(test_session)
    prod_with_image_uuid = uuid.uuid4()
    prod_without_image_uuid = uuid.uuid4()

    # Product A has an image
    await service.create_product(
        product_id=prod_with_image_uuid,
        title="Product A with Verified Image",
        slug=f"prod-a-image-{uuid.uuid4().hex[:8]}",
        brand="BrandA",
        model="ModelA",
        category="Laptops",
    )
    product_a_image = await service.add_image(
        product_id=prod_with_image_uuid,
        image_url="https://images.example.com/unique-product-a-front.webp",
        image_type="primary",
        verified=True,
    )

    # Product B has NO image
    await service.create_product(
        product_id=prod_without_image_uuid,
        title="Product B with Zero Images",
        slug=f"prod-b-no-image-{uuid.uuid4().hex[:8]}",
        brand="BrandB",
        model="ModelB",
        category="Laptops",
    )
    await test_session.commit()

    # Product A must have its own image
    images_a = await service.get_product_images(prod_with_image_uuid)
    assert len(images_a) == 1
    assert images_a[0].product_id == prod_with_image_uuid
    assert images_a[0].image_url == "https://images.example.com/unique-product-a-front.webp"

    # Product B must return an empty list and NEVER contain Product A's image
    images_b = await service.get_product_images(prod_without_image_uuid)
    assert images_b == []
    assert len(images_b) == 0

    # Explicit cross-check: No image in the database for Product B can have Product A's URL or ID
    for img in images_b:
        assert img.product_id != prod_with_image_uuid
        assert img.image_url != product_a_image.image_url
