"""Local Redis Cache adapter implementing CacheService."""

import time
from typing import Any, Dict, Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger
from app.services.cache import CacheService


class LocalRedisCacheService(CacheService):
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        if not self._client:
            self._client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Connected to Redis cache", extra={"host": settings.REDIS_HOST, "port": settings.REDIS_PORT})

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Disconnected from Redis cache")

    async def health_check(self) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            if not self._client:
                await self.connect()
            pong = await self._client.ping()
            latency = round((time.perf_counter() - start) * 1000, 2)
            if pong:
                return {
                    "status": "ok",
                    "latency_ms": latency,
                    "details": {"ping": "PONG", "host": settings.REDIS_HOST},
                }
            return {"status": "degraded", "latency_ms": latency, "error": "Ping failed"}
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "error",
                "latency_ms": latency,
                "error": str(exc),
            }

    async def get(self, key: str) -> Optional[str]:
        if not self._client:
            await self.connect()
        return await self._client.get(key)

    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        if not self._client:
            await self.connect()
        return bool(await self._client.set(key, value, ex=expire_seconds))

    async def delete(self, key: str) -> bool:
        if not self._client:
            await self.connect()
        return bool(await self._client.delete(key))
