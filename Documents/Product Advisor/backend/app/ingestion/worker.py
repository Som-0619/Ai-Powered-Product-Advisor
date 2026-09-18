"""Asynchronous queue worker for decoupled, non-blocking ingestion jobs."""

import asyncio
import uuid
from typing import Any, Dict, Optional
from sqlalchemy import select
from app.core.logging import logger
from app.services.queue import QueueService
from app.services.database import DatabaseService
from app.models.sources import CrawlJob
from app.ingestion.pipeline import IngestionPipeline


class IngestionWorker:
    """Consumes ingestion jobs from Redis Queue and executes the pipeline asynchronously."""

    def __init__(
        self,
        queue_service: QueueService,
        db_service: DatabaseService,
        pipeline: IngestionPipeline,
        queue_name: str = "ingestion_jobs",
    ):
        self.queue_service = queue_service
        self.db_service = db_service
        self.pipeline = pipeline
        self.queue_name = queue_name
        self._running = False

    async def process_one_job(self, timeout_seconds: int = 2) -> Optional[Dict[str, Any]]:
        """Pull and execute a single job from the queue. Useful for testing and step execution."""
        msg = await self.queue_service.dequeue(self.queue_name, timeout_seconds=timeout_seconds)
        if not msg:
            return None

        # Handle message format from LocalRedisQueueService
        payload = msg.get("payload", msg)
        job_id_str = payload.get("job_id")
        url = payload.get("url")

        if not url:
            logger.warning(f"Received malformed job message without URL: {msg}")
            return None

        logger.info(f"Processing ingestion job {job_id_str} for: {url}")

        # Update job status to processing in DB
        if job_id_str:
            await self._update_job_status(job_id_str, status="processing")

        try:
            result = await self.pipeline.run(url)
            if job_id_str:
                await self._update_job_status(
                    job_id_str,
                    status="completed",
                    raw_storage_path=result.get("raw_storage_path"),
                )
            return result
        except Exception as exc:
            logger.error(f"Worker failed processing job {job_id_str}: {exc}")
            if job_id_str:
                await self._update_job_status(
                    job_id_str,
                    status="failed",
                    error_message=str(exc),
                )
            return {"status": "failed", "job_id": job_id_str, "error": str(exc)}

    async def run_loop(self, poll_interval: float = 1.0) -> None:
        """Continuously consume jobs in an asynchronous event loop."""
        self._running = True
        logger.info(f"Starting IngestionWorker loop on queue: {self.queue_name}")
        while self._running:
            try:
                processed = await self.process_one_job(timeout_seconds=2)
                if not processed:
                    await asyncio.sleep(poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Unexpected error in IngestionWorker loop: {exc}")
                await asyncio.sleep(poll_interval)

    def stop(self) -> None:
        """Signal the worker loop to stop."""
        self._running = False

    async def _update_job_status(
        self,
        job_id_str: str,
        status: str,
        raw_storage_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Update the CrawlJob database record."""
        try:
            job_uuid = uuid.UUID(job_id_str)
            async with self.db_service.session() as session:
                stmt = select(CrawlJob).where(CrawlJob.id == job_uuid).limit(1)
                res = await session.execute(stmt)
                job = res.scalar_one_or_none()
                if job:
                    job.status = status
                    job.attempts += 1
                    if raw_storage_path:
                        job.raw_storage_path = raw_storage_path
                    if error_message:
                        job.error_message = error_message[:1000]
                    await session.commit()
        except Exception as exc:
            logger.warning(f"Could not update CrawlJob {job_id_str} status: {exc}")
