"""Search endpoint router implementing BM25, Vector, and Hybrid search with PostgreSQL hydration."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.services.factory import get_search_service
from app.services.product_catalog_service import ProductCatalogService
from app.schemas.search import SearchResponse

router = APIRouter(tags=["search"])


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    category: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    gpu: Optional[str] = None
    cpu: Optional[str] = None
    mode: str = Field("hybrid", description="Retrieval mode: keyword, vector, or hybrid")
    keyword_weight: Optional[float] = None
    vector_weight: Optional[float] = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SearchProductResult(BaseModel):
    product_id: str
    score: float
    matched_fields: Dict[str, Any] = Field(default_factory=dict)
    product: Dict[str, Any]
    primary_image_url: Optional[str] = None


class SearchAPIResponse(BaseModel):
    query: str
    search_mode: str
    total: int
    results: List[SearchProductResult]
    latency_ms: float
    debug: Optional[Dict[str, Any]] = None


async def _enrich_candidates(
    search_resp: SearchResponse,
    catalog_service: ProductCatalogService,
) -> List[SearchProductResult]:
    """Hydrate OpenSearch candidate IDs with fresh authoritative PostgreSQL product data."""
    if not search_resp.hits:
        return []

    candidate_ids = [h.id for h in search_resp.hits]
    products = await catalog_service.get_products_by_ids(candidate_ids)
    prod_map = {str(p.id): p for p in products}

    results: List[SearchProductResult] = []
    for hit in search_resp.hits:
        p = prod_map.get(hit.id)
        if not p:
            continue

        primary_image_url = None
        if p.images:
            primary_img = next(
                (img for img in p.images if img.is_primary), p.images[0]
            )
            primary_image_url = primary_img.image_url

        prod_dict = {
            "id": str(p.id),
            "title": p.title,
            "brand": p.brand,
            "model": p.model,
            "variant": p.variant,
            "category": p.category,
            "subcategory": p.subcategory,
            "description": p.description,
            "specifications": p.specifications or {},
            "model_number": p.model_number,
            "sku": p.sku,
            "is_component": p.is_component,
            "variants_count": len(p.variants) if p.variants else 0,
            "offers_count": len(p.retailer_offers) if p.retailer_offers else 0,
        }

        results.append(
            SearchProductResult(
                product_id=hit.id,
                score=hit.score,
                matched_fields=hit.highlights or {},
                product=prod_dict,
                primary_image_url=primary_image_url,
            )
        )

    return results


def _build_debug_info(
    q: str,
    mode: str,
    search_resp: SearchResponse,
) -> Optional[Dict[str, Any]]:
    if not settings.DEBUG:
        return None
    return {
        "query": q,
        "search_mode": mode,
        "total_candidates": search_resp.total,
        "returned_product_ids": [h.id for h in search_resp.hits],
        "scores": [h.score for h in search_resp.hits],
    }


def _clean_filters(filters_in: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = {}
    for k, v in filters_in.items():
        if v is not None and v != "" and not hasattr(v, "default"):
            cleaned[k] = v
    return cleaned


async def _execute_search(
    q: str,
    filters: Dict[str, Any],
    mode: str = "keyword",
    limit: int = 10,
    offset: int = 0,
    keyword_weight: Optional[float] = None,
    vector_weight: Optional[float] = None,
) -> SearchAPIResponse:
    clean_q = q.strip() if q else ""
    if not clean_q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty or whitespace.",
        )

    clean_f = _clean_filters(filters)
    search_service = get_search_service()
    catalog_service = ProductCatalogService()

    try:
        if mode == "vector":
            resp = await search_service.search_vector(
                clean_q, filters=clean_f, limit=limit, offset=offset
            )
        elif mode == "hybrid":
            resp = await search_service.search_hybrid(
                clean_q,
                filters=clean_f,
                keyword_weight=keyword_weight,
                vector_weight=vector_weight,
                limit=limit,
                offset=offset,
            )
        else:
            resp = await search_service.search_keyword(
                clean_q, filters=clean_f, limit=limit, offset=offset
            )
    except Exception as exc:
        logger.error(f"Search retrieval failed for query '{clean_q}': {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Search service error: {exc}",
        )

    enriched = await _enrich_candidates(resp, catalog_service)
    debug_data = _build_debug_info(clean_q, resp.search_mode, resp)

    return SearchAPIResponse(
        query=clean_q,
        search_mode=resp.search_mode,
        total=resp.total,
        results=enriched,
        latency_ms=resp.latency_ms,
        debug=debug_data,
    )


@router.get("/search", response_model=SearchAPIResponse)
async def search_get(
    q: str = Query(..., min_length=1, description="Search query"),
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    ram: Optional[str] = Query(None),
    storage: Optional[str] = Query(None),
    gpu: Optional[str] = Query(None),
    cpu: Optional[str] = Query(None),
    mode: str = Query("keyword", description="keyword, vector, or hybrid"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Execute product search. Default mode is BM25 keyword search."""
    return await _execute_search(
        q=q,
        filters={
            "category": category,
            "subcategory": subcategory,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
            "ram": ram,
            "storage": storage,
            "gpu": gpu,
            "cpu": cpu,
        },
        mode=mode,
        limit=limit,
        offset=offset,
    )


@router.get("/search/semantic", response_model=SearchAPIResponse)
async def semantic_search_get(
    q: str = Query(..., min_length=1, description="Semantic search query"),
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Execute dense vector k-NN semantic search."""
    return await _execute_search(
        q=q,
        filters={
            "category": category,
            "subcategory": subcategory,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
        },
        mode="vector",
        limit=limit,
        offset=offset,
    )


@router.get("/search/hybrid", response_model=SearchAPIResponse)
async def hybrid_search_get(
    q: str = Query(..., min_length=1, description="Hybrid search query"),
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    keyword_weight: Optional[float] = Query(None),
    vector_weight: Optional[float] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Execute hybrid search fusing BM25 keyword and dense vector similarity."""
    return await _execute_search(
        q=q,
        filters={
            "category": category,
            "subcategory": subcategory,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
        },
        mode="hybrid",
        limit=limit,
        offset=offset,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
    )


@router.post("/search", response_model=SearchAPIResponse)
async def search_post(request: SearchRequest):
    """Execute structured search (BM25, vector, or hybrid)."""
    return await _execute_search(
        q=request.query,
        filters={
            "category": request.category,
            "subcategory": request.subcategory,
            "brand": request.brand,
            "min_price": request.min_price,
            "max_price": request.max_price,
            "ram": request.ram,
            "storage": request.storage,
            "gpu": request.gpu,
            "cpu": request.cpu,
        },
        mode=request.mode,
        limit=request.limit,
        offset=request.offset,
        keyword_weight=request.keyword_weight,
        vector_weight=request.vector_weight,
    )

