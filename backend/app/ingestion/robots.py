"""Robots.txt parser and per-domain rate limiter."""

import asyncio
import time
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import urllib.robotparser
import httpx
from app.core.logging import logger
from app.security.ssrf import SSRFValidator


class RobotsDisallowedError(ValueError):
    """Raised when crawling a path is forbidden by robots.txt."""
    pass


class RobotsManager:
    """Fetches, parses, and caches robots.txt rules per origin."""

    USER_AGENT = "ProductAdvisorBot/1.0"

    def __init__(self, cache_ttl_seconds: int = 3600):
        self._cache: Dict[str, Tuple[urllib.robotparser.RobotFileParser, float]] = {}
        self._cache_ttl = cache_ttl_seconds
        # In-memory mock overrides for testing
        self._mock_rules: Dict[str, str] = {}

    def set_mock_robots_txt(self, domain: str, content: str) -> None:
        """Register a mock robots.txt content for testing."""
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(content.splitlines())
        self._cache[domain.lower()] = (parser, time.time() + 999999)

    async def can_fetch(self, url: str) -> bool:
        """Check whether ProductAdvisorBot is allowed to fetch the URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path or "/"

        parser = await self._get_parser_for_origin(parsed.scheme, domain)
        if parser is None:
            # If robots.txt could not be retrieved (e.g. 404), crawling is permitted
            return True

        allowed = parser.can_fetch(self.USER_AGENT, url)
        # Fallback to wildcard user agent if not explicitly defined
        if not allowed:
            allowed = parser.can_fetch("*", url)

        return allowed

    async def _get_parser_for_origin(
        self, scheme: str, domain: str
    ) -> Optional[urllib.robotparser.RobotFileParser]:
        """Retrieve cached parser or fetch robots.txt asynchronously."""
        now = time.time()
        if domain in self._cache:
            parser, expiry = self._cache[domain]
            if now < expiry:
                return parser

        robots_url = f"{scheme}://{domain}/robots.txt"
        try:
            # Validate URL with SSRF protection before fetching
            SSRFValidator.validate_url(robots_url)

            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                resp = await client.get(
                    robots_url,
                    headers={"User-Agent": self.USER_AGENT},
                )
                if resp.status_code == 200:
                    parser = urllib.robotparser.RobotFileParser()
                    parser.parse(resp.text.splitlines())
                    self._cache[domain] = (parser, now + self._cache_ttl)
                    return parser
                elif resp.status_code in (401, 403):
                    # Disallow all if access to robots.txt is forbidden
                    parser = urllib.robotparser.RobotFileParser()
                    parser.parse(["User-agent: *", "Disallow: /"])
                    self._cache[domain] = (parser, now + self._cache_ttl)
                    return parser
                else:
                    # 404 or other status means no restrictions
                    parser = urllib.robotparser.RobotFileParser()
                    parser.parse([])
                    self._cache[domain] = (parser, now + self._cache_ttl)
                    return parser
        except Exception as exc:
            logger.warning(
                f"Could not fetch robots.txt for {domain}: {exc}. Defaulting to permissive."
            )
            parser = urllib.robotparser.RobotFileParser()
            parser.parse([])
            self._cache[domain] = (parser, now + 300)  # short retry TTL
            return parser


class DomainRateLimiter:
    """Polite per-domain crawler rate limiter."""

    def __init__(self, min_delay_seconds: float = 1.0):
        self.min_delay = min_delay_seconds
        self._last_request_time: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def wait_for_domain(self, domain: str) -> float:
        """Wait if necessary to ensure polite crawl delay for domain."""
        domain = domain.lower()
        delay_slept = 0.0
        async with self._lock:
            now = time.time()
            last_time = self._last_request_time.get(domain, 0.0)
            elapsed = now - last_time
            if elapsed < self.min_delay:
                delay_slept = self.min_delay - elapsed
                await asyncio.sleep(delay_slept)
            self._last_request_time[domain] = time.time()
        return delay_slept
