"""Abstract base class for Cache Service."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class CacheService(ABC):
    """Cache service abstraction for Redis / ElastiCache."""

    @abstractmethod
    async def connect(self) -> None:
        """Initialize cache connection pool."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close cache connection pool."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check cache connectivity."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Retrieve value by key."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Set key-value pair with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove key from cache."""
        pass
