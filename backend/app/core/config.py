"""Configuration settings for Product Advisor."""

from typing import List, Literal, Optional
from pydantic import Field, field_validator, model_validator
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
    OPENSEARCH_URL: Optional[str] = None
    OPENSEARCH_USE_SSL: bool = False
    OPENSEARCH_VERIFY_CERTS: bool = False
    OPENSEARCH_USERNAME: str = "admin"
    OPENSEARCH_PASSWORD: str = "admin"
    OPENSEARCH_INDEX: str = "products_v1"
    OPENSEARCH_ALIAS: str = "products_current"

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
    EMBEDDING_DIMENSION: int = 384
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_RETRIES: int = 3

    # Browserbase (live web retrieval fallback when internal catalog is insufficient)
    BROWSERBASE_API_KEY: str = ""
    WEB_RETRIEVAL_ENABLED: bool = True
    WEB_RETRIEVAL_MIN_CANDIDATES: int = 8
    WEB_RETRIEVAL_TIMEOUT_SECONDS: float = 45.0

    # Search & Retrieval Configuration
    KEYWORD_WEIGHT: float = 0.5
    VECTOR_WEIGHT: float = 0.5
    ENABLE_DB_SEARCH_FALLBACK: bool = False

    # Retailer Availability & Verification Configuration
    RETAILER_VERIFICATION_MAX_AGE_HOURS: int = 720

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

    @model_validator(mode="after")
    def resolve_localhost_when_outside_docker(self) -> "Settings":
        """If running locally outside Docker container, resolve internal Docker hostnames to localhost."""
        import os
        is_in_docker = os.path.exists("/.dockerenv") or os.environ.get("RUNNING_IN_DOCKER") == "true"
        if not is_in_docker and self.ENVIRONMENT == "local":
            if self.POSTGRES_HOST == "postgres":
                self.POSTGRES_HOST = "localhost"
            if self.DATABASE_URL and "@postgres:" in self.DATABASE_URL:
                self.DATABASE_URL = self.DATABASE_URL.replace("@postgres:", "@localhost:")
            if self.OPENSEARCH_HOST == "opensearch":
                self.OPENSEARCH_HOST = "localhost"
            if self.REDIS_HOST == "redis":
                self.REDIS_HOST = "localhost"
            if "minio:9000" in self.STORAGE_ENDPOINT:
                self.STORAGE_ENDPOINT = self.STORAGE_ENDPOINT.replace("minio:9000", "localhost:9000")
            if "ollama:11434" in self.OLLAMA_BASE_URL:
                self.OLLAMA_BASE_URL = self.OLLAMA_BASE_URL.replace("ollama:11434", "localhost:11434")
        return self


settings = Settings()

