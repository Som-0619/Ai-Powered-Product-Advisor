"""Abstract base class for Database Service."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class DatabaseService(ABC):
    """Database service abstraction for PostgreSQL / Aurora."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection/pool."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection/pool."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verify database connectivity and return status."""
        pass

    @abstractmethod
    def session(self):
        """Async context manager yielding an AsyncSession."""
        pass

