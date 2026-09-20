"""Amazon OpenSearch Serverless adapter stub (Phase 16 preparation)."""

from typing import Any, Dict
from app.services.search import SearchService


class AwsOpenSearchServerlessService(SearchService):
    """AWS OpenSearch Serverless adapter using SigV4 authentication."""

    async def connect(self) -> None:
        raise NotImplementedError("AWS OpenSearch Serverless adapter scheduled for Phase 16.")

    async def disconnect(self) -> None:
        raise NotImplementedError("AWS OpenSearch Serverless adapter scheduled for Phase 16.")

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "unconfigured", "details": {"adapter": "aws_opensearch_serverless"}}

    async def create_index(self, index_name: str, mapping: Dict[str, Any]) -> bool:
        raise NotImplementedError()

    async def search(self, index_name: str, query: Dict[str, Any], size: int = 10) -> Dict[str, Any]:
        raise NotImplementedError()
