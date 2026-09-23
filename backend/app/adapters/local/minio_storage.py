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
        self._existing_keys: Optional[set] = None

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
            try:
                keys = await self.list_objects(prefix="products/", recursive=True)
                self._existing_keys = set(keys)
            except Exception as exc:
                logger.warning(f"Could not pre-cache MinIO product keys: {exc}")
                self._existing_keys = None
            logger.info(
                "Connected to local MinIO storage",
                extra={"endpoint": endpoint, "bucket": self._bucket, "cached_keys": len(self._existing_keys or set())},
            )

    def _ensure_bucket(self) -> None:
        """Synchronously check and create bucket if not already present, ensuring public read policy."""
        if self._client:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
                logger.info(f"Created MinIO bucket: {self._bucket}")
            import json
            try:
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                            "Resource": [f"arn:aws:s3:::{self._bucket}"],
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self._bucket}/*"],
                        },
                    ],
                }
                self._client.set_bucket_policy(self._bucket, json.dumps(policy))
            except Exception as exc:
                logger.warning(f"Could not set MinIO public read policy: {exc}")

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

    async def list_objects(self, prefix: str = "", recursive: bool = True) -> list[str]:
        """List object keys under the specified prefix."""
        if not self._client:
            await self.connect()

        clean_prefix = prefix.lstrip("/")
        loop = asyncio.get_running_loop()

        def _list():
            objs = self._client.list_objects(self._bucket, prefix=clean_prefix, recursive=recursive)
            return [o.object_name for o in objs]

        return await loop.run_in_executor(None, _list)

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
        if self._existing_keys is not None:
            self._existing_keys.add(clean_name)
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

        res = await loop.run_in_executor(None, _delete)
        if res and self._existing_keys is not None:
            self._existing_keys.discard(clean_name)
        return res

    async def exists(self, object_name: str) -> bool:
        """Check if an object exists in MinIO via cached set or stat metadata."""
        if not object_name or not isinstance(object_name, str):
            return False
        clean_name = object_name.lstrip("/")
        if self._existing_keys is not None:
            return clean_name in self._existing_keys

        if not self._client:
            await self.connect()

        loop = asyncio.get_running_loop()

        def _stat() -> bool:
            try:
                self._client.stat_object(self._bucket, clean_name)
                return True
            except Exception:
                return False

        return await loop.run_in_executor(None, _stat)

    async def get_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """Generate a valid public or presigned GET URL for viewing an object in browser."""
        clean_name = object_name.lstrip("/")
        endpoint = settings.STORAGE_ENDPOINT
        if "minio:9000" in endpoint:
            endpoint = endpoint.replace("minio:9000", "localhost:9000")
        if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
            endpoint = f"http://{endpoint}"
        return f"{endpoint.rstrip('/')}/{self._bucket}/{clean_name}"


# Backwards compatibility and canonical aliases
LocalMinioStorageService = MinioStorageService
MinIOStorage = MinioStorageService
