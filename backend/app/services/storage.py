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
