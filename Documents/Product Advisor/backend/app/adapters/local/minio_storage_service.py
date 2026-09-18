"""Local MinIO storage adapter alias for backward compatibility."""

from app.adapters.local.minio_storage import MinioStorageService, LocalMinioStorageService

__all__ = ["MinioStorageService", "LocalMinioStorageService"]
