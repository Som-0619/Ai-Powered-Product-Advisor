"""Amazon ElastiCache Redis adapter stub (Phase 16 preparation)."""

from typing import Any, Dict, Optional
from app.services.cache import CacheService


class AwsElastiCacheService(CacheService):
    """AWS ElastiCache Redis adapter."""

    async def connect(self) -> None:
        raise NotImplementedError("AWS ElastiCache adapter scheduled for Phase 16.")

    async def disconnect(self) -> None:
        raise NotImplementedError()

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "unconfigured", "details": {"adapter": "aws_elasticache"}}

    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError()

    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        raise NotImplementedError()

    async def delete(self, key: str) -> bool:
        raise NotImplementedError()
