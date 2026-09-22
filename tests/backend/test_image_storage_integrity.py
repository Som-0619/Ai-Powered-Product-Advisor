"""Stage 3 — Automated Product Image, Data Validation and Storage Integrity Tests.

Validates all 12 required integrity test suites from Section 20, plus the critical
cross-product isolation regression test from Section 21:
1. test_image_belongs_to_product()
2. test_variant_image_belongs_to_variant()
3. test_storage_key_matches_product()
4. test_primary_image_uniqueness()
5. test_image_object_exists()
6. test_no_cross_product_image_mapping()
7. test_no_index_based_image_mapping()
8. test_invalid_image_rejected()
9. test_orphan_image_detected()
10. test_product_without_image_does_not_use_other_product_image()
11. test_product_image_url_generation()
12. test_storage_service_abstraction()
13. test_critical_cross_product_regression()
"""

import inspect
import os
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.catalog import Product, ProductVariant
from app.models.media import ProductImage, CANONICAL_IMAGE_TYPES
from app.services.product_catalog_service import ProductCatalogService
from app.services.product_image_service import (
    ProductImageService,
    ImageOwnershipError,
    ImageNotFoundError,
)
from app.services.image_validator import ImageValidator, ImageValidationError
from app.services.storage import StorageService, StoragePath
from app.adapters.local.minio_storage import MinioStorageService
from app.adapters.aws.s3_storage import AwsS3StorageService

TEST_DB_URL = os.environ.get(
    "LOCAL_POSTGRES_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://advisor_user:advisor_password@127.0.0.1:5432/product_advisor",
    ),
)
if "postgres:5432" in TEST_DB_URL:
    TEST_DB_URL = TEST_DB_URL.replace("postgres:5432", "127.0.0.1:5432")


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(db_engine):
    maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def storage_client():
    client = MinioStorageService()
    await client.connect()
    return client


# =============================================================================
# 1. test_image_belongs_to_product()
# =============================================================================
@pytest.mark.asyncio
async def test_image_belongs_to_product(test_session: AsyncSession, storage_client: StorageService):
    """Every ProductImage MUST belong to exactly one canonical product.

    Image service MUST reject retrieving an image belonging to Product A using Product B's ID.
    """
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod_a = await catalog.create_product(
        title="Ownership Test Product A",
        slug=f"ownership-test-a-{uuid.uuid4().hex[:6]}",
        brand="Apple",
        model="MacBook Pro A",
        category="Laptops",
    )
    prod_b = await catalog.create_product(
        title="Ownership Test Product B",
        slug=f"ownership-test-b-{uuid.uuid4().hex[:6]}",
        brand="Dell",
        model="XPS B",
        category="Laptops",
    )

    img_a = await catalog.add_image(
        product_id=prod_a.id,
        image_url="https://cdn.example.com/img-a.webp",
        image_type="primary",
        storage_key=f"products/{prod_a.id}/primary.webp",
    )
    await test_session.flush()

    # 1. Image fetched with correct product_id succeeds
    resolved = await img_service.get_image(prod_a.id, img_a.id)
    assert resolved.id == img_a.id
    assert resolved.product_id == prod_a.id

    # 2. Image fetched with mismatched product_id MUST be rejected
    with pytest.raises(ImageOwnershipError) as exc:
        await img_service.get_image(prod_b.id, img_a.id)
    assert "Image ownership violation" in str(exc.value)


