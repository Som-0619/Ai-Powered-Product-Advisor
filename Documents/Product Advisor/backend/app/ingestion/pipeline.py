"""End-to-end Ingestion Pipeline orchestrating all 13 stages."""

import time
import uuid
from typing import Any, Dict, Optional
from sqlalchemy import select
from app.core.logging import logger
from app.services.database import DatabaseService
from app.services.storage import StorageService
from app.services.search import SearchService
from app.services.queue import QueueService
from app.schemas.ingestion import (
    DeduplicationResult,
    IngestionJobPayload,
    IngestionJobStatus,
    NormalizedEntity,
    RawCrawlPayload,
)
from app.models.sources import CrawlJob, Source
from app.ingestion.source_discovery import SourceDiscoveryService
from app.ingestion.crawler import CrawlerService, CrawlerError
from app.ingestion.extraction import ExtractionService
from app.ingestion.normalization import NormalizationService
from app.ingestion.deduplication import DeduplicationService
from app.ingestion.validation import ValidationService
from app.ingestion.indexing import IndexingService


class IngestionPipeline:
    """Orchestrates the 13-stage ingestion workflow from URL discovery to OpenSearch indexing."""

    def __init__(
        self,
        db_service: DatabaseService,
        storage_service: StorageService,
        search_service: SearchService,
        queue_service: Optional[QueueService] = None,
        source_discovery: Optional[SourceDiscoveryService] = None,
        crawler: Optional[CrawlerService] = None,
        extraction: Optional[ExtractionService] = None,
        normalization: Optional[NormalizationService] = None,
        deduplication: Optional[DeduplicationService] = None,
        validation: Optional[ValidationService] = None,
        indexing: Optional[IndexingService] = None,
    ):
        self.db_service = db_service
        self.storage_service = storage_service
        self.search_service = search_service
        self.queue_service = queue_service

        self.source_discovery = source_discovery or SourceDiscoveryService()
        self.crawler = crawler or CrawlerService()
        self.extraction = extraction or ExtractionService()
        self.normalization = normalization or NormalizationService()
        self.deduplication = deduplication or DeduplicationService(db_service=self.db_service)
        self.validation = validation or ValidationService()
        self.indexing = indexing or IndexingService(
            storage_service=self.storage_service,
            db_service=self.db_service,
            search_service=self.search_service,
        )

    async def run(self, url: str) -> Dict[str, Any]:
        """Execute the synchronous pipeline stages for a given URL."""
        url = url.strip()
        logger.info(f"Starting ingestion pipeline for: {url}")

        # 1. Source Discovery
        source_meta = self.source_discovery.discover_source(url)

        try:
            # 2. Crawl
            raw_payload = await self.crawler.crawl(url)

            # 3. Raw Storage in MinIO
            raw_path = await self.indexing.persist_raw_content(raw_payload)

            # 4. Extraction
            extracted = self.extraction.extract(raw_payload, source_meta)

            # 5, 6, 7. Cleaning, Normalization & PII Redaction
            normalized = self.normalization.normalize(extracted)

            # 8. Deduplication Check
            dedup_result: DeduplicationResult = await self.deduplication.check_duplicate(normalized)
            if dedup_result.status == "duplicate_identical":
                logger.info(f"Duplicate identical content found for {url}. Skipping re-indexing.")
                return {
                    "status": "duplicate_skipped",
                    "url": url,
                    "existing_id": dedup_result.existing_id,
                    "content_hash": normalized.content_hash,
                    "raw_storage_path": raw_path,
                    "message": dedup_result.message,
                }

            # 9. Validation
            self.validation.validate(normalized)

            # 10, 11, 12, 13. PostgreSQL Persistence, Embedding, and OpenSearch Indexing
            index_result = await self.indexing.persist_and_index(normalized, raw_path)

            return {
                "status": "completed",
                "url": url,
                "product_id": index_result["product_id"],
                "document_id": index_result["document_id"],
                "content_hash": normalized.content_hash,
                "raw_storage_path": raw_path,
                "entity_type": normalized.entity_type,
                "title": normalized.title,
                "opensearch": index_result["opensearch"],
            }

        except Exception as exc:
            logger.error(f"Ingestion pipeline failed for {url}: {exc}")
            # Record failed crawl job in database
            await self._record_failure(url, str(exc))
            raise

    async def enqueue_job(
        self,
        url: str,
        source_type: Optional[str] = None,
        queue_name: str = "ingestion_jobs",
    ) -> str:
        """Enqueue an asynchronous crawl/ingestion job into QueueService."""
        if not self.queue_service:
            raise RuntimeError("QueueService is not configured for asynchronous execution.")

        job_id = str(uuid.uuid4())
        payload = IngestionJobPayload(
            job_id=job_id,
            url=url,
            source_type=source_type,
            enqueued_at=time.time(),
        )

        # Enqueue in Redis / SQS
        await self.queue_service.enqueue(queue_name, payload.model_dump())


        # Create pending job record in DB
        async with self.db_service.session() as session:
            job = CrawlJob(
                id=uuid.UUID(job_id),
                url=url,
                status="pending",
                attempts=0,
            )
            session.add(job)
            await session.commit()

        logger.info(f"Enqueued ingestion job {job_id} for URL: {url}")
        return job_id

    async def _record_failure(self, url: str, error_message: str) -> None:
        """Record failed crawl attempt in database."""
        try:
            async with self.db_service.session() as session:
                job = CrawlJob(
                    url=url,
                    status="failed",
                    attempts=1,
                    error_message=error_message[:1000],
                )
                session.add(job)
                await session.commit()
        except Exception as exc:
            logger.warning(f"Could not log failure in crawl_jobs table: {exc}")
