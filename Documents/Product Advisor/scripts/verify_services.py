#!/usr/bin/env python3
"""
Product Advisor - Phase 1 Services Verification Script
Validates connectivity across all 7 core infrastructure components:
1. PostgreSQL
2. OpenSearch
3. Redis
4. MinIO
5. Ollama
6. FastAPI Backend
7. Next.js Frontend
"""

import os
import sys
import time
import socket
import urllib.request
import json
import urllib.error


GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def check_port(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def http_get(url: str, timeout: float = 4.0):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ProductAdvisor-Verifier"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)


def print_row(name: str, target: str, status: str, latency: str, details: str):
    color = GREEN if status == "OK" else (YELLOW if status == "WARN" else RED)
    print(f"{BOLD}{name:<18}{RESET} | {target:<24} | {color}{BOLD}{status:<6}{RESET} | {latency:<10} | {details}")


def main():
    print("\n" + "=" * 90)
    print(f"{BOLD}{BLUE}PRODUCT ADVISOR - PHASE 1 INFRASTRUCTURE VERIFICATION{RESET}")
    print("=" * 90)
    print(f"{'Service':<18} | {'Target':<24} | {'Status':<6} | {'Latency':<10} | {'Details'}")
    print("-" * 90)

    results = {}

    # 1. PostgreSQL
    start = time.perf_counter()
    pg_host = os.environ.get("POSTGRES_HOST", "localhost")
    pg_port = int(os.environ.get("POSTGRES_PORT", 5432))
    pg_ok = check_port(pg_host, pg_port)
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    if pg_ok:
        print_row("1. PostgreSQL", f"{pg_host}:{pg_port}", "OK", f"{elapsed}ms", "Port open, accepting connections")
        results["postgres"] = True
    else:
        print_row("1. PostgreSQL", f"{pg_host}:{pg_port}", "FAIL", f"{elapsed}ms", "Connection refused")
        results["postgres"] = False

    # 2. OpenSearch
    start = time.perf_counter()
    os_host = os.environ.get("OPENSEARCH_HOST", "localhost")
    os_port = int(os.environ.get("OPENSEARCH_PORT", 9200))
    status_code, body = http_get(f"http://{os_host}:{os_port}/_cluster/health")
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    if status_code == 200:
        try:
            data = json.loads(body)
            cluster_status = data.get("status", "unknown")
            cluster_name = data.get("cluster_name", "unknown")
            print_row("2. OpenSearch", f"{os_host}:{os_port}", "OK", f"{elapsed}ms", f"Cluster '{cluster_name}' ({cluster_status})")
            results["opensearch"] = True
        except Exception:
            print_row("2. OpenSearch", f"{os_host}:{os_port}", "OK", f"{elapsed}ms", "HTTP 200 OK")
            results["opensearch"] = True
    else:
        print_row("2. OpenSearch", f"{os_host}:{os_port}", "FAIL", f"{elapsed}ms", f"HTTP {status_code} ({body[:30]})")
        results["opensearch"] = False

    # 3. Redis
    start = time.perf_counter()
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = int(os.environ.get("REDIS_PORT", 6379))
    redis_ok = check_port(redis_host, redis_port)
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    if redis_ok:
        print_row("3. Redis", f"{redis_host}:{redis_port}", "OK", f"{elapsed}ms", "Port open, cache & queue ready")
        results["redis"] = True
    else:
        print_row("3. Redis", f"{redis_host}:{redis_port}", "FAIL", f"{elapsed}ms", "Connection refused")
        results["redis"] = False

    # 4. MinIO
    start = time.perf_counter()
    minio_host = "localhost"
    minio_port = 9000
    status_code, body = http_get(f"http://{minio_host}:{minio_port}/minio/health/live")
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    if status_code == 200:
        print_row("4. MinIO S3", f"{minio_host}:{minio_port}", "OK", f"{elapsed}ms", "Live probe passed")
        results["minio"] = True
    else:
        # Check port
        if check_port(minio_host, minio_port):
            print_row("4. MinIO S3", f"{minio_host}:{minio_port}", "OK", f"{elapsed}ms", "Port open")
            results["minio"] = True
        else:
            print_row("4. MinIO S3", f"{minio_host}:{minio_port}", "FAIL", f"{elapsed}ms", "Port unreachable")
            results["minio"] = False

    # 5. Ollama
    start = time.perf_counter()
    ollama_host = "localhost"
    ollama_port = 11434
    status_code, body = http_get(f"http://{ollama_host}:{ollama_port}/api/tags")
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    if status_code == 200:
        try:
            data = json.loads(body)
            models = [m.get("name") for m in data.get("models", [])]
            details = f"{len(models)} models available" if models else "Runtime online (no models pulled yet)"
            print_row("5. Ollama Runtime", f"{ollama_host}:{ollama_port}", "OK", f"{elapsed}ms", details)
            results["ollama"] = True
        except Exception:
            print_row("5. Ollama Runtime", f"{ollama_host}:{ollama_port}", "OK", f"{elapsed}ms", "Online")
            results["ollama"] = True
    else:
        print_row("5. Ollama Runtime", f"{ollama_host}:{ollama_port}", "FAIL", f"{elapsed}ms", "Unreachable")
        results["ollama"] = False

    # 6. FastAPI Backend
    start = time.perf_counter()
    status_code, body = http_get("http://localhost:8000/api/v1/health")
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    if status_code == 200:
        print_row("6. FastAPI Health", "http://localhost:8000", "OK", f"{elapsed}ms", "Liveness probe healthy")
        results["fastapi_health"] = True
    else:
        print_row("6. FastAPI Health", "http://localhost:8000", "FAIL", f"{elapsed}ms", f"HTTP {status_code}")
        results["fastapi_health"] = False

    # 6b. FastAPI Readiness (Deep Dependency Ping)
    start = time.perf_counter()
    status_code, body = http_get("http://localhost:8000/api/v1/ready")
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    if status_code == 200:
        try:
            data = json.loads(body)
            overall = data.get("status")
            print_row("6b. FastAPI Ready", "http://localhost:8000", "OK", f"{elapsed}ms", f"Deep status: {overall}")
            results["fastapi_ready"] = True
        except Exception:
            print_row("6b. FastAPI Ready", "http://localhost:8000", "OK", f"{elapsed}ms", "Readiness passed")
            results["fastapi_ready"] = True
    else:
        print_row("6b. FastAPI Ready", "http://localhost:8000", "WARN", f"{elapsed}ms", f"HTTP {status_code}")
        results["fastapi_ready"] = False

    # 7. Next.js Frontend
    start = time.perf_counter()
    # A Next.js development server may compile the first route on demand.
    status_code, body = http_get("http://localhost:3000", timeout=10.0)
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    if status_code in (200, 304):
        print_row("7. Next.js App", "http://localhost:3000", "OK", f"{elapsed}ms", "App reachable")
        results["frontend"] = True
    else:
        print_row("7. Next.js App", "http://localhost:3000", "FAIL", f"{elapsed}ms", f"HTTP {status_code}")
        results["frontend"] = False

    print("=" * 90)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"{BOLD}Summary: {passed}/{total} health checks passed.{RESET}\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
