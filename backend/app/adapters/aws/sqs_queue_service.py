"""Amazon SQS Queue adapter stub (Phase 16 preparation)."""

from typing import Any, Dict, Optional
from app.services.queue import QueueService


class AwsSqsQueueService(QueueService):
    """AWS SQS queue adapter."""

    async def connect(self) -> None:
        raise NotImplementedError("AWS SQS adapter scheduled for Phase 16.")

    async def disconnect(self) -> None:
        raise NotImplementedError()

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "unconfigured", "details": {"adapter": "aws_sqs"}}

    async def enqueue(self, queue_name: str, payload: Dict[str, Any]) -> str:
        raise NotImplementedError()

    async def dequeue(self, queue_name: str, timeout_seconds: int = 5) -> Optional[Dict[str, Any]]:
        raise NotImplementedError()
