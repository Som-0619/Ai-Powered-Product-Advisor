"""Agent Tool Layer.

Provides clean, typed, service-backed tools for specialist agents.
Agents interact with data ONLY through these tools, ensuring strict separation
from raw infrastructure (PostgreSQL connection, OpenSearch client, MinIO, Redis).
"""

import asyncio
import hashlib
import json
import time
import uuid
from typing import Any, Dict, List, Optional, Union

from app.core.config import settings
from app.core.logging import logger
from app.services.factory import (
    get_search_service,
    get_cache_service,
    get_storage_service,
)
from app.services.product_catalog_service import ProductCatalogService
from app.services.product_image_service import (
    ProductImageService,
    ImageOwnershipError,
    ImageNotFoundError,
)


from app.models.catalog import CANONICAL_ELECTRONICS_CATEGORIES

DEFAULT_TOOL_TIMEOUT = 10.0


async def search_products(
    query: str,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    mode: str = "hybrid",
    limit: int = 10,
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> List[Dict[str, Any]]:
    """Search products catalog using OpenSearch candidates and PostgreSQL hydration."""
    search_service = get_search_service()
    catalog_service = ProductCatalogService()

    norm_cat = None
    if category:
        c_clean = category.strip().lower()
        for canonical in CANONICAL_ELECTRONICS_CATEGORIES:
            if c_clean == canonical.lower() or canonical.lower() in c_clean or c_clean in canonical.lower():
                norm_cat = canonical
                break
        if not norm_cat:
            norm_cat = category

    active_filters = dict(filters or {})
    if norm_cat:
        active_filters["category"] = norm_cat
    if brand:
        active_filters["brand"] = brand

    async def _execute():
        t_os = time.perf_counter()
        if mode == "keyword":
            resp = await search_service.search_keyword(query, filters=active_filters, limit=limit)
        elif mode == "vector":
            resp = await search_service.search_vector(query, filters=active_filters, limit=limit)
        else:
            resp = await search_service.search_hybrid(query, filters=active_filters, limit=limit)

        # If strict category/brand filter returned 0 hits, retry relaxed so natural query matches catalog
        if not resp.hits and ("category" in active_filters or "brand" in active_filters):
            relaxed_filters = {k: v for k, v in active_filters.items() if k not in ("category", "brand")}
            if mode == "keyword":
                resp = await search_service.search_keyword(query, filters=relaxed_filters, limit=limit)
            elif mode == "vector":
                resp = await search_service.search_vector(query, filters=relaxed_filters, limit=limit)
            else:
                resp = await search_service.search_hybrid(query, filters=relaxed_filters, limit=limit)

        os_latency_ms = round((time.perf_counter() - t_os) * 1000, 2)
        os_result_count = len(resp.hits) if resp and resp.hits else 0
        logger.info(
            f"[DEV_TRACE] OpenSearch latency: {os_latency_ms}ms, OpenSearch result count: {os_result_count}",
            extra={"opensearch_latency_ms": os_latency_ms, "opensearch_result_count": os_result_count},
        )

        if not resp.hits:
            return []

        pids = [h.id for h in resp.hits]
        t_pg = time.perf_counter()
        products = await catalog_service.get_products_by_ids(pids)
        pg_latency_ms = round((time.perf_counter() - t_pg) * 1000, 2)
        pg_result_count = len(products)
        logger.info(
            f"[DEV_TRACE] PostgreSQL latency: {pg_latency_ms}ms, PostgreSQL result count: {pg_result_count}",
            extra={"postgresql_latency_ms": pg_latency_ms, "postgresql_result_count": pg_result_count},
        )
        prod_map = {str(p.id): p for p in products}

        results = []
        for h in resp.hits:
            p = prod_map.get(h.id)
            if not p:
                continue

            primary_image_url = None
            if p.images:
                primary_img = next((img for img in p.images if img.is_primary), p.images[0])
                primary_image_url = primary_img.image_url

            from app.services.retailer_offers import resolve_product_retailer_offers
            stored_offers = [
                {
                    "retailer": o.retailer,
                    "price": float(o.price) if o.price is not None else None,
                    "url": o.url,
                    "currency": o.currency or "INR",
                    "availability_status": o.availability_status,
                    "verification_status": o.verification_status,
                    "external_product_id": getattr(o, "external_product_id", None),
                    "last_verified": o.last_verified.isoformat() if getattr(o, "last_verified", None) else None,
                }
                for o in (p.retailer_offers or [])
            ]
            resolved_offers, az_url, fk_url, lowest_verified_price = resolve_product_retailer_offers(
                product_id=str(p.id),
                title=p.title or "",
                brand=p.brand or "",
                model=p.model or "",
                variant=p.variant or "",
                external_product_id=p.external_product_id,
                stored_offers=stored_offers,
            )

            price = lowest_verified_price
            formatted_price = f"₹{int(price):,}" if price is not None and price.is_integer() else (f"₹{price:,.2f}" if price is not None else "Price unavailable")

            results.append({
                "product_id": str(p.id),
                "brand": p.brand or "",
                "model": p.model or "",
                "title": p.title or "",
                "variant": p.variant or "",
                "category": p.category or "",
                "subcategory": p.subcategory or "",
                "description": p.description or "",
                "relevance_score": h.score,
                "matched_fields": h.highlights or {},
                "price": price,
                "formatted_price": formatted_price,
                "amazon_url": az_url,
                "flipkart_url": fk_url,
                "retailer_offers": resolved_offers,
                "buy_links": resolved_offers,
                "specifications": p.specifications or {},
                "primary_image_url": primary_image_url,
                "basic_product_context": (
                    f"{p.brand or ''} {p.model or ''} ({p.category or ''}). "
                    f"{p.description or ''}"
                ).strip(),
            })
        return results

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"search_products timed out after {timeout}s for query: {query}")
        return []
    except Exception as exc:
        logger.error(f"search_products tool failed: {exc}")
        return []


