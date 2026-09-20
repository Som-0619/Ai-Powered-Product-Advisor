"""Source discovery and domain reputation classification service."""

import hashlib
import time
from urllib.parse import urlparse
from typing import Dict, Optional, Tuple
from app.schemas.ingestion import SourceMetadata
from app.core.logging import logger


KNOWN_DOMAINS: Dict[str, Tuple[str, float]] = {
    # Distributors (trust: 0.95)
    "digikey.com": ("distributor", 0.95),
    "www.digikey.com": ("distributor", 0.95),
    "mouser.com": ("distributor", 0.95),
    "www.mouser.com": ("distributor", 0.95),
    "arrow.com": ("distributor", 0.95),
    "www.arrow.com": ("distributor", 0.95),
    "newark.com": ("distributor", 0.95),
    "element14.com": ("distributor", 0.95),
    "octopart.com": ("distributor", 0.95),

    # Manufacturers & Official Hardware (trust: 1.0)
    "espressif.com": ("manufacturer", 1.0),
    "www.espressif.com": ("manufacturer", 1.0),
    "adafruit.com": ("manufacturer", 0.98),
    "www.adafruit.com": ("manufacturer", 0.98),
    "sparkfun.com": ("manufacturer", 0.98),
    "www.sparkfun.com": ("manufacturer", 0.98),
    "ti.com": ("manufacturer", 1.0),
    "www.ti.com": ("manufacturer", 1.0),
    "st.com": ("manufacturer", 1.0),
    "www.st.com": ("manufacturer", 1.0),
    "raspberrypi.com": ("manufacturer", 1.0),
    "www.raspberrypi.com": ("manufacturer", 1.0),
    "nvidia.com": ("manufacturer", 1.0),
    "www.nvidia.com": ("manufacturer", 1.0),
    "amd.com": ("manufacturer", 1.0),
    "intel.com": ("manufacturer", 1.0),
    "asus.com": ("manufacturer", 0.95),
    "apple.com": ("manufacturer", 1.0),

    # Consumer Retailers (trust: 0.85)
    "bestbuy.com": ("retailer", 0.85),
    "www.bestbuy.com": ("retailer", 0.85),
    "microcenter.com": ("retailer", 0.90),
    "www.microcenter.com": ("retailer", 0.90),
    "newegg.com": ("retailer", 0.85),
    "bhphotovideo.com": ("retailer", 0.90),
    "amazon.com": ("retailer", 0.80),
    "www.amazon.com": ("retailer", 0.80),

    # Community / Forums (trust: 0.60)
    "github.com": ("community", 0.70),
    "reddit.com": ("community", 0.55),
    "hackaday.com": ("community", 0.65),
    "instructables.com": ("community", 0.60),
}


class SourceDiscoveryService:
    """Discovers, classifies, and assesses trust of external web sources."""

    def discover_source(self, url: str, content_hash: Optional[str] = None) -> SourceMetadata:
        """Analyze a URL, extract its domain, classify source type and trust rating."""
        parsed = urlparse(url.strip())
        domain = (parsed.netloc or "").lower()
        if not domain:
            raise ValueError(f"Invalid URL '{url}' has no domain netloc.")

        # Match known domain or find base domain
        source_type = "retailer"
        trust_score = 0.50

        if domain in KNOWN_DOMAINS:
            source_type, trust_score = KNOWN_DOMAINS[domain]
        else:
            # Check domain suffix
            for known_host, (stype, score) in KNOWN_DOMAINS.items():
                if domain.endswith(f".{known_host}"):
                    source_type = stype
                    trust_score = score
                    break

        now = time.time()
        c_hash = content_hash or hashlib.sha256(url.encode("utf-8")).hexdigest()

        return SourceMetadata(
            source_url=url,
            domain=domain,
            crawl_time=now,
            last_seen=now,
            content_hash=c_hash,
            source_type=source_type,
            trust_score=trust_score,
        )

    def is_allowed_source_type(self, source_type: str) -> bool:
        """Check if source type is acceptable for ingestion."""
        return source_type in {
            "retailer",
            "distributor",
            "manufacturer",
            "datasheet",
            "community",
        }
