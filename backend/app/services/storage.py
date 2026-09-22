"""Abstract base class for Object Storage Service and logical path definitions."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Set


class StoragePath:
    """Logical storage directory structure.

    All stored files in Product Advisor must be organized under one of these
    six standard prefixes to ensure clear separation and clean retention policies:
    - raw/: Unprocessed crawler HTML dumps, raw scraped JSON, raw PDFs
    - products/: Product specification exports, catalog backups
    - reviews/: Review text bodies, external review sentiment dumps
    - documents/: Technical manuals, datasheets, schematics, application notes
    - images/: High-res product images, port diagrams, component pinouts
    - web/: Rendered static web assets, crawl screenshots
    """

    RAW = "raw"
    PRODUCTS = "products"
    REVIEWS = "reviews"
    DOCUMENTS = "documents"
    IMAGES = "images"
    WEB = "web"

    VALID_PREFIXES: Set[str] = {RAW, PRODUCTS, REVIEWS, DOCUMENTS, IMAGES, WEB}

    @classmethod
    def build(cls, prefix: str, *parts: str) -> str:
        """Construct a validated logical storage key path.

        Example:
            StoragePath.build(StoragePath.DOCUMENTS, "datasheets", "esp32.pdf")
            -> "documents/datasheets/esp32.pdf"
        """
        clean_prefix = prefix.strip("/")
        if clean_prefix not in cls.VALID_PREFIXES:
            raise ValueError(
                f"Invalid storage prefix '{prefix}'. Allowed prefixes are: {sorted(cls.VALID_PREFIXES)}"
            )
        cleaned_parts = [p.strip("/") for p in parts if p.strip("/")]
        if not cleaned_parts:
            raise ValueError("At least one filename or subpath must be provided after prefix.")
        return f"{clean_prefix}/{'/'.join(cleaned_parts)}"

    @classmethod
    def validate_safe_key(cls, key: str, expected_product_id: Optional[Any] = None) -> bool:
        """Validate that a storage key does not contain path traversal, null bytes, or illicit prefixes.

        If expected_product_id is supplied, ensures the key starts with products/{expected_product_id}/.
        """
        if not key or not isinstance(key, str):
            return False
        # Prevent null bytes and path traversal
        if "\x00" in key or ".." in key or key.startswith("/") or key.startswith("\\"):
            return False
        parts = key.split("/")
        if not parts or parts[0] not in cls.VALID_PREFIXES:
            return False
        if expected_product_id is not None:
            pid_str = str(expected_product_id)
            if len(parts) < 2 or parts[0] != cls.PRODUCTS or parts[1] != pid_str:
                return False
        return True

    @classmethod
    def build_product_image_key(
        cls,
        product_id: Any,
        image_type: str,
        image_id: Optional[Any] = None,
        variant_id: Optional[Any] = None,
    ) -> str:
        """Construct canonical Stage 3 image storage key.

        Follows Section 5 rules:
        - products/{product_id}/primary.webp
        - products/{product_id}/{image_type}.webp
        - products/{product_id}/gallery/{image_id}.webp
        - products/{product_id}/variants/{variant_id}/primary.webp
        - products/{product_id}/variants/{variant_id}/gallery/{image_id}.webp
        """
        pid_str = str(product_id).strip("/")
        clean_type = str(image_type).lower().strip("/")

        if variant_id:
            vid_str = str(variant_id).strip("/")
            if clean_type == "gallery" and image_id:
                return f"products/{pid_str}/variants/{vid_str}/gallery/{str(image_id)}.webp"
            return f"products/{pid_str}/variants/{vid_str}/primary.webp"

        if clean_type == "gallery" and image_id:
            return f"products/{pid_str}/gallery/{str(image_id)}.webp"

        return f"products/{pid_str}/{clean_type}.webp"


class StorageService(ABC):
    """Storage service abstraction for MinIO (Local) and Amazon S3 (AWS).

    Application code interacts exclusively with this interface and never directly
    imports or calls the underlying storage provider (MinIO or boto3).
    """

    @abstractmethod
    async def connect(self) -> None:
        """Initialize client connection and ensure bucket exists."""
        pass

    @abstractmethod
    async def list_objects(self, prefix: str = "", recursive: bool = True) -> list[str]:
        """List object keys under the given prefix.

        Args:
            prefix: Key prefix filter (e.g. 'products/').
            recursive: Whether to list recursively down directories.

        Returns:
            List of object key strings.
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verify storage connection and bucket accessibility."""
        pass

    @abstractmethod
    async def put_object(
        self,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Store an object and return its logical path or URI.

        Args:
            object_name: Key / path of the object (e.g. 'documents/specs.pdf')
            data: Binary payload
            content_type: MIME type (e.g. 'application/pdf', 'image/webp')

        Returns:
            Public or canonical path identifier for the object.
        """
        pass

    @abstractmethod
    async def get_object(self, object_name: str) -> Optional[bytes]:
        """Retrieve an object's binary data.

        Args:
            object_name: Key / path of the object.

        Returns:
            Bytes if found, or None if the object does not exist.
        """
        pass

    @abstractmethod
    async def delete_object(self, object_name: str) -> bool:
        """Delete an object from storage.

        Args:
            object_name: Key / path of the object.

        Returns:
            True if deletion was successful or object didn't exist.
        """
        pass

    @abstractmethod
    async def exists(self, object_name: str) -> bool:
        """Check if an object exists in storage without fetching its payload.

        Args:
            object_name: Key / path of the object.

        Returns:
            True if object exists, False otherwise.
        """
        pass

    @abstractmethod
    async def get_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """Generate a presigned or public access URL for the object.

        Args:
            object_name: Key / path of the object.
            expires_seconds: Expiration lifetime for presigned URLs.

        Returns:
            A downloadable or viewable URL string.
        """
        pass

    async def upload(
        self,
        object_name_or_data: Any,
        data_or_name: Optional[Any] = None,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload object to storage.

        Supports both:
            upload(object_name, data, content_type)
            upload(data, object_name, content_type)
        """
        if isinstance(object_name_or_data, (bytes, bytearray)):
            data = object_name_or_data
            object_name = str(data_or_name)
        else:
            object_name = str(object_name_or_data)
            data = data_or_name if isinstance(data_or_name, (bytes, bytearray)) else str(data_or_name or "").encode("utf-8")
        return await self.put_object(object_name, data, content_type)

    async def delete(self, object_name: str) -> bool:
        """Delete an object from storage."""
        return await self.delete_object(object_name)


# Lazy alias imports to avoid circular dependencies
def __getattr__(name: str):
    if name == "MinIOStorage":
        from app.adapters.local.minio_storage import MinIOStorage
        return MinIOStorage
    elif name == "S3Storage":
        from app.adapters.aws.s3_storage import S3Storage
        return S3Storage
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

