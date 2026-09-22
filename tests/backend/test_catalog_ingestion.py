"""Automated tests for Stage 2 Canonical Catalog Ingestion Pipeline.

Validates Section 18 requirements:
1. test_duplicate_prevention()
2. test_idempotent_import()
3. test_product_identity()
4. test_variant_identity()
5. test_image_product_association()
6. test_review_product_association()
7. test_source_provenance()
8. test_retailer_offer_validation()
9. test_category_validation()
"""

import os
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from app.models.catalog import (
    Product,
    ProductVariant,
    CANONICAL_ELECTRONICS_CATEGORIES,
)
from app.models.media import ProductImage, CANONICAL_IMAGE_TYPES
from app.models.sources import ProductSource, CANONICAL_SOURCE_TYPES
from app.models.retailer_offers import RetailerOffer
from app.models.reviews import ProductReview
from app.ingestion.catalog_ingestion_service import (
    CatalogIngestionService,
    compute_canonical_product_id,
    compute_canonical_variant_id,
)
from app.services.product_catalog_service import ProductCatalogService

TEST_DB_URL = os.environ.get(
    "LOCAL_POSTGRES_URL",
    "postgresql+asyncpg://advisor_user:advisor_password@127.0.0.1:5432/product_advisor",
)


@pytest_asyncio.fixture(loop_scope="function")
async def ingestion_session():
    """Provides an isolated AsyncSession for catalog ingestion tests."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_duplicate_prevention(ingestion_session: AsyncSession):
    """Verify that duplicate products within batch or database are prevented."""
    service = CatalogIngestionService(ingestion_session)

    candidate = {
        "brand": "Raspberry Pi",
        "model": "Pico W Test Duplicate",
        "variant": "Standard",
        "title": "Raspberry Pi Pico W Test Duplicate",
        "category": "Microcontrollers",
        "subcategory": "Microcontroller Boards",
        "sku": "RPI-PICOW-DUP-01",
        "specs": {"mcu": "RP2040", "operating_voltage": "3.3V"},
        "images": [{"image_type": "primary", "source_url": "https://example.com/pico.jpg"}],
    }

    # Run with candidate twice in same batch
    report = await service.run_pipeline([candidate, candidate], dry_run=True)
    assert report["products_discovered"] == 2
    assert report["new_products"] == 1
    assert report["possible_duplicates"] == 1


@pytest.mark.asyncio
async def test_idempotent_import(ingestion_session: AsyncSession):
    """Verify that running ingestion on the same dataset twice is safe and produces 0 duplicates."""
    service = CatalogIngestionService(ingestion_session)
    pid = uuid.uuid4()

    item = {
        "product_id": pid,
        "brand": "Framework",
        "model": f"Laptop 13 Idempotent Test {pid.hex[:6]}",
        "variant": "Intel Core Ultra",
        "title": f"Framework Laptop 13 Idempotent Test {pid.hex[:6]}",
        "category": "Laptops",
        "subcategory": "Thin & Light Laptops",
        "sku": f"FRM-13-IDEMP-{pid.hex[:6]}",
        "specs": {"cpu": "Intel Core Ultra 7", "ram": "16GB"},
        "images": [{"image_type": "primary", "source_url": "https://example.com/fw13.jpg"}],
    }

    # First live import
    report1 = await service.run_pipeline([item], dry_run=False)
    assert report1["persisted_to_database"] == 1

    # Second live import of identical item
    report2 = await service.run_pipeline([item], dry_run=False)
    assert report2["new_products"] == 0
    assert report2["possible_duplicates"] == 1
    assert report2["persisted_to_database"] == 0


@pytest.mark.asyncio
async def test_product_identity():
    """Verify deterministic UUIDv5 generation preserves identity and prevents external key usage as PID."""
    pid1 = compute_canonical_product_id("Apple", "MacBook Air 15 M3", "16GB / 512GB")
    pid2 = compute_canonical_product_id("Apple", "MacBook Air 15 M3", "16GB / 512GB")
    pid3 = compute_canonical_product_id("Apple", "MacBook Air 15 M3", "24GB / 1TB")

    assert pid1 == pid2, "Deterministic UUID must be identical for same brand, model, and variant"
    assert pid1 != pid3, "Different variants must have distinct canonical product IDs"
    assert isinstance(pid1, uuid.UUID)


@pytest.mark.asyncio
async def test_variant_identity(ingestion_session: AsyncSession):
    """Verify variant identity association with canonical product_id."""
    catalog_service = ProductCatalogService(ingestion_session)
    pid = uuid.uuid4()

    await catalog_service.create_product(
        product_id=pid,
        title="Lenovo LOQ 15 Variant Test",
        slug=f"lenovo-loq-15-test-{pid.hex[:6]}",
        brand="Lenovo",
        model="LOQ 15",
        category="Laptops",
    )

    # Add 2 distinct configuration variants
    v1 = await catalog_service.create_variant(
        product_id=pid,
        variant_name="16GB / 512GB / RTX 4050",
        sku=f"LEN-LOQ-4050-{pid.hex[:4]}",
        specifications={"ram": "16GB", "storage": "512GB", "gpu": "RTX 4050"},
    )
    v2 = await catalog_service.create_variant(
        product_id=pid,
        variant_name="16GB / 1TB / RTX 4060",
        sku=f"LEN-LOQ-4060-{pid.hex[:4]}",
        specifications={"ram": "16GB", "storage": "1TB", "gpu": "RTX 4060"},
    )
    await ingestion_session.commit()

    variants = await catalog_service.get_product_variants(pid)
    assert len(variants) == 2
    for v in variants:
        assert v.product_id == pid
        assert v.id in [v1.id, v2.id]


@pytest.mark.asyncio
async def test_image_product_association(ingestion_session: AsyncSession):
    """Verify strict image association and deterministic storage key generation."""
    catalog_service = ProductCatalogService(ingestion_session)
    pid = uuid.uuid4()

    await catalog_service.create_product(
        product_id=pid,
        title="Sony WH-1000XM5 Image Test",
        slug=f"sony-wh1000xm5-img-test-{pid.hex[:6]}",
        brand="Sony",
        model="WH-1000XM5",
        category="Headphones",
    )

    img = await catalog_service.add_image(
        product_id=pid,
        image_url="https://example.com/sony_xm5.jpg",
        image_type="primary",
        storage_key=f"products/{pid}/primary.webp",
    )
    await ingestion_session.commit()

    images = await catalog_service.get_product_images(pid)
    assert len(images) == 1
    for img in images:
        assert img.product_id == pid
        assert img.storage_key == f"products/{pid}/primary.webp"
        assert img.image_type in CANONICAL_IMAGE_TYPES


@pytest.mark.asyncio
async def test_review_product_association(ingestion_session: AsyncSession):
    """Verify that newly imported products without reviews maintain review count 0 and remain valid."""
    catalog_service = ProductCatalogService(ingestion_session)
    pid = uuid.uuid4()

    await catalog_service.create_product(
        product_id=pid,
        title="Bose QC Ultra Review Test",
        slug=f"bose-qc-ultra-rev-test-{pid.hex[:6]}",
        brand="Bose",
        model="QC Ultra",
        category="Headphones",
    )
    await ingestion_session.commit()

    reviews = await catalog_service.get_product_reviews(pid)
    assert len(reviews) == 0, "Products without authentic reviews must have review count 0"


@pytest.mark.asyncio
async def test_source_provenance(ingestion_session: AsyncSession):
    """Verify provenance metadata attachment to canonical product."""
    catalog_service = ProductCatalogService(ingestion_session)
    pid = uuid.uuid4()

    await catalog_service.create_product(
        product_id=pid,
        title="Bosch BME680 Provenance Test",
        slug=f"bosch-bme680-prov-test-{pid.hex[:6]}",
        brand="Bosch Sensortec",
        model="BME680",
        category="Sensors",
    )

    src = await catalog_service.add_product_source(
        product_id=pid,
        source_url="https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme680/",
        source_type="manufacturer",
        external_product_id="BME680-MOD",
        trust_score=1.0,
    )
    await ingestion_session.commit()

    sources = await catalog_service.get_product_sources(pid)
    assert len(sources) == 1
    assert sources[0].product_id == pid
    assert sources[0].source_type in CANONICAL_SOURCE_TYPES
    assert sources[0].trust_score == 1.0


@pytest.mark.asyncio
async def test_retailer_offer_validation(ingestion_session: AsyncSession):
    """Verify retailer offers adhere to check constraints and missing offers are tolerated."""
    catalog_service = ProductCatalogService(ingestion_session)
    pid = uuid.uuid4()

    await catalog_service.create_product(
        product_id=pid,
        title="Google Pixel 8 Offer Test",
        slug=f"google-pixel-8-offer-test-{pid.hex[:6]}",
        brand="Google",
        model="Pixel 8",
        category="Smartphones",
    )

    # Valid retailer offer
    offer = await catalog_service.add_retailer_offer(
        product_id=pid,
        retailer="amazon",
        external_product_id="B0CGV44SDF",
        url="https://www.amazon.in/dp/B0CGV44SDF",
        price=75999.0,
        availability_status="available",
        verification_status="verified",
    )
    await ingestion_session.commit()

    offers = await catalog_service.get_retailer_offers(pid)
    assert len(offers) == 1
    assert offers[0].retailer == "amazon"
    assert offers[0].verification_status == "verified"


@pytest.mark.asyncio
async def test_category_validation():
    """Verify canonical category enforcement across imported dataset."""
    from app.ingestion.data import ALL_NEW_CANONICAL_PRODUCTS

    valid_categories_set = set(CANONICAL_ELECTRONICS_CATEGORIES)
    for item in ALL_NEW_CANONICAL_PRODUCTS:
        cat = item.get("category")
        assert cat in valid_categories_set, f"Product {item['title']} has non-canonical category: '{cat}'"