async def get_product(
    product_id: Union[uuid.UUID, str],
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> Optional[Dict[str, Any]]:
    """Fetch canonical product entity by stable product_id."""
    catalog_service = ProductCatalogService()

    async def _execute():
        p = await catalog_service.get_product(product_id)
        if not p:
            return None

        primary_image_url = None
        if p.images:
            primary_img = next((img for img in p.images if img.is_primary), p.images[0])
            primary_image_url = primary_img.image_url

        from app.services.retailer_offers import resolve_product_retailer_offers
        stored_offers = [
            {
                "retailer": o.retailer,
                "price": float(o.price) if o.price is not None else None,
                "url": o.url,
                "currency": o.currency or "INR",
                "availability_status": o.availability_status,
                "verification_status": o.verification_status,
                "external_product_id": getattr(o, "external_product_id", None),
                "last_verified": o.last_verified.isoformat() if getattr(o, "last_verified", None) else None,
            }
            for o in (p.retailer_offers or [])
        ]
        resolved_offers, az_url, fk_url, lowest_verified_price = resolve_product_retailer_offers(
            product_id=str(p.id),
            title=p.title or "",
            brand=p.brand or "",
            model=p.model or "",
            variant=p.variant or "",
            external_product_id=p.external_product_id,
            stored_offers=stored_offers,
        )
        price = lowest_verified_price
        formatted_price = f"₹{int(price):,}" if price is not None and price.is_integer() else (f"₹{price:,.2f}" if price is not None else "Price unavailable")

        return {
            "product_id": str(p.id),
            "id": str(p.id),
            "title": p.title or "",
            "brand": p.brand or "",
            "model": p.model or "",
            "variant": p.variant or "",
            "category": p.category or "",
            "subcategory": p.subcategory or "",
            "description": p.description or "",
            "specifications": p.specifications or {},
            "model_number": p.model_number or "",
            "sku": p.sku or "",
            "price": price,
            "formatted_price": formatted_price,
            "amazon_url": az_url,
            "flipkart_url": fk_url,
            "retailer_offers": resolved_offers,
            "buy_links": resolved_offers,
            "primary_image_url": primary_image_url,
            "is_component": bool(p.is_component),
        }

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"get_product failed for {product_id}: {exc}")
        return None


