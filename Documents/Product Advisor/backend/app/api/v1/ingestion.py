"""API endpoints for web ingestion, crawl jobs, and retrieval dry-runs."""

import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.models.sources import CrawlJob
from app.services.factory import (
    get_db_service,
    get_search_service,
    get_storage_service,
    get_queue_service,
)
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.crawler import CrawlerService


router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


class CrawlRequest(BaseModel):
    url: str = Field(..., description="Target web URL to crawl and ingest")
    source_type: Optional[str] = Field(None, description="Optional source classification override")


class DryRunRequest(BaseModel):
    url: str = Field(..., description="Target web URL or identifier")
    html_content: Optional[str] = Field(None, description="Optional raw HTML content to bypass live network")


def _get_pipeline(crawler: Optional[CrawlerService] = None) -> IngestionPipeline:
    return IngestionPipeline(
        db_service=get_db_service(),
        storage_service=get_storage_service(),
        search_service=get_search_service(),
        queue_service=get_queue_service(),
        crawler=crawler,
    )


@router.post("/crawl", status_code=status.HTTP_202_ACCEPTED)
async def submit_crawl_job(request: CrawlRequest):
    """Asynchronously enqueue a web crawl job."""
    pipeline = _get_pipeline()
    try:
        job_id = await pipeline.enqueue_job(url=request.url, source_type=request.source_type)
        return {
            "status": "pending",
            "job_id": job_id,
            "url": request.url,
            "message": "Crawl job enqueued successfully.",
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Retrieve the execution status of a crawl job."""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job UUID format.")

    db = get_db_service()
    async with db.session() as session:
        stmt = select(CrawlJob).where(CrawlJob.id == job_uuid).limit(1)
        res = await session.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail=f"Crawl job {job_id} not found.")

        return {
            "job_id": str(job.id),
            "url": job.url,
            "status": job.status,
            "attempts": job.attempts,
            "raw_storage_path": job.raw_storage_path,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }


@router.post("/dry-run")
async def dry_run_ingestion(request: DryRunRequest):
    """Synchronously execute the full 13-stage ingestion pipeline for dry-run testing."""
    crawler = CrawlerService()
    if request.html_content:
        crawler.register_mock_url(request.url, status_code=200, content=request.html_content)

    pipeline = _get_pipeline(crawler=crawler)
    try:
        result = await pipeline.run(request.url)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
