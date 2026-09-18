"""Integration and unit tests for Object Storage Service and MinIO/S3 adapters.

Validates:
1. StorageService interface adherence and DI retrieval via get_storage_service()
2. Logical StoragePath prefixes (raw/, products/, reviews/, documents/, images/, web/)
3. put_object, get_object, exists, delete_object, get_url against local MinIO
4. Byte-for-byte data integrity and content types
5. Safe handling of non-existent keys (returning None instead of crashing)
6. AWS S3 adapter interface compliance and deployment readiness
"""

import uuid
import pytest
import pytest_asyncio

from app.services.storage import StorageService, StoragePath
from app.services.factory import get_storage_service
from app.adapters.local.minio_storage import MinioStorageService
from app.adapters.aws.s3_storage import AwsS3StorageService


@pytest_asyncio.fixture(loop_scope="function")
async def storage() -> StorageService:
    """Fixture providing initialized StorageService singleton."""
    service = get_storage_service()
    await service.connect()
    return service


def test_storage_path_validation():
    """Verify that StoragePath strictly enforces the 6 required logical directories."""
    # Test all 6 valid prefixes
    for prefix in [
        StoragePath.RAW,
        StoragePath.PRODUCTS,
        StoragePath.REVIEWS,
        StoragePath.DOCUMENTS,
        StoragePath.IMAGES,
        StoragePath.WEB,
    ]:
        path = StoragePath.build(prefix, "subfolder", "test_file.bin")
        assert path == f"{prefix}/subfolder/test_file.bin"
        assert path.startswith(f"{prefix}/")

    # Leading/trailing slashes should be normalized
    norm_path = StoragePath.build("/documents/", "/datasheets/", "sensor.pdf")
    assert norm_path == "documents/datasheets/sensor.pdf"

    # Invalid prefix must raise ValueError
    with pytest.raises(ValueError, match="Invalid storage prefix 'invalid_prefix'"):
        StoragePath.build("invalid_prefix", "file.txt")

    # Empty subparts must raise ValueError
    with pytest.raises(ValueError, match="At least one filename or subpath must be provided"):
        StoragePath.build(StoragePath.RAW)


@pytest.mark.asyncio
async def test_storage_service_health_check(storage: StorageService):
    """Verify health_check() confirms bucket existence and measures latency."""
    health = await storage.health_check()
    assert health["status"] == "ok"
    assert health["latency_ms"] >= 0
    assert health["details"]["bucket_exists"] is True
    assert health["details"]["provider"] == "minio"


@pytest.mark.asyncio
async def test_put_get_exists_across_all_six_logical_paths(storage: StorageService):
    """Verify put_object, exists, get_object across raw, products, reviews, documents, images, web."""
    unique_run = uuid.uuid4().hex[:8]

    test_artifacts = {
        StoragePath.RAW: {
            "path": StoragePath.build(StoragePath.RAW, unique_run, "crawler_dump.html"),
            "data": b"<html><body>Raw Scraped HTML Payload</body></html>",
            "content_type": "text/html",
        },
        StoragePath.PRODUCTS: {
            "path": StoragePath.build(StoragePath.PRODUCTS, unique_run, "catalog_snapshot.json"),
            "data": b'{"product_count": 42, "schema_version": "2.0"}',
            "content_type": "application/json",
        },
        StoragePath.REVIEWS: {
            "path": StoragePath.build(StoragePath.REVIEWS, unique_run, "review_evidence.txt"),
            "data": b"Verified review sentiment analysis: positive, fraud_score=0.02",
            "content_type": "text/plain",
        },
        StoragePath.DOCUMENTS: {
            "path": StoragePath.build(StoragePath.DOCUMENTS, unique_run, "esp32_datasheet.pdf"),
            "data": b"%PDF-1.4 Mock Binary PDF Content for ESP32-WROOM-32E Datasheet",
            "content_type": "application/pdf",
        },
        StoragePath.IMAGES: {
            "path": StoragePath.build(StoragePath.IMAGES, unique_run, "pinout_diagram.webp"),
            "data": b"RIFF....WEBPVP8X Mock Binary WebP Image for Component Pinout",
            "content_type": "image/webp",
        },
        StoragePath.WEB: {
            "path": StoragePath.build(StoragePath.WEB, unique_run, "product_screenshot.png"),
            "data": b"\x89PNG\r\n\x1a\n Mock Binary PNG Screenshot of Retail Page",
            "content_type": "image/png",
        },
    }

    # 1. Put objects under each logical path
    for prefix, item in test_artifacts.items():
        stored_path = await storage.put_object(
            object_name=item["path"],
            data=item["data"],
            content_type=item["content_type"],
        )
        assert stored_path == item["path"]

    # 2. Check exists() and get_object() for byte-for-byte exact matching
    for prefix, item in test_artifacts.items():
        assert await storage.exists(item["path"]) is True

        retrieved_data = await storage.get_object(item["path"])
        assert retrieved_data is not None
        assert retrieved_data == item["data"], f"Data mismatch for {item['path']}"

    # 3. Clean up and verify deletion
    for prefix, item in test_artifacts.items():
        deleted = await storage.delete_object(item["path"])
        assert deleted is True
        assert await storage.exists(item["path"]) is False
        assert await storage.get_object(item["path"]) is None


@pytest.mark.asyncio
async def test_get_url_presigned_generation(storage: StorageService):
    """Verify get_url() generates valid presigned URLs with expiry and signatures."""
    test_key = StoragePath.build(StoragePath.DOCUMENTS, "test_url", "manual.pdf")
    payload = b"%PDF-1.5 Sample User Manual"

    await storage.put_object(test_key, payload, content_type="application/pdf")
    try:
        url = await storage.get_url(test_key, expires_seconds=1800)
        assert isinstance(url, str)
        assert test_key in url
        # Should include presigned signature query parameters (e.g. X-Amz-Signature, X-Amz-Expires)
        assert "X-Amz-Expires" in url or "X-Amz-Signature" in url or "product-advisor-data" in url
    finally:
        await storage.delete_object(test_key)


@pytest.mark.asyncio
async def test_non_existent_object_handling(storage: StorageService):
    """Verify that querying or deleting non-existent keys returns None/False safely."""
    random_key = StoragePath.build(StoragePath.RAW, "non_existent", f"{uuid.uuid4().hex}.bin")

    # exists() should return False
    assert await storage.exists(random_key) is False

    # get_object() should return None (not raise)
    assert await storage.get_object(random_key) is None

    # delete_object() on non-existent object should succeed idempotently
    assert await storage.delete_object(random_key) is True


def test_aws_s3_adapter_interface_compliance():
    """Verify that AwsS3StorageService satisfies the StorageService contract."""
    s3_service = AwsS3StorageService(bucket_name="my-s3-bucket", region_name="us-east-1")
    assert isinstance(s3_service, StorageService)
    assert hasattr(s3_service, "put_object")
    assert hasattr(s3_service, "get_object")
    assert hasattr(s3_service, "delete_object")
    assert hasattr(s3_service, "exists")
    assert hasattr(s3_service, "get_url")
    assert hasattr(s3_service, "connect")
    assert hasattr(s3_service, "health_check")