async def get_product_variants(
    product_id: Union[uuid.UUID, str],
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> List[Dict[str, Any]]:
    """Fetch all canonical variants strictly belonging to product_id."""
    catalog_service = ProductCatalogService()

    async def _execute():
        variants = await catalog_service.get_product_variants(product_id)
        return [
            {
                "variant_id": str(v.id),
                "product_id": str(v.product_id),
                "variant_name": v.variant_name or v.title or "",
                "sku": v.sku or "",
                "specifications": v.specifications or v.attributes or {},
            }
            for v in variants
        ]

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"get_product_variants failed for {product_id}: {exc}")
        return []


async def get_product_images(
    product_id: Union[uuid.UUID, str],
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> List[Dict[str, Any]]:
    """Fetch all verified images strictly belonging to product_id."""
    image_service = ProductImageService()

    async def _execute():
        images = await image_service.get_images(product_id)
        return [
            {
                "image_id": str(img.id),
                "product_id": str(img.product_id),
                "variant_id": str(img.variant_id) if img.variant_id else None,
                "image_url": img.image_url,
                "storage_key": img.storage_key,
                "image_type": img.image_type,
                "is_primary": bool(img.is_primary),
                "verified": bool(img.verified),
            }
            for img in images
        ]

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"get_product_images failed for {product_id}: {exc}")
        return []


async def get_product_reviews(
    product_id: Union[uuid.UUID, str],
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> List[Dict[str, Any]]:
    """Fetch canonical customer reviews strictly belonging to product_id."""
    catalog_service = ProductCatalogService()

    async def _execute():
        reviews = await catalog_service.get_product_reviews(product_id)
        return [
            {
                "review_id": str(r.id),
                "product_id": str(r.product_id),
                "title": r.title or "",
                "body": r.body or "",
                "rating": float(r.rating) if r.rating is not None else None,
                "sentiment": r.sentiment or "neutral",
                "is_verified_purchase": bool(r.is_verified_purchase),
            }
            for r in reviews
        ]

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"get_product_reviews failed for {product_id}: {exc}")
        return []


async def get_retailer_offers(
    product_id: Union[uuid.UUID, str],
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> List[Dict[str, Any]]:
    """Fetch external retailer offers strictly belonging to product_id.

    Returns status: available, unavailable, or unknown.
    """
    catalog_service = ProductCatalogService()

    async def _execute():
        p = await catalog_service.get_product(product_id)
        if not p:
            from app.services.catalog_fallback import get_fallback_product
            fb = get_fallback_product(str(product_id))
            if fb:
                from app.services.retailer_offers import resolve_product_retailer_offers
                resolved, _, _, _ = resolve_product_retailer_offers(
                    product_id=str(product_id),
                    title=fb.get("title", ""),
                    brand=fb.get("brand"),
                    model=fb.get("model"),
                    variant=fb.get("variant"),
                    external_product_id=fb.get("external_product_id") or fb.get("asin"),
                    stored_offers=fb.get("retailer_offers") or fb.get("buy_links") or [],
                )
                return resolved
            return []

        from app.services.retailer_offers import resolve_product_retailer_offers
        stored = [
            {
                "retailer": o.retailer,
                "price": float(o.price) if o.price is not None else None,
                "url": o.url,
                "currency": o.currency or "INR",
                "availability_status": o.availability_status,
                "verification_status": o.verification_status,
                "external_product_id": getattr(o, "external_product_id", None),
                "last_verified": o.last_verified.isoformat() if getattr(o, "last_verified", None) else None,
            }
            for o in (p.retailer_offers or [])
        ]
        resolved, _, _, _ = resolve_product_retailer_offers(
            product_id=str(p.id),
            title=p.title or "",
            brand=p.brand or "",
            model=p.model or "",
            variant=p.variant or "",
            external_product_id=p.external_product_id,
            stored_offers=stored,
        )
        return resolved

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"get_retailer_offers failed for {product_id}: {exc}")
        return []


