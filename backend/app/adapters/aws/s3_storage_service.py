"""AWS S3 Storage adapter alias for backward compatibility."""

from app.adapters.aws.s3_storage import AwsS3StorageService

__all__ = ["AwsS3StorageService"]