# =============================================================================
# 2. test_variant_image_belongs_to_variant()
# =============================================================================
@pytest.mark.asyncio
async def test_variant_image_belongs_to_variant(test_session: AsyncSession, storage_client: StorageService):
    """Variant-specific images must reference a variant that actually belongs to product_id.

    Reject image where image.product_id = Product A but variant belongs to Product B.
    """
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod_a = await catalog.create_product(
        title="Variant Test Phone A",
        slug=f"variant-test-a-{uuid.uuid4().hex[:6]}",
        brand="Google",
        model="Pixel 9",
        category="Smartphones",
    )
    prod_b = await catalog.create_product(
        title="Variant Test Phone B",
        slug=f"variant-test-b-{uuid.uuid4().hex[:6]}",
        brand="Samsung",
        model="Galaxy S24",
        category="Smartphones",
    )

    var_b = await catalog.create_variant(
        product_id=prod_b.id,
        variant_name="Samsung 256GB Black",
        sku=f"SKU-SAM-{uuid.uuid4().hex[:6]}",
    )
    await test_session.flush()

    # Reject adding image to Product A referencing Variant B
    with pytest.raises(ValueError) as exc:
        await catalog.add_image(
            product_id=prod_a.id,
            image_url="https://cdn.example.com/img-cross.webp",
            variant_id=var_b.id,
            storage_key=f"products/{prod_a.id}/variants/{var_b.id}/primary.webp",
        )
    assert "Variant ownership mismatch" in str(exc.value)

    # Reject querying Product A for images of Variant B
    with pytest.raises(ImageOwnershipError) as exc_query:
        await img_service.get_images_for_variant(prod_a.id, var_b.id)
    assert "Variant mismatch" in str(exc_query.value)


# =============================================================================
# 3. test_storage_key_matches_product()
# =============================================================================
@pytest.mark.asyncio
async def test_storage_key_matches_product(test_session: AsyncSession):
    """Every storage key must strictly belong to the same canonical product_id."""
    pid_a = uuid.uuid4()
    pid_b = uuid.uuid4()
    img_id = uuid.uuid4()

    valid_primary = ProductImageService.build_canonical_storage_key(pid_a, "primary")
    assert valid_primary == f"products/{pid_a}/primary.webp"
    assert ProductImageService.validate_storage_key_matches_product(pid_a, valid_primary) is True

    # Valid views
    for view in ("front", "back", "left", "right", "ports", "camera", "gallery"):
        key = ProductImageService.build_canonical_storage_key(pid_a, view, image_id=img_id)
        assert ProductImageService.validate_storage_key_matches_product(pid_a, key) is True

    # Invalid: key contains pid_a but validated against pid_b
    assert ProductImageService.validate_storage_key_matches_product(pid_b, valid_primary) is False

    # Invalid: path traversal attacks
    assert ProductImageService.validate_storage_key_matches_product(pid_a, f"products/{pid_a}/../etc/passwd") is False
    assert ProductImageService.validate_storage_key_matches_product(pid_a, f"/products/{pid_a}/primary.webp") is False
    assert ProductImageService.validate_storage_key_matches_product(pid_a, f"products/{pid_a}/primary\x00.webp") is False


# =============================================================================
# 4. test_primary_image_uniqueness()
# =============================================================================
@pytest.mark.asyncio
async def test_primary_image_uniqueness(test_session: AsyncSession, storage_client: StorageService):
    """Every product must have at most ONE primary image."""
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod = await catalog.create_product(
        title="Single Primary Test Phone",
        slug=f"primary-uniq-test-{uuid.uuid4().hex[:6]}",
        brand="OnePlus",
        model="Nord 4",
        category="Smartphones",
    )

    # 1. Add first primary image
    img1 = await catalog.add_image(
        product_id=prod.id,
        image_url="https://cdn.example.com/phone-front.webp",
        image_type="primary",
        is_primary=True,
        storage_key=f"products/{prod.id}/primary.webp",
    )
    await test_session.flush()

    primary_1 = await img_service.get_primary_image(prod.id)
    assert primary_1.id == img1.id

    # 2. Add second image and set it as primary via ProductImageService
    img2 = await catalog.add_image(
        product_id=prod.id,
        image_url="https://cdn.example.com/phone-side.webp",
        image_type="left",
        is_primary=False,
        storage_key=f"products/{prod.id}/left.webp",
    )
    await test_session.flush()

    await img_service.set_primary_image(prod.id, img2.id)

    # Re-query all images for this product; exactly one must have is_primary = True
    images = await img_service.get_images(prod.id)
    primaries = [im for im in images if im.is_primary]
    assert len(primaries) == 1
    assert primaries[0].id == img2.id

    # 3. Direct DB insert of a duplicate is_primary=True MUST fail partial unique index
    dup_img = ProductImage(
        id=uuid.uuid4(),
        product_id=prod.id,
        image_type="primary",
        is_primary=True,
        storage_key=f"products/{prod.id}/primary_dup.webp",
    )
    test_session.add(dup_img)
    with pytest.raises(IntegrityError):
        await test_session.flush()
    await test_session.rollback()


