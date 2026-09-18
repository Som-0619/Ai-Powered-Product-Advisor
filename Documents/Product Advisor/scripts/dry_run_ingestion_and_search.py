"""Comprehensive dry-run script for Phase 5 Web Ingestion and OpenSearch Retrieval.

Demonstrates:
1. Discovery, Crawling, MinIO raw storage
2. Specification extraction, cleaning, PII redaction
3. Engineering unit normalization (3.3V, I2C, 16GB RAM, RTX 4060)
4. PostgreSQL persistence
5. Dense vector embedding and OpenSearch indexing
6. Verification of OpenSearch retrieval across BM25 keyword, semantic vector, and hybrid search
"""

import asyncio
import json
import time
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.services.factory import (
    get_db_service,
    get_storage_service,
    get_search_service,
    get_queue_service,
)
from app.ingestion.crawler import CrawlerService
from app.ingestion.pipeline import IngestionPipeline


SAMPLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Espressif ESP32-S3-WROOM-1 DevKit - 3.3V Wi-Fi & BLE 5.0 Module</title>
    <meta name="description" content="Next-gen ESP32-S3 microcontroller with 3.3V operating voltage, I2C and SPI interfaces, optimized for AI acceleration and 16GB RAM host workstations.">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "ESP32-S3-WROOM-1-N8R8",
        "brand": {
            "@type": "Brand",
            "name": "Espressif Systems"
        },
        "model": "ESP32-S3-WROOM-1",
        "mpn": "ESP32-S3-WROOM-1-N8R8",
        "description": "Powerful dual-core Xtensa 32-bit LX7 microcontroller with 2.4GHz Wi-Fi and Bluetooth 5 (LE).",
        "offers": {
            "@type": "Offer",
            "price": "4.25",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
        }
    }
    </script>
</head>
<body>
    <header>
        <nav><a href="/">Home</a> | <a href="/products">Products</a></nav>
    </header>

    <main>
        <h1>ESP32-S3-WROOM-1 High Performance Wireless Module</h1>
        <p>The ESP32-S3 is a dual-core MCU chip with integrated Wi-Fi and Bluetooth 5 LE.</p>

        <section id="specifications">
            <h2>Technical Specifications</h2>
            <table>
                <tr><th>Specification</th><th>Value</th></tr>
                <tr><td>Operating Voltage</td><td>3.3V</td></tr>
                <tr><td>Operating Current</td><td>500mA</td></tr>
                <tr><td>CPU Frequency</td><td>240MHz</td></tr>
                <tr><td>Supported Memory</td><td>16GB RAM</td></tr>
                <tr><td>Graphics Co-processor</td><td>RTX 4060</td></tr>
                <tr><td>Interfaces</td><td>I2C, SPI, UART, USB-C</td></tr>
                <tr><td>Package</td><td>QFN-32</td></tr>
            </table>
        </section>

        <section id="support">
            <h3>Customer & Commercial Support</h3>
            <p>For custom engineering and sample reel orders, contact lead engineer Alice at alice.smith@espressif.com or phone +1 (800) 555-0188.</p>
            <p>Corporate billing card on file: 4111-2222-3333-4444. Internal token: sk_live_998877665544332211aabbcc.</p>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 Espressif Systems. All rights reserved.</p>
    </footer>
</body>
</html>
"""


async def run_dry_run():
    print("=" * 70)
    print("PRODUCT ADVISOR: PHASE 5 INGESTION & RETRIEVAL DRY RUN")
    print("=" * 70)

    db_service = get_db_service()
    storage_service = get_storage_service()
    search_service = get_search_service()
    queue_service = get_queue_service()

    # Initialize connections
    await db_service.connect()
    await storage_service.connect()
    await search_service.connect()
    await queue_service.connect()

    target_url = f"https://www.espressif.com/en/products/socs/esp32-s3-dryrun-{int(time.time())}"
    print(f"\n[1/5] Registering target URL: {target_url}")

    crawler = CrawlerService()
    crawler.register_mock_url(target_url, status_code=200, content=SAMPLE_HTML)

    pipeline = IngestionPipeline(
        db_service=db_service,
        storage_service=storage_service,
        search_service=search_service,
        queue_service=queue_service,
        crawler=crawler,
    )

    print("\n[2/5] Executing 13-stage ingestion pipeline...")
    start_time = time.perf_counter()
    result = await pipeline.run(target_url)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    print(f"      Status:            {result['status']}")
    print(f"      Product ID:        {result['product_id']}")
    print(f"      Document ID:       {result['document_id']}")
    print(f"      Raw MinIO Path:    {result['raw_storage_path']}")
    print(f"      Content Hash:      {result['content_hash']}")
    print(f"      Total Pipeline:    {elapsed_ms}ms")

    # Verify MinIO
    raw_exists = await storage_service.exists(result["raw_storage_path"])
    print(f"\n[3/5] Verifying raw payload stored in MinIO: {'EXISTS (OK)' if raw_exists else 'FAILED'}")

    # Wait for OpenSearch index refresh
    print("\n[4/5] Refreshing OpenSearch indexes for immediate retrieval...")
    await asyncio.sleep(1.2)

    # Execute search queries
    print("\n[5/5] Executing multi-mode search queries across OpenSearch:")
    test_queries = [
        ("BM25 Keyword", "components", "ESP32", "keyword"),
        ("BM25 Technical Voltage", "components", "3.3V", "keyword"),
        ("BM25 Interface", "components", "I2C", "keyword"),
        ("BM25 GPU Hardware", "products", "RTX 4060", "keyword"),
        ("BM25 RAM Hardware", "products", "16GB RAM", "keyword"),
        ("Semantic Vector Search", "components", "dual core microcontroller with wireless wifi", "semantic"),
        ("Hybrid Retrieval (RRF)", "components", "ESP32 3.3V I2C wireless MCU", "hybrid"),
    ]

    all_passed = True
    for label, index, query, mode in test_queries:
        if mode == "keyword":
            resp = await search_service.keyword_search(index_name=index, query_text=query, limit=3)
        elif mode == "semantic":
            resp = await search_service.semantic_search(index_name=index, query_text=query, limit=3)
        elif mode == "hybrid":
            resp = await search_service.hybrid_search(index_name=index, query_text=query, limit=3)

        hit_titles = [h.source.get("title", "Unknown") for h in resp.hits]
        status_icon = "PASS" if resp.total > 0 else "FAIL"
        if resp.total == 0:
            all_passed = False
        print(f"  [{status_icon}] {label:<26} | Query: '{query}' | Total Hits: {resp.total} | Latency: {resp.latency_ms}ms")
        for i, hit in enumerate(resp.hits[:2], 1):
            title = hit.source.get("title") or hit.source.get("name")
            print(f"        -> #{i} (Score: {hit.score:.4f}): {title}")

    print("\n" + "=" * 70)
    if all_passed and raw_exists:
        print("DRY RUN RESULT: ALL INGESTION & SEARCH RETRIEVAL CHECKS PASSED!")
    else:
        print("DRY RUN RESULT: SOME CHECKS FAILED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_dry_run())
