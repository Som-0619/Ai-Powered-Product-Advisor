"""Amazon Web Services (AWS) S3 Storage adapter implementation.

Prepared for AWS production deployment. Implements the StorageService interface
using boto3 client patterns while safely handling unconfigured local environments.
"""

import asyncio
from datetime import timedelta
import io
import time
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logging import logger
from app.services.storage import StorageService

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    ClientError = Exception


class AwsS3StorageService(StorageService):
    """Production AWS S3 Storage Adapter.

    Handles S3 authentication via IAM roles (ECS/EKS/EC2) or environment credentials.
    Ready for AWS deployment without requiring application changes.
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        self._bucket = bucket_name or settings.STORAGE_BUCKET
        self._region = region_name or settings.STORAGE_REGION
        self._client = None

    def _ensure_boto3(self) -> None:
        if not BOTO3_AVAILABLE:
            raise RuntimeError(
                "AWS S3 storage adapter requires 'boto3' to be installed. "
                "Add 'boto3' to requirements when deploying to AWS environment."
            )

    async def connect(self) -> None:
        """Initialize boto3 S3 client with regional configuration."""
        self._ensure_boto3()
        if not self._client:
            loop = asyncio.get_running_loop()

            def _init_client():
                return boto3.client("s3", region_name=self._region)

            self._client = await loop.run_in_executor(None, _init_client)
            logger.info(
                "Initialized AWS S3 storage client",
                extra={"bucket": self._bucket, "region": self._region},
            )

    async def health_check(self) -> Dict[str, Any]:
        """Perform a head-bucket check to verify permissions and accessibility."""
        start = time.perf_counter()
        if not BOTO3_AVAILABLE:
            return {
                "status": "unconfigured",
                "details": {"adapter": "aws_s3", "note": "boto3 not installed for local dev"},
            }

        try:
            if not self._client:
                await self.connect()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: self._client.head_bucket(Bucket=self._bucket))
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "ok",
                "latency_ms": latency,
                "details": {"bucket": self._bucket, "provider": "aws_s3"},
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
        """Upload an object to S3 bucket."""
        self._ensure_boto3()
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _upload():
            self._client.put_object(
                Bucket=self._bucket,
                Key=clean_name,
                Body=data,
                ContentType=content_type,
            )

        await loop.run_in_executor(None, _upload)
        return clean_name

    async def get_object(self, object_name: str) -> Optional[bytes]:
        """Fetch object binary data from S3."""
        self._ensure_boto3()
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _fetch() -> Optional[bytes]:
            try:
                resp = self._client.get_object(Bucket=self._bucket, Key=clean_name)
                return resp["Body"].read()
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code")
                if error_code in ("NoSuchKey", "404"):
                    return None
                raise

        return await loop.run_in_executor(None, _fetch)

    async def delete_object(self, object_name: str) -> bool:
        """Delete an object from S3."""
        self._ensure_boto3()
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _delete():
            try:
                self._client.delete_object(Bucket=self._bucket, Key=clean_name)
                return True
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code")
                if error_code == "NoSuchKey":
                    return True
                raise

        return await loop.run_in_executor(None, _delete)

    async def exists(self, object_name: str) -> bool:
        """Check if an object exists in S3 via head_object."""
        self._ensure_boto3()
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _head() -> bool:
            try:
                self._client.head_object(Bucket=self._bucket, Key=clean_name)
                return True
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code")
                if error_code in ("404", "NoSuchKey"):
                    return False
                raise

        return await loop.run_in_executor(None, _head)

    async def get_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """Generate a presigned GET URL for an S3 object."""
        self._ensure_boto3()
        if not self._client:
            await self.connect()

        clean_name = object_name.lstrip("/")
        loop = asyncio.get_running_loop()

        def _presign() -> str:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": clean_name},
                ExpiresIn=expires_seconds,
            )

        return await loop.run_in_executor(None, _presign)