# =============================================================================
# 5. test_image_object_exists()
# =============================================================================
@pytest.mark.asyncio
async def test_image_object_exists(test_session: AsyncSession, storage_client: StorageService):
    """Verify that stored image objects actually exist in MinIO and are readable."""
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod = await catalog.create_product(
        title="Storage Object Existence Test Device",
        slug=f"storage-obj-exist-{uuid.uuid4().hex[:6]}",
        brand="Raspberry Pi",
        model="Pi 5",
        category="Single Board Computers",
    )

    # Generate valid synthetic WEBP image payload
    sample_payload = ImageValidator.create_synthetic_webp(300, 300, color=(16, 185, 129))

    # Upload and register image through ProductImageService
    registered_img = await img_service.upload_and_register_image(
        product_id=prod.id,
        data=sample_payload,
        image_type="primary",
        is_primary=True,
    )
    await test_session.flush()

    # 1. Verify object exists in storage
    exists = await storage_client.exists(registered_img.storage_key)
    assert exists is True, f"Object {registered_img.storage_key} does not exist in storage"

    # 2. Verify payload is readable and valid
    fetched_data = await storage_client.get_object(registered_img.storage_key)
    assert fetched_data is not None
    assert len(fetched_data) > 0

    val = ImageValidator.validate_image_bytes(fetched_data)
    assert val["is_valid"] is True
    assert val["format"] == "WEBP"
    assert val["dimensions"] == (300, 300)


# =============================================================================
# 6. test_no_cross_product_image_mapping()
# =============================================================================
@pytest.mark.asyncio
async def test_no_cross_product_image_mapping(test_session: AsyncSession, storage_client: StorageService):
    """Two products must never share images or cross-reference each other."""
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod_1 = await catalog.create_product(
        title="Discrete Product 1",
        slug=f"discrete-1-{uuid.uuid4().hex[:6]}",
        brand="Sony",
        model="WH-1000XM5",
        category="Headphones",
    )
    prod_2 = await catalog.create_product(
        title="Discrete Product 2",
        slug=f"discrete-2-{uuid.uuid4().hex[:6]}",
        brand="Bose",
        model="QC Ultra",
        category="Headphones",
    )

    img_1 = await catalog.add_image(
        product_id=prod_1.id,
        image_url="https://cdn.example.com/sony-xm5.webp",
        image_type="primary",
        is_primary=True,
        storage_key=f"products/{prod_1.id}/primary.webp",
    )
    img_2 = await catalog.add_image(
        product_id=prod_2.id,
        image_url="https://cdn.example.com/bose-qc.webp",
        image_type="primary",
        is_primary=True,
        storage_key=f"products/{prod_2.id}/primary.webp",
    )
    await test_session.flush()

    # Images for Product 1 must not contain Image 2
    images_1 = await img_service.get_images(prod_1.id)
    assert any(im.id == img_1.id for im in images_1)
    assert not any(im.id == img_2.id for im in images_1)

    # Images for Product 2 must not contain Image 1
    images_2 = await img_service.get_images(prod_2.id)
    assert any(im.id == img_2.id for im in images_2)
    assert not any(im.id == img_1.id for im in images_2)


