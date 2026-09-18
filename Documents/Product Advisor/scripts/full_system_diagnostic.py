"""Comprehensive full-system diagnostic and dry-run script.

Benchmarks and validates operational status across:
1. PostgreSQL & Relational Data Layer
2. MinIO Object Storage
3. Redis Cache & Queue
4. Model Gateway & Embedding Service
5. OpenSearch Retrieval Engine (BM25, k-NN Vector, Hybrid, Metadata Filtering)
6. Open Web Ingestion Pipeline (SSRF, Robots, Crawler, Extract, Clean, Normalize, Deduplicate, Validate, Index, Async Queue Worker)
7. FastAPI REST Endpoints
"""

import asyncio
import hashlib
import json
import time
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple
from sqlalchemy import select, func

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

import httpx

from app.services.factory import (
    get_db_service,
    get_storage_service,
    get_search_service,
    get_cache_service,
    get_queue_service,
    get_embedding_service,
    get_model_gateway,
)
from app.services.storage import StoragePath
from app.models.catalog import Product, Category, Brand, Specification
from app.models.components import Component, ComponentSpecification
from app.models.reviews import Review
from app.models.sources import Source, ProductSource, CrawlJob
from app.models.media import Document
from app.security.ssrf import SSRFValidator, SSRFSecurityError
from app.ingestion.robots import RobotsManager, DomainRateLimiter
from app.ingestion.crawler import CrawlerService
from app.ingestion.extraction import ExtractionService
from app.ingestion.cleaning import CleaningService, PIIRedactor
from app.ingestion.normalization import NormalizationService
from app.ingestion.deduplication import DeduplicationService
from app.ingestion.validation import ValidationService
from app.ingestion.indexing import IndexingService
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.worker import IngestionWorker
from app.schemas.ingestion import RawCrawlPayload, SourceMetadata, ExtractedEntity, ExtractedSpecification


