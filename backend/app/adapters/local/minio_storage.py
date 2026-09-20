"""Local MinIO storage adapter implementing StorageService."""

import asyncio
from datetime import timedelta
import io
import time
from typing import Any, Dict, Optional
from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.logging import logger
from app.services.storage import StorageService


class MinioStorageService(StorageService):
    """Local MinIO object storage adapter.

    Encapsulates all MinIO client operations and executes blocking I/O calls
    asynchronously using the running event loop's default executor.
    """

    def __init__(self):
        self._client: Optional[Minio] = None
        self._bucket: str = settings.STORAGE_BUCKET

    def _get_clean_endpoint(self) -> str:
        """Strip http:// or https:// scheme for the MinIO client SDK."""
        ep = settings.STORAGE_ENDPOINT
        for prefix in ("http://", "https://"):
            if ep.startswith(prefix):
                ep = ep[len(prefix):]
        return ep.rstrip("/")

    async def connect(self) -> None:
        """Initialize the MinIO client and ensure the storage bucket exists."""
        if not self._client:
            endpoint = self._get_clean_endpoint()
            self._client = Minio(
                endpoint,
                access_key=settings.STORAGE_ACCESS_KEY,
                secret_key=settings.STORAGE_SECRET_KEY,
                secure=settings.STORAGE_SECURE,
            )
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._ensure_bucket)
            logger.info(
                "Connected to local MinIO storage",
                extra={"endpoint": endpoint, "bucket": self._bucket},
            )

    def _ensure_bucket(self) -> None:
        """Synchronously check and create bucket if not already present."""
        if self._client:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
                logger.info(f"Created MinIO bucket: {self._bucket}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform a live health probe verifying bucket availability and latency."""
        start = time.perf_counter()
        try:
            if not self._client:
                await self.connect()
            loop = asyncio.get_running_loop()
            exists = await loop.run_in_executor(
                None, self._client.bucket_exists, self._bucket
            )
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "ok" if exists else "degraded",
                "latency_ms": latency,
                "details": {"bucket": self._bucket, "bucket_exists": exists, "provider": "minio"},
            }
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "error",
                "latency_ms": latency,
                "error": str(exc),
            }

    async def put_object(
        self,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload binary data to MinIO under the specified object key."""
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _upload():
            stream = io.BytesIO(data)
            self._client.put_object(
                self._bucket,
                clean_name,
                stream,
                length=len(data),
                content_type=content_type,
            )

        await loop.run_in_executor(None, _upload)
        return clean_name

    async def get_object(self, object_name: str) -> Optional[bytes]:
        """Fetch binary data of an object from MinIO."""
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _fetch() -> Optional[bytes]:
            try:
                response = self._client.get_object(self._bucket, clean_name)
                try:
                    return response.read()
                finally:
                    response.close()
                    response.release_conn()
            except S3Error as exc:
                if exc.code in ("NoSuchKey", "NoSuchBucket"):
                    return None
                raise

        return await loop.run_in_executor(None, _fetch)

    async def delete_object(self, object_name: str) -> bool:
        """Remove an object from MinIO."""
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _delete():
            try:
                self._client.remove_object(self._bucket, clean_name)
                return True
            except S3Error as exc:
                if exc.code == "NoSuchKey":
                    return True
                raise

        return await loop.run_in_executor(None, _delete)

    async def exists(self, object_name: str) -> bool:
        """Check if an object exists in MinIO via stat metadata."""
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _stat() -> bool:
            try:
                self._client.stat_object(self._bucket, clean_name)
                return True
            except S3Error as exc:
                if exc.code in ("NoSuchKey", "NoSuchBucket"):
                    return False
                raise

        return await loop.run_in_executor(None, _stat)

    async def get_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """Generate a presigned GET URL for downloading/viewing an object."""
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _presign() -> str:
            return self._client.presigned_get_object(
                self._bucket,
                clean_name,
                expires=timedelta(seconds=expires_seconds),
            )

        return await loop.run_in_executor(None, _presign)


# Backwards compatibility alias
LocalMinioStorageService = MinioStorageService
