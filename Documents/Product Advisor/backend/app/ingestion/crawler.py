"""Crawler service executing asynchronous, safe, and rate-limited web requests."""

import asyncio
import hashlib
import time
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse
import httpx

from app.core.logging import logger
from app.security.ssrf import SSRFValidator, SSRFSecurityError
from app.ingestion.robots import RobotsManager, DomainRateLimiter, RobotsDisallowedError
from app.schemas.ingestion import RawCrawlPayload


class CrawlerError(Exception):
    """Base exception for crawler failures."""
    pass


class CrawlerService:
    """Production-grade asynchronous web crawler with SSRF protection, robots.txt, and rate limiting."""

    USER_AGENT = "ProductAdvisorBot/1.0 (+https://productadvisor.local/bot)"
    MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MB

    def __init__(
        self,
        robots_manager: Optional[RobotsManager] = None,
        rate_limiter: Optional[DomainRateLimiter] = None,
        max_retries: int = 3,
        base_backoff_seconds: float = 0.5,
    ):
        self.robots_manager = robots_manager or RobotsManager()
        self.rate_limiter = rate_limiter or DomainRateLimiter()
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        # Mock handlers for offline testing / deterministic tests
        self._mock_responses: Dict[str, Dict[str, Any]] = {}

    def register_mock_url(
        self,
        url: str,
        status_code: int = 200,
        content: str = "",
        headers: Optional[Dict[str, str]] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        """Register a mock URL response for testing without internet access."""
        self._mock_responses[url] = {
            "status_code": status_code,
            "content": content,
            "headers": headers or {"content-type": "text/html; charset=utf-8"},
            "exception": exception,
        }

    async def crawl(self, url: str) -> RawCrawlPayload:
        """Execute a secure crawl of a single URL, with SSRF protection and retry logic."""
        url = url.strip()

        # 1. SSRF Validation
        SSRFValidator.validate_url(url)

        parsed = urlparse(url)
        domain = (parsed.netloc or "").lower()

        # 2. Check Robots.txt
        can_fetch = await self.robots_manager.can_fetch(url)
        if not can_fetch:
            raise RobotsDisallowedError(f"Crawling URL '{url}' is disallowed by robots.txt")

        # 3. Asynchronous HTTP Fetch with Exponential Backoff Retry
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                # Polite domain rate limit wait
                await self.rate_limiter.wait_for_domain(domain)

                # Check Mock Responses (for isolated testing)
                if url in self._mock_responses:
                    mock = self._mock_responses[url]
                    if mock["exception"]:
                        raise mock["exception"]
                    body_text = mock["content"]
                    c_hash = hashlib.sha256(body_text.encode("utf-8")).hexdigest()
                    return RawCrawlPayload(
                        url=url,
                        status_code=mock["status_code"],
                        content=body_text,
                        content_bytes=len(body_text.encode("utf-8")),
                        content_type=mock["headers"].get("content-type", "text/html"),
                        headers=mock["headers"],
                        crawl_time=time.time(),
                        content_hash=c_hash,
                    )


                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(10.0, connect=5.0),
                    follow_redirects=True,
                    max_redirects=5,
                    headers={
                        "User-Agent": self.USER_AGENT,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    },
                ) as client:
                    resp = await client.get(url)

                    # Re-verify target URL after redirects to prevent redirect SSRF
                    if str(resp.url) != url:
                        SSRFValidator.validate_url(str(resp.url))

                    # Check transient HTTP statuses (503, 429, 502, 504)
                    if resp.status_code in (429, 502, 503, 504):
                        raise httpx.HTTPStatusError(
                            f"Server returned transient {resp.status_code}",
                            request=resp.request,
                            response=resp,
                        )

                    # Raise for client errors (404, 403, 401) without retry
                    resp.raise_for_status()

                    # Safety check on response size
                    content_bytes = resp.content
                    if len(content_bytes) > self.MAX_RESPONSE_BYTES:
                        raise CrawlerError(
                            f"Response size {len(content_bytes)} exceeds max allowed {self.MAX_RESPONSE_BYTES} bytes."
                        )

                    content_text = resp.text
                    c_hash = hashlib.sha256(content_bytes).hexdigest()

                    headers_dict = {k.lower(): v for k, v in resp.headers.items()}

                    return RawCrawlPayload(
                        url=str(resp.url),
                        status_code=resp.status_code,
                        content=content_text,
                        content_bytes=len(content_bytes),
                        content_type=headers_dict.get("content-type", "text/html"),
                        headers=headers_dict,
                        crawl_time=time.time(),
                        content_hash=c_hash,
                    )

            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in (429, 502, 503, 504):
                    last_error = exc
                    logger.warning(
                        f"Transient HTTP {exc.response.status_code} on attempt {attempt}/{self.max_retries} for '{url}'"
                    )
                    if attempt < self.max_retries:
                        backoff = self.base_backoff_seconds * (2 ** (attempt - 1))
                        await asyncio.sleep(backoff)
                        continue
                    break
                raise CrawlerError(f"HTTP {exc.response.status_code} client error for '{url}': {exc}") from exc
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
                logger.warning(
                    f"Crawl attempt {attempt}/{self.max_retries} failed for '{url}': {exc}"
                )
                if attempt < self.max_retries:
                    backoff = self.base_backoff_seconds * (2 ** (attempt - 1))
                    await asyncio.sleep(backoff)
                else:
                    break
            except Exception as exc:
                # Permanent non-retriable error
                raise CrawlerError(f"Crawl failed for '{url}': {exc}") from exc


        raise CrawlerError(
            f"Failed to crawl '{url}' after {self.max_retries} attempts. Last error: {last_error}"
        )