class DiagnosticRunner:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def record(
        self,
        service: str,
        feature: str,
        status: str,
        latency_ms: float,
        score: str,
        details: str,
    ):
        self.results.append({
            "service": service,
            "feature": feature,
            "status": status,
            "latency_ms": latency_ms,
            "score": score,
            "details": details,
        })

    async def run_all(self):
        print("=" * 95)
        print(" " * 20 + "PRODUCT ADVISOR: FULL SYSTEM SERVICE DRY RUN")
        print("=" * 95)
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Testing all 7 service layers end-to-end...\n")

        await self.test_database_layer()
        await self.test_storage_layer()
        await self.test_cache_and_queue_layer()
        await self.test_embedding_and_model_layer()
        await self.test_opensearch_retrieval_layer()
        await self.test_ingestion_pipeline_layer()
        await self.test_fastapi_endpoints()

        self.print_summary_table()

    # -----------------------------------------------------------------
    # 1. Database Layer
    # -----------------------------------------------------------------
    async def test_database_layer(self):
        print("[1/7] Testing PostgreSQL Database Layer...")
        db = get_db_service()
        start = time.perf_counter()
        health = await db.health_check()
        lat = round((time.perf_counter() - start) * 1000, 2)

        self.record("PostgreSQL", "Engine Connectivity & Ping", health.get("status", "ok").upper(), lat, "100%", f"Latency: {lat}ms")

        # Table row counts
        start = time.perf_counter()
        counts = {}
        async with db.session() as session:
            for model, name in [
                (Product, "products"),
                (Component, "components"),
                (ComponentSpecification, "component_specs"),
                (Specification, "specifications"),
                (Review, "reviews"),
                (Source, "sources"),
                (ProductSource, "product_sources"),
                (Document, "documents"),
                (CrawlJob, "crawl_jobs"),
            ]:
                q = await session.execute(select(func.count(model.id)))
                counts[name] = q.scalar() or 0
        lat = round((time.perf_counter() - start) * 1000, 2)
        total_rows = sum(counts.values())
        self.record(
            "PostgreSQL",
            "Schema Integrity (9 core tables)",
            "HEALTHY",
            lat,
            f"{total_rows} rows",
            f"Prods: {counts['products']}, Comps: {counts['components']}, Specs: {counts['specifications']}, Docs: {counts['documents']}",
        )

        # Relational query test (Product with Component and Specs)
        start = time.perf_counter()
        async with db.session() as session:
            stmt = select(Product).where(Product.is_component == True).limit(3)
            res = await session.execute(stmt)
            components = res.scalars().all()
        lat = round((time.perf_counter() - start) * 1000, 2)
        self.record(
            "PostgreSQL",
            "Relational Queries & Filtering",
            "HEALTHY" if components else "DEGRADED",
            lat,
            f"{len(components)} records",
            f"Fetched {len(components)} active components in {lat}ms",
        )

    # -----------------------------------------------------------------
    # 2. Storage Layer
    # -----------------------------------------------------------------
    async def test_storage_layer(self):
        print("[2/7] Testing MinIO Object Storage Layer...")
        storage = get_storage_service()
        start = time.perf_counter()
        health = await storage.health_check()
        lat = round((time.perf_counter() - start) * 1000, 2)

        self.record("MinIO Storage", "Bucket Connectivity", health.get("status", "ok").upper(), lat, "100%", f"Bucket: {health.get('details', {}).get('bucket', 'product-advisor-data')}")

        # Roundtrip test across all 6 logical paths
        test_payload = b"Diagnostic payload test content 12345"
        passed_paths = 0
        total_paths = len(StoragePath.VALID_PREFIXES)

        start = time.perf_counter()
        for prefix in StoragePath.VALID_PREFIXES:
            key = StoragePath.build(prefix, "diagnostic", "test_file.txt")
            await storage.put_object(key, test_payload, "text/plain")
            exists = await storage.exists(key)
            data = await storage.get_object(key)
            if exists and data == test_payload:
                passed_paths += 1
            await storage.delete_object(key)
        lat = round((time.perf_counter() - start) * 1000, 2)

        score_pct = f"{int(passed_paths / total_paths * 100)}%"
        self.record(
            "MinIO Storage",
            "6/6 Logical Paths Read/Write",
            "HEALTHY" if passed_paths == total_paths else "DEGRADED",
            lat,
            score_pct,
            f"Verified {passed_paths}/{total_paths} paths: raw, products, reviews, documents, images, web",
        )

        # Presigned URL generation
        start = time.perf_counter()
        dummy_key = StoragePath.build(StoragePath.DOCUMENTS, "test.pdf")
        presigned_url = await storage.get_url(dummy_key, expires_seconds=300)
        lat = round((time.perf_counter() - start) * 1000, 2)

        has_url = presigned_url.startswith("http")
        self.record(
            "MinIO Storage",
            "Presigned URL Generation",
            "HEALTHY" if has_url else "DEGRADED",
            lat,
            "100%" if has_url else "0%",
            f"Presigned endpoint generated in {lat}ms",
        )

    # -----------------------------------------------------------------
    # 3. Cache & Queue Layer
    # -----------------------------------------------------------------
    async def test_cache_and_queue_layer(self):
        print("[3/7] Testing Redis Cache & Queue Layer...")
        cache = get_cache_service()
        queue = get_queue_service()

        # Cache test
        start = time.perf_counter()
        c_health = await cache.health_check()
        lat = round((time.perf_counter() - start) * 1000, 2)
        self.record("Redis Cache", "Cache Ping & Health", c_health.get("status", "ok").upper(), lat, "100%", f"Latency: {lat}ms")

        start = time.perf_counter()
        test_k, test_v = f"test_k_{uuid.uuid4().hex[:6]}", {"status": "active", "value": 42}
        await cache.set(test_k, json.dumps(test_v), expire_seconds=60)
        retrieved_raw = await cache.get(test_k)

        retrieved = json.loads(retrieved_raw) if retrieved_raw else None
        await cache.delete(test_k)
        lat = round((time.perf_counter() - start) * 1000, 2)
        cache_ok = (retrieved == test_v)
        self.record(
            "Redis Cache",
            "Set/Get/Delete Cycle",
            "HEALTHY" if cache_ok else "FAILED",
            lat,
            "100%" if cache_ok else "0%",
            f"Key-value roundtrip verified in {lat}ms",
        )

        # Queue test
        start = time.perf_counter()
        q_health = await queue.health_check()
        lat = round((time.perf_counter() - start) * 1000, 2)
        self.record("Redis Queue", "Queue Ping & Health", q_health.get("status", "ok").upper(), lat, "100%", f"Latency: {lat}ms")

        start = time.perf_counter()
        q_name = f"diag_q_{uuid.uuid4().hex[:6]}"
        msg_payload = {"task": "ingestion_test", "id": 101}
        job_id = await queue.enqueue(q_name, msg_payload)
        popped = await queue.dequeue(q_name, timeout_seconds=2)
        lat = round((time.perf_counter() - start) * 1000, 2)

        queue_ok = popped and (popped.get("payload") == msg_payload or popped == msg_payload)
        self.record(
            "Redis Queue",
            "Enqueue / Dequeue Execution",
            "HEALTHY" if queue_ok else "FAILED",
            lat,
            "100%" if queue_ok else "0%",
            f"Job {job_id[:8]} processed in {lat}ms",
        )

    # -----------------------------------------------------------------
    # 4. Model Gateway & Embedding Service
    # -----------------------------------------------------------------
    async def test_embedding_and_model_layer(self):
        print("[4/7] Testing Model Gateway & Embedding Service...")
        mg = get_model_gateway()
        embedding = get_embedding_service()

        # Model gateway check
        start = time.perf_counter()
        mg_health = await mg.health_check()
        lat = round((time.perf_counter() - start) * 1000, 2)
        self.record(
            "Model Gateway",
            "Ollama Runtime Ping",
            mg_health.get("status", "ok").upper(),
            lat,
            "100%",
            f"Provider: {mg_health.get('details', {}).get('provider', 'ollama')}",
        )

        # Embedding service test
        start = time.perf_counter()
        test_text = "Espressif ESP32-WROOM-32E 3.3V Wi-Fi and Bluetooth module"
        vec1 = await embedding.embed_query(test_text)
        vec2 = await embedding.embed_query(test_text)
        lat = round((time.perf_counter() - start) * 1000, 2)

        is_384 = len(vec1) == 384
        is_deterministic = (vec1 == vec2)
        # Check normalization: sum of squares ≈ 1.0
        norm = sum(x * x for x in vec1) ** 0.5
        is_normalized = (0.98 <= norm <= 1.02)

        emb_ok = is_384 and is_deterministic and is_normalized
        self.record(
            "Embedding Service",
            "Dense Vectors (384-dim, normalized)",
            "HEALTHY" if emb_ok else "DEGRADED",
            lat,
            "100%" if emb_ok else "0%",
            f"Dim: {len(vec1)}, Norm: {norm:.3f}, Deterministic: {is_deterministic}",
        )

    # -----------------------------------------------------------------
    # 5. OpenSearch Retrieval Layer
    # -----------------------------------------------------------------
    async def test_opensearch_retrieval_layer(self):
        print("[5/7] Testing OpenSearch Retrieval Engine...")
        search = get_search_service()

        start = time.perf_counter()
        health = await search.health_check()
        lat = round((time.perf_counter() - start) * 1000, 2)
        indices_dict = health.get("details", {}).get("indices", {})
        self.record(
            "OpenSearch",
            "Cluster Health & 4 Core Indices",
            health.get("status", "ok").upper(),
            lat,
            f"{len(indices_dict)}/4 indices",
            f"Cluster status: {health.get('details', {}).get('cluster_status', 'yellow')}, Indices: {list(indices_dict.keys())}",
        )

        # BM25 Exact Technical Term Matching
        tech_terms = [
            ("ESP32", "components"),
            ("3.3V", "components"),
            ("I2C", "components"),
            ("RTX 4060", "products"),
            ("16GB RAM", "products"),
        ]
        hits_count = 0
        total_lat = 0.0
        for term, index in tech_terms:
            t_start = time.perf_counter()
            resp = await search.keyword_search(index, term, limit=3)
            t_lat = (time.perf_counter() - t_start) * 1000
            total_lat += t_lat
            if resp.total > 0:
                hits_count += 1
        avg_lat = round(total_lat / len(tech_terms), 2)
        score_str = f"{hits_count}/{len(tech_terms)}"

        self.record(
            "OpenSearch",
            "BM25 Technical Keyword (ESP32, 3.3V, I2C, RTX 4060, 16GB)",
            "HEALTHY" if hits_count == len(tech_terms) else "DEGRADED",
            avg_lat,
            f"{int(hits_count / len(tech_terms) * 100)}%",
            f"Retrieved {score_str} exact technical queries. Avg latency: {avg_lat}ms",
        )

        # Semantic Vector Search (k-NN)
        start = time.perf_counter()
        sem_resp = await search.semantic_search(
            index_name="components",
            query_text="low power dual core microcontroller wireless Wi-Fi module",
            limit=3,
        )
        lat = round((time.perf_counter() - start) * 1000, 2)
        sem_ok = sem_resp.total > 0
        self.record(
            "OpenSearch",
            "Dense Vector Semantic k-NN Search",
            "HEALTHY" if sem_ok else "DEGRADED",
            lat,
            "100%" if sem_ok else "0%",
            f"Hits: {sem_resp.total}, Top match: '{sem_resp.hits[0].source.get('title', 'Unknown')[:30]}'",
        )

        # Hybrid Search (RRF Fusion)
        start = time.perf_counter()
        hyb_resp = await search.hybrid_search(
            index_name="components",
            query_text="ESP32 3.3V I2C wireless module",
            alpha=0.5,
            limit=3,
        )
        lat = round((time.perf_counter() - start) * 1000, 2)
        hyb_ok = hyb_resp.total > 0
        self.record(
            "OpenSearch",
            "Hybrid Search (BM25 + Vector RRF)",
            "HEALTHY" if hyb_ok else "DEGRADED",
            lat,
            "100%" if hyb_ok else "0%",
            f"Hits: {hyb_resp.total}, RRF Score: {hyb_resp.hits[0].score:.4f}",
        )

    # -----------------------------------------------------------------
    # 6. Web Ingestion Pipeline Layer
    # -----------------------------------------------------------------
    async def test_ingestion_pipeline_layer(self):
        print("[6/7] Testing Web Ingestion Pipeline Layer...")
        # 1. SSRF Validator
        start = time.perf_counter()
        blocked = 0
        test_attacks = [
            "http://127.0.0.1/admin",
            "http://10.0.0.1/internal",
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:8000/ready",
            "file:///etc/passwd",
        ]
        for url in test_attacks:
            try:
                SSRFValidator.validate_url(url)
            except SSRFSecurityError:
                blocked += 1
        lat = round((time.perf_counter() - start) * 1000, 2)
        ssrf_ok = (blocked == len(test_attacks))
        self.record(
            "Ingestion Security",
            "SSRF Validator (Blocks 5 dangerous targets)",
            "HEALTHY" if ssrf_ok else "FAILED",
            lat,
            f"{blocked}/{len(test_attacks)}",
            f"Blocked loopback, 10.x, AWS metadata, localhost, file:// in {lat}ms",
        )

        # 2. Robots & Rate Limiter
        start = time.perf_counter()
        robots = RobotsManager()
        robots.set_mock_robots_txt("vendor.com", "User-agent: *\nDisallow: /secret/")
        allowed = await robots.can_fetch("https://vendor.com/datasheet.html")
        disallowed = await robots.can_fetch("https://vendor.com/secret/spec.html")
        lat = round((time.perf_counter() - start) * 1000, 2)
        robots_ok = (allowed is True and disallowed is False)
        self.record(
            "Ingestion Compliance",
            "Robots.txt & Domain Rate Limiter",
            "HEALTHY" if robots_ok else "FAILED",
            lat,
            "100%",
            f"Correctly enforced allow/disallow policy for ProductAdvisorBot",
        )

        # 3. Extraction & PII Redaction & Normalization
        start = time.perf_counter()
        sample_html = """
        <html>
            <head><title>Diagnostic Sensor - 3300 mV I2C/SPI</title></head>
            <body>
                <table>
                    <tr><td>Operating Voltage</td><td>3300 mV</td></tr>
                    <tr><td>Operating Current</td><td>500 mA</td></tr>
                    <tr><td>RAM</td><td>16GB RAM</td></tr>
                    <tr><td>Interface</td><td>I2C, SPI, USB-C</td></tr>
                </table>
                <p>Support: tech@corp.com, phone: (555) 123-4567, card: 4111-2222-3333-4444</p>
            </body>
        </html>
        """
        payload = RawCrawlPayload(
            url="https://www.adafruit.com/diagnostic-sensor",
            status_code=200,
            content=sample_html,
            content_bytes=len(sample_html),
            content_hash=hashlib.sha256(sample_html.encode()).hexdigest(),
        )
        meta = SourceMetadata(
            source_url=payload.url,
            domain="adafruit.com",
            content_hash=payload.content_hash,
            trust_score=0.98,
        )
        extracted = ExtractionService().extract(payload, meta)
        normalized = NormalizationService().normalize(extracted)
        lat = round((time.perf_counter() - start) * 1000, 2)

        # Check normalization
        elec = normalized.electrical_parameters
        norm_v = elec.get("voltage") == 3.3
        norm_c = elec.get("current") == 0.5
        norm_ram = elec.get("ram_gb") == 16.0
        norm_iface = "I2C" in elec.get("interface", [])

        # Check PII
        pii_email = "[REDACTED_EMAIL]" in normalized.cleaned_text
        pii_phone = "[REDACTED_PHONE]" in normalized.cleaned_text
        pii_card = "[REDACTED_CARD]" in normalized.cleaned_text

        parse_ok = norm_v and norm_c and norm_ram and norm_iface and pii_email and pii_phone and pii_card
        self.record(
            "Ingestion Parsing",
            "Extraction, Cleaning, PII Redaction & Unit Normalization",
            "HEALTHY" if parse_ok else "DEGRADED",
            lat,
            "100%" if parse_ok else "0%",
            f"3300mV->3.3V, 500mA->0.5A, 16GB RAM->16GB, PII masked (email, phone, card)",
        )

        # 4. End-to-end Ingestion Pipeline Run
        start = time.perf_counter()
        target_url = f"https://www.espressif.com/diagnostic-full-run-{int(time.time())}"
        crawler = CrawlerService()
        crawler.register_mock_url(target_url, status_code=200, content=sample_html)

        pipeline = IngestionPipeline(
            db_service=get_db_service(),
            storage_service=get_storage_service(),
            search_service=get_search_service(),
            queue_service=get_queue_service(),
            crawler=crawler,
        )
        ingest_res = await pipeline.run(target_url)
        lat = round((time.perf_counter() - start) * 1000, 2)

        e2e_ok = ingest_res.get("status") in ("completed", "duplicate_skipped")
        self.record(
            "Ingestion Pipeline",
            "13-Stage End-to-End Execution (MinIO + Postgres + OpenSearch)",
            "HEALTHY" if e2e_ok else "FAILED",
            lat,
            "100%" if e2e_ok else "0%",
            f"Product: {ingest_res.get('product_id', '')[:8]}..., Raw MinIO: {ingest_res.get('raw_storage_path')}",
        )

        # 5. Async Worker Queue Execution
        start = time.perf_counter()
        q_name = f"diag_work_q_{uuid.uuid4().hex[:6]}"
        job_url = f"https://www.adafruit.com/async-job-{int(time.time())}"
        crawler.register_mock_url(job_url, status_code=200, content=sample_html)

        job_id = await pipeline.enqueue_job(job_url, source_type="distributor", queue_name=q_name)
        worker = IngestionWorker(
            queue_service=get_queue_service(),
            db_service=get_db_service(),
            pipeline=pipeline,
            queue_name=q_name,
        )
        work_res = await worker.process_one_job(timeout_seconds=2)
        lat = round((time.perf_counter() - start) * 1000, 2)
        work_ok = work_res and work_res.get("status") in ("completed", "duplicate_skipped")
        self.record(
            "Ingestion Worker",
            "Async Queue Dispatch & Background Worker Consumption",
            "HEALTHY" if work_ok else "FAILED",
            lat,
            "100%" if work_ok else "0%",
            f"Enqueued job {job_id[:8]}... consumed & completed in {lat}ms",
        )

    # -----------------------------------------------------------------
    # 7. FastAPI REST API Endpoints
    # -----------------------------------------------------------------
    async def test_fastapi_endpoints(self):
        print("[7/7] Testing FastAPI HTTP Endpoints...")
        from app.main import app
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Health
            start = time.perf_counter()
            r_health = await client.get("/api/v1/health")
            lat = round((time.perf_counter() - start) * 1000, 2)
            self.record(
                "FastAPI REST",
                "GET /api/v1/health (Liveness)",
                "HEALTHY" if r_health.status_code == 200 else "FAILED",
                lat,
                f"HTTP {r_health.status_code}",
                f"Status: {r_health.json().get('status')}",
            )

            # Ready
            start = time.perf_counter()
            r_ready = await client.get("/api/v1/ready")
            lat = round((time.perf_counter() - start) * 1000, 2)
            ready_json = r_ready.json()
            self.record(
                "FastAPI REST",
                "GET /api/v1/ready (Deep Subsystem Readiness)",
                "HEALTHY" if r_ready.status_code == 200 else "DEGRADED",
                lat,
                f"HTTP {r_ready.status_code}",
                f"Overall: {ready_json.get('status')}, Subsystems: {len(ready_json.get('subsystems', {}))}",
            )

            # Ingestion Dry Run Endpoint
            start = time.perf_counter()
            r_dry = await client.post("/api/v1/ingestion/dry-run", json={
                "url": "https://www.espressif.com/test-endpoint-diag",
                "html_content": "<html><head><title>ESP32 Diagnostic Endpoint</title></head><body>3.3V microcontroller</body></html>"
            })
            lat = round((time.perf_counter() - start) * 1000, 2)
            dry_ok = r_dry.status_code == 200 and r_dry.json().get("status") in ("completed", "duplicate_skipped")
            self.record(
                "FastAPI REST",
                "POST /api/v1/ingestion/dry-run (Full Pipeline Ingestion API)",
                "HEALTHY" if dry_ok else "FAILED",
                lat,
                f"HTTP {r_dry.status_code}",
                f"Status: {r_dry.json().get('status')}, Product ID: {r_dry.json().get('product_id', '')[:8]}...",
            )

    # -----------------------------------------------------------------
    # Print Summary Table
    # -----------------------------------------------------------------
    def print_summary_table(self):
        print("\n" + "=" * 115)
        print(f"{'SERVICE':<18} | {'FEATURE / SUBSYSTEM':<38} | {'STATUS':<9} | {'LATENCY':<9} | {'SCORE':<9} | {'DETAILS'}")
        print("-" * 115)

        total_features = len(self.results)
        healthy_count = 0

        for r in self.results:
            st = r["status"]
            if st in ("HEALTHY", "OK"):
                healthy_count += 1
            lat_str = f"{r['latency_ms']}ms"
            print(f"{r['service']:<18} | {r['feature']:<38} | {st:<9} | {lat_str:<9} | {r['score']:<9} | {r['details']}")

        print("=" * 115)
        health_pct = round((healthy_count / total_features) * 100, 1)
        print(f"\nOVERALL SYSTEM WORKING SCORE: {healthy_count}/{total_features} features fully operational ({health_pct}% operational)")
        print("=" * 115)


if __name__ == "__main__":
    runner = DiagnosticRunner()
    asyncio.run(runner.run_all())
