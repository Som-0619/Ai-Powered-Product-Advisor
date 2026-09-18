"""Service factory and dependency injection registry."""

from app.core.config import settings
from app.core.logging import logger
from app.services.database import DatabaseService
from app.services.search import SearchService
from app.services.cache import CacheService
from app.services.storage import StorageService
from app.services.queue import QueueService
from app.services.model_gateway import ModelGateway
from app.services.embedding import EmbeddingService

from app.adapters.local.postgres_service import LocalPostgresService
from app.adapters.local.opensearch_service import LocalOpenSearchService
from app.adapters.local.redis_cache_service import LocalRedisCacheService
from app.adapters.local.redis_queue_service import LocalRedisQueueService
from app.adapters.local.minio_storage import MinioStorageService
from app.adapters.local.ollama_model_gateway import LocalOllamaModelGateway
from app.adapters.local.ollama_embedding_service import LocalOllamaEmbeddingService
from app.adapters.local.local_embedding import DeterministicLocalEmbeddingService


class ServiceContainer:
    """Holds singleton service adapter instances initialized according to ENVIRONMENT."""

    def __init__(self):
        self.db: DatabaseService = None
        self.search: SearchService = None
        self.cache: CacheService = None
        self.storage: StorageService = None
        self.queue: QueueService = None
        self.model_gateway: ModelGateway = None
        self.embedding: EmbeddingService = None
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        env = settings.ENVIRONMENT.lower()
        logger.info(f"Initializing service container for environment: {env}")

        if env == "local":
            self.db = LocalPostgresService()
            self.embedding = DeterministicLocalEmbeddingService(dimension=384)
            self.search = LocalOpenSearchService(embedding_service=self.embedding)
            self.cache = LocalRedisCacheService()
            self.queue = LocalRedisQueueService()
            self.storage = MinioStorageService()
            self.model_gateway = LocalOllamaModelGateway()
        elif env == "aws":
            # Reserved for Phase 16 AWS adapters
            from app.adapters.aws.aurora_service import AwsAuroraService
            from app.adapters.aws.opensearch_serverless_service import AwsOpenSearchServerlessService
            from app.adapters.aws.elasticache_service import AwsElastiCacheService
            from app.adapters.aws.s3_storage import AwsS3StorageService
            from app.adapters.aws.sqs_queue_service import AwsSqsQueueService

            self.db = AwsAuroraService()
            self.search = AwsOpenSearchServerlessService()
            self.cache = AwsElastiCacheService()
            self.queue = AwsSqsQueueService()
            self.storage = AwsS3StorageService()
            self.model_gateway = LocalOllamaModelGateway()
            self.embedding = LocalOllamaEmbeddingService()
        else:
            raise ValueError(f"Unsupported ENVIRONMENT '{env}'. Must be 'local' or 'aws'.")
        self._initialized = True


# Global container instance
container = ServiceContainer()


def get_db_service() -> DatabaseService:
    if not container._initialized:
        container.initialize()
    return container.db


def get_search_service() -> SearchService:
    if not container._initialized:
        container.initialize()
    return container.search


def get_cache_service() -> CacheService:
    if not container._initialized:
        container.initialize()
    return container.cache


def get_storage_service() -> StorageService:
    if not container._initialized:
        container.initialize()
    return container.storage


def get_queue_service() -> QueueService:
    if not container._initialized:
        container.initialize()
    return container.queue


def get_model_gateway() -> ModelGateway:
    if not container._initialized:
        container.initialize()
    return container.model_gateway


def get_embedding_service() -> EmbeddingService:
    if not container._initialized:
        container.initialize()
    return container.embedding
