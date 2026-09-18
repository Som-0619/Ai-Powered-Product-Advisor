"""Ingestion package providing discovery, crawling, extraction, normalization, and indexing."""

from app.ingestion.source_discovery import SourceDiscoveryService
from app.ingestion.crawler import CrawlerService, CrawlerError
from app.ingestion.extraction import ExtractionService
from app.ingestion.cleaning import CleaningService, PIIRedactor
from app.ingestion.normalization import NormalizationService
from app.ingestion.deduplication import DeduplicationService
from app.ingestion.validation import ValidationService, IngestionValidationError
from app.ingestion.indexing import IndexingService
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.worker import IngestionWorker
from app.ingestion.robots import RobotsManager, DomainRateLimiter, RobotsDisallowedError

__all__ = [
    "SourceDiscoveryService",
    "CrawlerService",
    "CrawlerError",
    "ExtractionService",
    "CleaningService",
    "PIIRedactor",
    "NormalizationService",
    "DeduplicationService",
    "ValidationService",
    "IngestionValidationError",
    "IndexingService",
    "IngestionPipeline",
    "IngestionWorker",
    "RobotsManager",
    "DomainRateLimiter",
    "RobotsDisallowedError",
]
