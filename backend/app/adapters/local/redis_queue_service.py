"""Local Redis Queue adapter implementing QueueService."""

import json
import time
import uuid
from typing import Any, Dict, Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger
from app.services.queue import QueueService


class LocalRedisQueueService(QueueService):
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None
        self._loop = None

    async def connect(self) -> None:
        import asyncio
        current_loop = asyncio.get_running_loop()
        if self._client and self._loop != current_loop:
            self._client = None

        if not self._client:
            self._loop = current_loop
            self._client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Connected to Redis queue")


    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Disconnected from Redis queue")

    async def health_check(self) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            if not self._client:
                await self.connect()
            pong = await self._client.ping()
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "ok" if pong else "degraded",
                "latency_ms": latency,
                "details": {"provider": "redis_queue"},
            }
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "error",
                "latency_ms": latency,
                "error": str(exc),
            }

    async def enqueue(self, queue_name: str, payload: Dict[str, Any]) -> str:
        if not self._client:
            await self.connect()
        job_id = str(uuid.uuid4())
        message = json.dumps({"job_id": job_id, "payload": payload, "enqueued_at": time.time()})
        await self._client.rpush(f"queue:{queue_name}", message)
        return job_id

    async def dequeue(self, queue_name: str, timeout_seconds: int = 5) -> Optional[Dict[str, Any]]:
        if not self._client:
            await self.connect()
        result = await self._client.blpop(f"queue:{queue_name}", timeout=timeout_seconds)
        if result:
            _, message_json = result
            return json.loads(message_json)
        return None
