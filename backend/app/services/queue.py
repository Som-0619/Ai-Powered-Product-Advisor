"""Abstract base class for Asynchronous Queue Service."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class QueueService(ABC):
    """Queue service abstraction for Redis Queue / AWS SQS."""

    @abstractmethod
    async def connect(self) -> None:
        """Initialize connection to queue."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to queue."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check queue connectivity."""
        pass

    @abstractmethod
    async def enqueue(self, queue_name: str, payload: Dict[str, Any]) -> str:
        """Enqueue a job payload, returns job_id."""
        pass

    @abstractmethod
    async def dequeue(self, queue_name: str, timeout_seconds: int = 5) -> Optional[Dict[str, Any]]:
        """Dequeue a job payload."""
        pass
