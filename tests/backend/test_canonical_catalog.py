"""Automated tests for Canonical Product Catalog Foundation.

Validates Requirements:
1. Canonical product entity contains: product_id, brand, model, variant, category, subcategory, description, external_product_id, created_at, updated_at.
2. product_id is a stable UUID; never uses array index; never replaced by external_product_id.
3. Variants strictly belong to product_id (variant_id, variant_name, sku, external_variant_id, specifications).
4. Product images strictly belong to product_id (image_id, variant_id, image_url, image_type, source, verified).
5. Retailer offers strictly belong to product_id (offer_id, retailer, external_product_id, url, price, currency, availability_status, verification_status).
6. Product sources strictly belong to product_id (source_id, source_type, source_url, external_product_id, trust_score).
7. Foreign-key integrity and cascade constraints.
8. ProductCatalogService retrieval methods.
"""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.catalog import Product, ProductVariant
from app.models.media import ProductImage, CANONICAL_IMAGE_TYPES
from app.models.retailer_offers import RetailerOffer
from app.models.sources import ProductSource, CANONICAL_SOURCE_TYPES
from app.services.product_catalog_service import ProductCatalogService


# Use 127.0.0.1 for local host connectivity to PostgreSQL container
TEST_DB_URL = "postgresql+asyncpg://advisor_user:advisor_password@127.0.0.1:5432/product_advisor"


