"""In-memory cache for web-retrieved (Browserbase) product data.

A /recommend response can include web-sourced cards with synthetic
product_ids that exist in neither PostgreSQL nor the static fallback
catalog. The frontend's product detail modal always makes separate follow-up
calls -- GET /products/{id}, /products/{id}/reviews, /products/{id}/images,
/products/{id}/buy-links -- after a card is shown. Without this cache those
calls 404 for web items even though the card carried real scraped specs and
reviews. Storing the same data here, keyed by product_id, lets those
endpoints resolve it for web items too, with no frontend change.

Entries use the exact same dict shape as a FALLBACK_CATALOG product so they
can be consumed by the same downstream code paths in products.py.
"""

import time
from typing import Any, Dict, Optional

_TTL_SECONDS = 3600
_cache: Dict[str, tuple] = {}


def store_web_product(product_id: str, data: Dict[str, Any]) -> None:
    _cache[product_id] = (time.time() + _TTL_SECONDS, data)


def get_web_product(product_id: str) -> Optional[Dict[str, Any]]:
    entry = _cache.get(product_id)
    if not entry:
        return None
    expires_at, data = entry
    if time.time() > expires_at:
        del _cache[product_id]
        return None
    return data