async def get_product_specifications(
    product_id: Union[uuid.UUID, str],
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> Dict[str, Any]:
    """Extract structured specifications for product_id."""
    catalog_service = ProductCatalogService()

    async def _execute():
        p = await catalog_service.get_product(product_id)
        if not p:
            return {}
        return p.specifications or {}

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"get_product_specifications failed for {product_id}: {exc}")
        return {}


async def get_product_context(
    product_id: Union[uuid.UUID, str],
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> Dict[str, Any]:
    """Controlled compact product context tool (Section 20).

    Returns compact summary:
    - product info
    - variants overview
    - key specifications
    - image reference
    - reviews summary
    - retailer offer status
    - sources
    Cached in Redis when available.
    """
    pid_str = str(product_id)
    cache_service = get_cache_service()
    cache_key = f"product_context:{pid_str}"

    # Try cache
    try:
        cached = await cache_service.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    catalog_service = ProductCatalogService()

    async def _execute():
        p = await catalog_service.get_product(product_id)
        if not p:
            return {"product_id": pid_str, "found": False}

        # Compact variant info
        variants_info = []
        if p.variants:
            variants_info = [
                {"variant_id": str(v.id), "title": v.variant_name or v.title or ""}
                for v in p.variants[:5]
            ]

        # Key specifications
        specs = p.specifications or {}
        key_specs = {}
        priority_keys = [
            "cpu", "processor", "gpu", "graphics", "ram", "memory",
            "storage", "ssd", "display", "screen", "resolution",
            "battery", "camera", "interface", "connectivity", "voltage",
            "current", "power", "package", "chipset"
        ]
        for k in priority_keys:
            if k in specs and specs[k]:
                key_specs[k] = specs[k]
        # If no priority keys matched, take first 5 keys
        if not key_specs and specs:
            for k, v in list(specs.items())[:5]:
                key_specs[k] = v

        # Image info
        primary_image_url = None
        images_count = len(p.images) if p.images else 0
        if p.images:
            primary_img = next((img for img in p.images if img.is_primary), p.images[0])
            primary_image_url = primary_img.image_url

        # Reviews summary
        reviews_count = len(p.reviews) if p.reviews else 0
        avg_rating = None
        if p.reviews:
            ratings = [r.rating for r in p.reviews if r.rating is not None]
            if ratings:
                avg_rating = round(sum(ratings) / len(ratings), 2)

        # Retailer offers status
        lowest_price = None
        availability = "unknown"
        if p.retailer_offers:
            valid_offers = [o for o in p.retailer_offers if o.price is not None and o.price > 0]
            if valid_offers:
                lowest_price = float(min(o.price for o in valid_offers))
            statuses = [o.availability_status for o in p.retailer_offers if o.availability_status]
            if "available" in statuses:
                availability = "available"
            elif all(s == "unavailable" for s in statuses):
                availability = "unavailable"

        # Provenance sources
        sources = [s.source_type for s in p.sources] if p.sources else []

        context = {
            "product_id": pid_str,
            "found": True,
            "title": p.title or f"{p.brand or ''} {p.model or ''}".strip(),
            "brand": p.brand or "",
            "model": p.model or "",
            "variant": p.variant or "",
            "category": p.category or "",
            "subcategory": p.subcategory or "",
            "description": p.description or "",
            "key_specifications": key_specs,
            "variants_count": len(p.variants) if p.variants else 0,
            "variants": variants_info,
            "primary_image_url": primary_image_url,
            "images_count": images_count,
            "reviews_count": reviews_count,
            "average_rating": avg_rating,
            "lowest_price": lowest_price,
            "availability_status": availability,
            "sources": sources,
        }

        # Cache in Redis for 10 minutes
        try:
            await cache_service.set(cache_key, json.dumps(context), expire_seconds=600)
        except Exception:
            pass

        return context

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"get_product_context failed for {product_id}: {exc}")
        return {"product_id": pid_str, "found": False, "error": str(exc)}


