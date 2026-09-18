"""Configuration settings for Product Advisor."""

from typing import List, Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core environment
    ENVIRONMENT: Literal["local", "aws"] = "local"
    PROJECT_NAME: str = "Product Advisor"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # PostgreSQL Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "product_advisor"
    POSTGRES_USER: str = "advisor_user"
    POSTGRES_PASSWORD: str = "advisor_password"
    DATABASE_URL: Optional[str] = None

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # OpenSearch
    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USE_SSL: bool = False
    OPENSEARCH_VERIFY_CERTS: bool = False
    OPENSEARCH_USERNAME: str = "admin"
    OPENSEARCH_PASSWORD: str = "admin"

    # Redis Cache & Local Queue
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Object Storage (MinIO local, S3 on AWS)
    STORAGE_PROVIDER: Literal["minio", "s3"] = "minio"
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "product-advisor-data"
    STORAGE_REGION: str = "us-east-1"
    STORAGE_SECURE: bool = False

    # Queue Provider (Redis local, SQS on AWS)
    QUEUE_PROVIDER: Literal["redis", "sqs"] = "redis"

    # Local Model Runtime (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Configured Models
    FAST_MODEL: str = "qwen:4b"
    REASONING_MODEL: str = "qwen2.5:7b"
    VISION_MODEL: str = "moondream:1.8b"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_RETRIES: int = 3

    # Retailer Availability & Verification Configuration
    RETAILER_VERIFICATION_MAX_AGE_HOURS: int = 72

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_mode(cls, value: object) -> object:
        """Accept common deployment labels injected into DEBUG by host environments."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod", "off"}:
                return False
            if normalized in {"development", "dev", "debug", "on"}:
                return True
        return value


settings = Settings()