@pytest_asyncio.fixture(loop_scope="function")
async def test_session():
    """Provides an isolated AsyncSession for catalog tests."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_product_has_stable_id(test_session: AsyncSession):
    """Verify that every product has a stable, immutable UUID identity and not an array index."""
    stable_uuid = uuid.uuid4()
    service = ProductCatalogService(test_session)

    product = await service.create_product(
        product_id=stable_uuid,
        title="Dell XPS 15 9530 Canonical Test",
        slug=f"dell-xps-15-{uuid.uuid4().hex[:8]}",
        brand="Dell",
        model="XPS 15 9530",
        variant="Core i7 / 32GB / 1TB SSD",
        category="Laptops & Ultrabooks",
        subcategory="Creator & Premium Laptops",
        description="Ultra-premium creator workstation laptop.",
        external_product_id="B0CBGF51G3",
    )
    await test_session.commit()

    # Identity checks
    assert product.id == stable_uuid
    assert product.product_id == stable_uuid
    assert isinstance(product.product_id, uuid.UUID)
    # Ensure ID is not a sequential number or array index
    assert str(product.product_id) == str(stable_uuid)

    # Fetch back via service
    fetched = await service.get_product(stable_uuid)
    assert fetched is not None
    assert fetched.id == stable_uuid
    assert fetched.product_id == stable_uuid
    assert fetched.brand == "Dell"
    assert fetched.model == "XPS 15 9530"
    assert fetched.category == "Laptops & Ultrabooks"
    assert fetched.subcategory == "Creator & Premium Laptops"
    assert fetched.created_at is not None
    assert fetched.updated_at is not None


@pytest.mark.asyncio
async def test_variant_belongs_to_product(test_session: AsyncSession):
    """Verify variants have distinct identities and strictly belong to product_id."""
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    product = await service.create_product(
        product_id=product_uuid,
        title="ThinkPad X1 Carbon Gen 11 Test",
        slug=f"thinkpad-x1-test-{uuid.uuid4().hex[:8]}",
        brand="Lenovo",
        model="ThinkPad X1 Carbon Gen 11",
        category="Laptops & Ultrabooks",
    )
    await test_session.commit()

    # Create 2 distinct hardware variants (16GB RAM vs 32GB RAM)
    v1_id = uuid.uuid4()
    v2_id = uuid.uuid4()

    var1 = await service.create_variant(
        variant_id=v1_id,
        product_id=product_uuid,
        variant_name="16GB RAM / 512GB SSD / Core i7-1365U",
        sku=f"LNV-X1C11-16-{uuid.uuid4().hex[:6]}",
        specifications={"ram_gb": 16, "storage_gb": 512, "cpu": "Intel Core i7-1365U"},
        external_variant_id="VAR-ASIN-16GB",
    )
    var2 = await service.create_variant(
        variant_id=v2_id,
        product_id=product_uuid,
        variant_name="32GB RAM / 1TB SSD / Core i7-1370P",
        sku=f"LNV-X1C11-32-{uuid.uuid4().hex[:6]}",
        specifications={"ram_gb": 32, "storage_gb": 1024, "cpu": "Intel Core i7-1370P"},
        external_variant_id="VAR-ASIN-32GB",
    )
    await test_session.commit()

    # Foreign key and identity checks
    assert var1.product_id == product_uuid
    assert var2.product_id == product_uuid
    assert var1.variant_id == v1_id
    assert var2.variant_id == v2_id
    assert var1.variant_id != var2.variant_id
    assert var1.sku != var2.sku
    assert var1.specifications["ram_gb"] == 16
    assert var2.specifications["ram_gb"] == 32

    # Fetch variant through service
    fetched_v1 = await service.get_variant(v1_id)
    assert fetched_v1 is not None
    assert fetched_v1.product_id == product_uuid
    assert fetched_v1.variant_name == "16GB RAM / 512GB SSD / Core i7-1365U"


@pytest.mark.asyncio
async def test_image_belongs_to_product(test_session: AsyncSession):
    """Verify images strictly belong to product_id across canonical image types."""
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    await service.create_product(
        product_id=product_uuid,
        title="Sony WH-1000XM5 Test",
        slug=f"sony-wh1000xm5-{uuid.uuid4().hex[:8]}",
        brand="Sony",
        model="WH-1000XM5",
        category="Audio & Headphones",
    )
    await test_session.commit()

    # Add images for various canonical types
    img_front = await service.add_image(
        product_id=product_uuid,
        image_url="https://images.example.com/sony-front.jpg",
        image_type="front",
        is_primary=True,
        verified=True,
        source="Manufacturer",
    )
    img_ports = await service.add_image(
        product_id=product_uuid,
        image_url="https://images.example.com/sony-ports.jpg",
        image_type="ports",
        is_primary=False,
        verified=True,
        source="Amazon",
    )
    await test_session.commit()

    # Verify relationships
    assert img_front.product_id == product_uuid
    assert img_ports.product_id == product_uuid
    assert img_front.image_id == img_front.id
    assert img_front.image_type in CANONICAL_IMAGE_TYPES
    assert img_ports.image_type in CANONICAL_IMAGE_TYPES

    # Fetch through service
    images = await service.get_product_images(product_uuid)
    assert len(images) >= 2
    for img in images:
        assert img.product_id == product_uuid
        assert img.verified is True


@pytest.mark.asyncio
async def test_retailer_offer_belongs_to_product(test_session: AsyncSession):
    """Verify retailer offers strictly reference product_id with valid marketplaces and statuses."""
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    await service.create_product(
        product_id=product_uuid,
        title="Apple MacBook Pro 14 Test",
        slug=f"macbook-pro-14-{uuid.uuid4().hex[:8]}",
        brand="Apple",
        model="MacBook Pro 14",
        category="Laptops & Ultrabooks",
    )
    await test_session.commit()

    # Add Amazon offer
    az_offer = await service.add_retailer_offer(
        product_id=product_uuid,
        retailer="amazon",
        external_product_id="B0CHX1W1XY",
        url="https://www.amazon.in/dp/B0CHX1W1XY",
        price=199900.0,
        currency="INR",
        availability_status="available",
        verification_status="verified",
    )
    # Add Flipkart offer
    fk_offer = await service.add_retailer_offer(
        product_id=product_uuid,
        retailer="flipkart",
        external_product_id="itm1234567890",
        url="https://www.flipkart.com/product/p/itm1234567890",
        price=197900.0,
        currency="INR",
        availability_status="available",
        verification_status="verified",
    )
    await test_session.commit()

    # Identity and constraints
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
        assert o.currency == "INR"


@pytest.mark.asyncio
async def test_source_belongs_to_product(test_session: AsyncSession):
    """Verify product source provenance strictly belongs to product_id."""
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    await service.create_product(
        product_id=product_uuid,
        title="ESP32-S3 Microcontroller Test",
        slug=f"esp32-s3-test-{uuid.uuid4().hex[:8]}",
        brand="Espressif",
        model="ESP32-S3",
        category="Electronic Components",
        is_component=True,
    )
    await test_session.commit()

    source = await service.add_product_source(
        product_id=product_uuid,
        source_url="https://www.espressif.com/en/products/socs/esp32-s3",
        source_type="manufacturer",
        external_product_id="ESP32-S3-WROOM-1",
        trust_score=0.99,
    )
    await test_session.commit()

    assert source.product_id == product_uuid
    assert source.source_type == "manufacturer"
    assert source.source_type in CANONICAL_SOURCE_TYPES
    assert source.trust_score == 0.99

    sources = await service.get_product_sources(product_uuid)
    assert len(sources) >= 1
    assert sources[0].product_id == product_uuid


@pytest.mark.asyncio
async def test_external_id_does_not_replace_product_id(test_session: AsyncSession):
    """CRITICAL: external_product_id (e.g. Amazon ASIN) must NEVER replace internal product_id."""
    service = ProductCatalogService(test_session)
    asin = "B0CBGF51G3"
    custom_uuid = uuid.uuid4()

    product = await service.create_product(
        product_id=custom_uuid,
        title="ASIN Identity Isolation Test Laptop",
        slug=f"asin-test-{uuid.uuid4().hex[:8]}",
        brand="Dell",
        model="XPS 15",
        external_product_id=asin,
    )
    await test_session.commit()

    # 1. Primary key must NOT be ASIN string
    assert product.id != asin
    assert product.product_id != asin
    assert isinstance(product.id, uuid.UUID)

    # 2. external_product_id stores the ASIN
    assert product.external_product_id == asin

    # 3. Product ID remains stable even if external_product_id changes
    product.external_product_id = "B0UPDATED99"
    await test_session.commit()

    re_fetched = await service.get_product(custom_uuid)
    assert re_fetched.id == custom_uuid
    assert re_fetched.product_id == custom_uuid
    assert re_fetched.external_product_id == "B0UPDATED99"


@pytest.mark.asyncio
async def test_foreign_key_integrity(test_session: AsyncSession):
    """Verify relational cascading deletes and foreign-key integrity constraints."""
    service = ProductCatalogService(test_session)
    product_uuid = uuid.uuid4()

    product = await service.create_product(
        product_id=product_uuid,
        title="Cascade Deletion Test Product",
        slug=f"cascade-test-{uuid.uuid4().hex[:8]}",
    )
    await test_session.commit()

    # Attach variant, image, offer, and source
    var = await service.create_variant(
        product_id=product_uuid,
        variant_name="Default Variant",
        sku=f"CASCADE-SKU-{uuid.uuid4().hex[:6]}",
    )
    img = await service.add_image(
        product_id=product_uuid,
        image_url="https://example.com/test.jpg",
    )
    offer = await service.add_retailer_offer(
        product_id=product_uuid,
        retailer="amazon",
        price=100.0,
    )
    source = await service.add_product_source(
        product_id=product_uuid,
        source_url="https://example.com/source",
    )
    await test_session.commit()

    # Delete parent product
    await test_session.delete(product)
    await test_session.commit()

    # Verify children were cascaded on delete
    res_var = await test_session.execute(select(ProductVariant).where(ProductVariant.id == var.id))
    assert res_var.scalar_one_or_none() is None

    res_img = await test_session.execute(select(ProductImage).where(ProductImage.id == img.id))
    assert res_img.scalar_one_or_none() is None

    res_offer = await test_session.execute(select(RetailerOffer).where(RetailerOffer.id == offer.id))
    assert res_offer.scalar_one_or_none() is None

    res_src = await test_session.execute(select(ProductSource).where(ProductSource.id == source.id))
    assert res_src.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_orphan_insert_rejected(test_session: AsyncSession):
    """Verify that images and offers cannot be created referencing a non-existent product_id."""
    non_existent_uuid = uuid.uuid4()
    service = ProductCatalogService(test_session)

    # Attempting to add an image to a non-existent product must violate foreign key
    with pytest.raises(IntegrityError):
        await service.add_image(
            product_id=non_existent_uuid,
            image_url="https://example.com/orphan.jpg",
        )
        await test_session.commit()
    await test_session.rollback()

    # Attempting to add a retailer offer to a non-existent product must violate foreign key
    with pytest.raises(IntegrityError):
        await service.add_retailer_offer(
            product_id=non_existent_uuid,
            retailer="amazon",
            price=50.0,
        )
        await test_session.commit()
    await test_session.rollback()
