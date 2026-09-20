"""Deduplication service utilizing content hashes and canonical URL matching."""

import time
from typing import Optional
from sqlalchemy import select
from app.services.database import DatabaseService
from app.models.sources import ProductSource, CrawlJob
from app.schemas.ingestion import DeduplicationResult, NormalizedEntity
from app.core.logging import logger


class DeduplicationService:
    """Detects duplicates using SHA-256 content hashes and source URLs."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    async def check_duplicate(self, entity: NormalizedEntity) -> DeduplicationResult:
        """Check if an entity already exists in database with identical or modified content."""
        source_url = entity.source_metadata.source_url
        new_hash = entity.content_hash

        async with self.db_service.session() as session:
            # Query existing ProductSource by source_url
            stmt = select(ProductSource).where(ProductSource.source_url == source_url).limit(1)
            result = await session.execute(stmt)
            existing_ps = result.scalar_one_or_none()

            if existing_ps:
                crawl_meta = existing_ps.crawl_metadata or {}
                existing_hash = crawl_meta.get("content_hash")
                product_id_str = str(existing_ps.product_id)

                if existing_hash == new_hash:
                    # Content is identical: Update last_seen timestamp
                    crawl_meta["last_seen"] = time.time()
                    existing_ps.crawl_metadata = crawl_meta
                    await session.commit()

                    logger.info(
                        f"Deduplication: Identical content detected for {source_url} (hash {new_hash[:8]}). Updated last_seen."
                    )
                    return DeduplicationResult(
                        status="duplicate_identical",
                        content_hash=new_hash,
                        existing_id=product_id_str,
                        message="Identical content hash; updated last_seen without re-indexing.",
                    )
                else:
                    # Content has been updated
                    logger.info(
                        f"Deduplication: Updated content detected for {source_url} (old hash {str(existing_hash)[:8]} -> new {new_hash[:8]})."
                    )
                    return DeduplicationResult(
                        status="duplicate_updated",
                        content_hash=new_hash,
                        existing_id=product_id_str,
                        message="Content updated; requires re-indexing.",
                    )

            # Not found: completely new entity
            return DeduplicationResult(
                status="new",
                content_hash=new_hash,
                existing_id=None,
                message="New entity eligible for ingestion.",
            )