# =============================================================================
# 7. test_no_index_based_image_mapping()
# =============================================================================
@pytest.mark.asyncio
async def test_no_index_based_image_mapping(test_session: AsyncSession, storage_client: StorageService):
    """Image resolution MUST be by product_id and image_id, never positional or index-based."""
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod = await catalog.create_product(
        title="Multi-View Camera",
        slug=f"multi-view-cam-{uuid.uuid4().hex[:6]}",
        brand="Canon",
        model="EOS R6",
        category="Cameras",
    )

    # Add 4 images in arbitrary order
    types = ["back", "ports", "primary", "front"]
    created_map = {}
    for t in types:
        im = await catalog.add_image(
            product_id=prod.id,
            image_url=f"https://cdn.example.com/canon-{t}.webp",
            image_type=t,
            is_primary=(t == "primary"),
            storage_key=f"products/{prod.id}/{t}.webp",
        )
        created_map[t] = im
    await test_session.flush()

    # Querying primary must resolve strictly by identity, not position 0
    resolved_primary = await img_service.get_primary_image(prod.id)
    assert resolved_primary.id == created_map["primary"].id
    assert resolved_primary.image_type == "primary"

    # Querying specific image by ID succeeds regardless of where it appears in list
    for t in types:
        resolved_img = await img_service.get_image(prod.id, created_map[t].id)
        assert resolved_img.id == created_map[t].id
        assert resolved_img.image_type == t


# =============================================================================
# 8. test_invalid_image_rejected()
# =============================================================================
@pytest.mark.asyncio
async def test_invalid_image_rejected(test_session: AsyncSession, storage_client: StorageService):
    """Reject corrupt payloads, zero-byte files, and HTML masquerading as images."""
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod = await catalog.create_product(
        title="Rejection Test Device",
        slug=f"rejection-test-{uuid.uuid4().hex[:6]}",
        brand="Test",
        model="Model X",
        category="Consumer Electronics",
    )

    # 1. Zero-byte payload
    with pytest.raises(ValueError) as exc1:
        await img_service.upload_and_register_image(
            product_id=prod.id,
            data=b"",
            image_type="primary",
        )
    assert "zero_byte_file" in str(exc1.value)

    # 2. HTML masquerade
    html_masquerade = b"<!DOCTYPE html><html><head><title>404</title></head><body>Not Found</body></html>"
    with pytest.raises(ValueError) as exc2:
        await img_service.upload_and_register_image(
            product_id=prod.id,
            data=html_masquerade,
            image_type="primary",
        )
    assert "html_file_pretending_to_be_image" in str(exc2.value)

    # 3. Corrupt garbage data
    with pytest.raises(ValueError) as exc3:
        await img_service.upload_and_register_image(
            product_id=prod.id,
            data=b"random_corrupt_binary_header_garbage_data",
            image_type="primary",
        )
    assert "broken_or_unreadable_image" in str(exc3.value)


# =============================================================================
# 9. test_orphan_image_detected()
# =============================================================================
@pytest.mark.asyncio
async def test_orphan_image_detected(test_session: AsyncSession, storage_client: StorageService):
    """Objects existing in storage without a corresponding database record must be detected as orphans."""
    orphan_key = f"products/{uuid.uuid4()}/orphan_untracked.webp"

    # Put object directly in storage without DB registration
    dummy_payload = ImageValidator.create_synthetic_webp(100, 100)
    await storage_client.put_object(orphan_key, dummy_payload, content_type="image/webp")

    # Verify object exists in storage
    assert await storage_client.exists(orphan_key) is True

    # Verify no DB record exists for this storage key
    stmt = select(ProductImage).where(ProductImage.storage_key == orphan_key)
    res = await test_session.execute(stmt)
    assert res.scalar_one_or_none() is None

    # Detect orphan
    all_objs = set(await storage_client.list_objects(prefix="products/"))
    assert orphan_key in all_objs

    # Clean up test object
    await storage_client.delete_object(orphan_key)


# =============================================================================
# 10. test_product_without_image_does_not_use_other_product_image()
# =============================================================================
@pytest.mark.asyncio
async def test_product_without_image_does_not_use_other_product_image(
    test_session: AsyncSession,
    storage_client: StorageService,
):
    """A product with no images MUST return None/empty, never an image from another product."""
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod_with_img = await catalog.create_product(
        title="Laptop With Real Image",
        slug=f"laptop-with-img-{uuid.uuid4().hex[:6]}",
        brand="Apple",
        model="MacBook Air",
        category="Laptops",
    )
    prod_without_img = await catalog.create_product(
        title="Sensors Without Image",
        slug=f"sensors-without-img-{uuid.uuid4().hex[:6]}",
        brand="Bosch",
        model="BME680 Sensor",
        category="Electronic Components",
    )

    real_img = await catalog.add_image(
        product_id=prod_with_img.id,
        image_url="https://cdn.example.com/macbook-air.webp",
        image_type="primary",
        is_primary=True,
        storage_key=f"products/{prod_with_img.id}/primary.webp",
    )
    await test_session.flush()

    # Product without image MUST return None for primary
    primary = await img_service.get_primary_image(prod_without_img.id)
    assert primary is None

    # Product without image MUST return [] for images
    images = await img_service.get_images(prod_without_img.id)
    assert images == []