async def check_compatibility_context(
    first_product_id: Union[uuid.UUID, str],
    second_product_id: Union[uuid.UUID, str],
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> Dict[str, Any]:
    """Retrieve specifications of both products and extract electrical/hardware compatibility context."""
    catalog_service = ProductCatalogService()

    async def _execute():
        p1 = await catalog_service.get_product(first_product_id)
        p2 = await catalog_service.get_product(second_product_id)

        if not p1 or not p2:
            missing = []
            if not p1:
                missing.append(str(first_product_id))
            if not p2:
                missing.append(str(second_product_id))
            return {
                "status": "insufficient_information",
                "reason": f"Product(s) not found in catalog: {', '.join(missing)}",
                "p1_specs": {},
                "p2_specs": {},
            }

        s1 = p1.specifications or {}
        s2 = p2.specifications or {}

        # Extract interfaces, operating voltage, protocols
        return {
            "p1_id": str(p1.id),
            "p1_name": p1.title or f"{p1.brand or ''} {p1.model or ''}",
            "p1_category": p1.category,
            "p1_specs": s1,
            "p2_id": str(p2.id),
            "p2_name": p2.title or f"{p2.brand or ''} {p2.model or ''}",
            "p2_category": p2.category,
            "p2_specs": s2,
        }

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"check_compatibility_context failed: {exc}")
        return {"status": "error", "error": str(exc)}


async def analyze_product_image(
    product_id: Union[uuid.UUID, str],
    image_id: Optional[Union[uuid.UUID, str]] = None,
    claims: Optional[List[str]] = None,
    timeout: float = DEFAULT_TOOL_TIMEOUT,
) -> Dict[str, Any]:
    """Enforces Image Safety Rule: strictly verifies image exists and belongs to product_id

    before calling VisionAgent.
    """
    image_service = ProductImageService()
    storage_service = get_storage_service()

    async def _execute():
        images = await image_service.get_images(product_id)
        if not images:
            return {
                "status": "error",
                "error_type": "image_not_found",
                "message": f"No verified images exist for product {product_id}",
            }

        target_img = None
        if image_id:
            img_id_str = str(image_id)
            for img in images:
                if str(img.id) == img_id_str:
                    target_img = img
                    break
            if not target_img:
                return {
                    "status": "error",
                    "error_type": "ownership_mismatch",
                    "message": f"Image {image_id} does not belong to product {product_id}",
                }
        else:
            target_img = next((img for img in images if img.is_primary), images[0])

        # Resolve image bytes via StorageService
        image_bytes = None
        storage_key = target_img.storage_key
        if storage_key and not storage_key.startswith("http") and not storage_key.startswith("data:"):
            try:
                image_bytes = await storage_service.get_object(storage_key)
            except Exception as exc:
                logger.warning(f"Could not load image bytes for {storage_key}: {exc}")

        # Fallback dummy 1x1 image bytes if binary not loaded to permit metadata analysis
        if not image_bytes:
            image_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"

        from app.agents.vision import VisionAgent
        vision_agent = VisionAgent()
        result = await vision_agent.analyze_image(
            image_bytes=image_bytes,
            image_source=target_img.image_url,
            related_claims=claims,
            product_id=str(product_id),
            image_product_id=str(target_img.product_id),
            image_id=str(target_img.id),
            view_type=target_img.image_type,
            image_url=target_img.image_url,
        )

        return {
            "status": "success",
            "product_id": str(product_id),
            "image_id": str(target_img.id),
            "image_url": target_img.image_url,
            "observations": [obs.model_dump() for obs in result.observations],
            "verified": result.verified,
        }

    try:
        return await asyncio.wait_for(_execute(), timeout=timeout)
    except Exception as exc:
        logger.error(f"analyze_product_image failed: {exc}")
        return {"status": "error", "error": str(exc)}
