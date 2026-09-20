"""AWS Aurora PostgreSQL adapter stub (Phase 16 preparation)."""

from typing import Any, Dict
from app.services.database import DatabaseService


class AwsAuroraService(DatabaseService):
    """AWS Aurora adapter connecting to Amazon Aurora PostgreSQL."""

    async def connect(self) -> None:
        raise NotImplementedError("AWS Aurora adapter scheduled for Phase 16.")

    async def disconnect(self) -> None:
        raise NotImplementedError("AWS Aurora adapter scheduled for Phase 16.")

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "unconfigured", "details": {"adapter": "aws_aurora"}}

    def session(self):
        raise NotImplementedError("AWS Aurora adapter scheduled for Phase 16.")