# =============================================================================
# 11. test_product_image_url_generation()
# =============================================================================
@pytest.mark.asyncio
async def test_product_image_url_generation(test_session: AsyncSession, storage_client: StorageService):
    """Verify safe URL generation via StorageService without exposing storage internals."""
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    prod = await catalog.create_product(
        title="URL Generation Test Headphones",
        slug=f"url-gen-test-{uuid.uuid4().hex[:6]}",
        brand="Sennheiser",
        model="HD 600",
        category="Headphones",
    )

    payload = ImageValidator.create_synthetic_webp(200, 200)
    img = await img_service.upload_and_register_image(
        product_id=prod.id,
        data=payload,
        image_type="primary",
        is_primary=True,
    )
    await test_session.flush()

    # Generate presigned or public URL
    url = await img_service.get_image_url(prod.id, img.id)
    assert url is not None
    assert isinstance(url, str)
    assert "http" in url
    # Ensure key product identifier is present
    assert str(prod.id) in url or "product-advisor" in url


# =============================================================================
# 12. test_storage_service_abstraction()
# =============================================================================
def test_storage_service_abstraction():
    """Verify that product/business logic never imports MinIO or boto3 directly."""
    import app.services.product_catalog_service as pcs
    import app.services.product_image_service as pis
    import app.services.image_validator as iv

    for mod in (pcs, pis, iv):
        src = inspect.getsource(mod)
        assert "import minio" not in src
        assert "from minio" not in src
        assert "import boto3" not in src
        assert "from boto3" not in src


# =============================================================================
# 13. test_critical_cross_product_regression() (Section 21)
# =============================================================================
@pytest.mark.asyncio
async def test_critical_cross_product_regression(test_session: AsyncSession, storage_client: StorageService):
    """Critical regression test from Section 21:

    Create:
    Product A, Product B
    Image A -> Product A, Image B -> Product B
    Request: get_primary_image(Product A)
    Expected: Image A. It MUST NEVER return Image B.
    Repeat with multiple products.
    """
    catalog = ProductCatalogService(test_session)
    img_service = ProductImageService(test_session, storage_client)

    # Test across 3 distinct products in different categories
    test_specs = [
        ("Product A", "Laptop Alpha", "Laptops"),
        ("Product B", "Smartphone Beta", "Smartphones"),
        ("Product C", "Headphones Gamma", "Headphones"),
    ]

    created_products = []
    created_images = []

    for name, model, cat in test_specs:
        p = await catalog.create_product(
            title=name,
            slug=f"cross-reg-{uuid.uuid4().hex[:6]}",
            brand="RegBrand",
            model=model,
            category=cat,
        )
        img = await catalog.add_image(
            product_id=p.id,
            image_url=f"https://cdn.example.com/{model.lower().replace(' ', '-')}.webp",
            image_type="primary",
            is_primary=True,
            storage_key=f"products/{p.id}/primary.webp",
        )
        created_products.append(p)
        created_images.append(img)

    await test_session.flush()

    # Strictly verify each product retrieves ONLY its own primary image
    for idx, prod in enumerate(created_products):
        primary = await img_service.get_primary_image(prod.id)
        assert primary is not None
        assert primary.id == created_images[idx].id
        assert primary.product_id == prod.id

        # Verify it NEVER matches any other product's image
        for other_idx, other_img in enumerate(created_images):
            if other_idx != idx:
                assert primary.id != other_img.id
                assert primary.product_id != other_img.product_id
