"""Products detail, reviews, and evidence endpoint router."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.services.factory import get_db_service
from app.services.catalog_service import CatalogService
from app.services.catalog_fallback import get_fallback_product, get_product_images
from app.services.retailer_offers import (
    get_canonical_product_offers,
    get_canonical_comparison,
)
from app.models.catalog import Product, Specification
from app.models.reviews import Review
from app.models.media import Document

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{id}")
async def get_product(id: str):
    """Retrieve product details with specifications and component profiles."""
    # Try DB first if available
    try:
        product_uuid = uuid.UUID(id)
        db = get_db_service()
        async with db.session() as session:
            catalog = CatalogService(session)
            product = await catalog.get_product_details(product_uuid)
            if product:
                specs_dict = {s.key: s.value for s in product.specifications}
                component_data = None
                if product.component_profile:
                    comp = product.component_profile
                    component_data = {
                        "part_number": comp.part_number,
                        "package_type": comp.package_type,
                        "pin_count": comp.pin_count,
                        "mounting_type": comp.mounting_type,
                        "datasheet_url": comp.datasheet_url,
                        "specs": comp.specifications_json,
                    }
                prices_list = []
                for p in getattr(product, "prices", []):
                    prices_list.append({
                        "amount": float(p.amount),
                        "currency": p.currency,
                        "is_current": getattr(p, "is_current", True),
                    })
                offers = get_canonical_product_offers(str(product.id))
                return {
                    "status": "success",
                    "id": str(product.id),
                    "product_id": str(product.id),
                    "title": product.title,
                    "slug": product.slug,
                    "description": product.description,
                    "brand": product.brand.name if product.brand else None,
                    "category": product.category.name if product.category else None,
                    "category_slug": product.category.slug if product.category else None,
                    "model_number": product.model_number,
                    "sku": product.sku,
                    "is_component": product.is_component,
                    "specifications": specs_dict,
                    "component_profile": component_data,
                    "prices": prices_list,
                    "retailer_offers": offers,
                    "buy_links": offers,
                }
    except Exception:
        pass

    # Fallback to in-memory catalog
    fallback = get_fallback_product(id)
    if fallback:
        offers = get_canonical_product_offers(fallback["id"])
        if not offers:
            offers = fallback.get("retailer_offers") or fallback.get("buy_links", [])
        images = get_product_images(fallback["id"], fallback.get("external_product_id") or fallback.get("asin"))
        main_img = None
        for im in images:
            if im.get("image_type") in ("primary", "front"):
                main_img = im.get("image_url")
                break
        if not main_img and images:
            for im in images:
                if im.get("verified"):
                    main_img = im.get("image_url")
                    break
        if not main_img:
            main_img = fallback.get("image_url")
        return {
            "status": "success",
            "id": fallback["id"],
            "product_id": fallback["id"],
            "external_product_id": fallback.get("external_product_id") or fallback.get("asin"),
            "title": fallback["title"],
            "slug": fallback.get("slug", ""),
            "description": fallback.get("description", ""),
            "brand": fallback.get("brand", ""),
            "category": fallback.get("category", ""),
            "category_slug": fallback.get("category", "").lower().replace(" ", "-"),
            "model_number": fallback.get("model_number", ""),
            "sku": fallback.get("sku", ""),
            "is_component": fallback.get("is_component", False),
            "specifications": fallback.get("specs", {}),
            "component_profile": {
                "part_number": fallback.get("title", ""),
                "voltage": fallback.get("voltage_display", "3.3V"),
                "specs": fallback.get("specs", {}),
            } if fallback.get("is_component") else None,
            "prices": [{
                "amount": fallback.get("price", 0.0),
                "currency": fallback.get("currency", "INR"),
                "is_current": True,
            }],
            "product_image": main_img,
            "image_url": main_img,
            "images": images,
            "retailer_offers": offers,
            "buy_links": offers,
            "amazon_url": fallback.get("amazon_url"),
            "flipkart_url": fallback.get("flipkart_url"),
        }

    raise HTTPException(status_code=404, detail=f"Product with id '{id}' not found")


@router.get("/{id}/images")
async def get_product_images_endpoint(id: str):
    """Retrieve verified product images for canonical product_id."""
    images = get_product_images(id)
    if not images:
        fallback = get_fallback_product(id)
        if not fallback:
            raise HTTPException(status_code=404, detail=f"Product with id '{id}' not found")
        images = get_product_images(fallback["id"])

    # Strict identity check: all returned images must reference this product_id
    verified_images = []
    for img in images:
        if img.get("product_id") and img.get("product_id") != id:
            continue
        verified_images.append(dict(img))

    return {
        "status": "success",
        "product_id": id,
        "count": len(verified_images),
        "images": verified_images,
    }


@router.get("/{id}/offers")
async def get_product_offers(id: str):
    """Retrieve normalized retailer offers for canonical product_id."""
    offers = get_canonical_product_offers(id)
    if not offers:
        fallback = get_fallback_product(id)
        if not fallback:
            raise HTTPException(status_code=404, detail=f"Product with id '{id}' not found")
        offers = fallback.get("retailer_offers") or fallback.get("buy_links", [])

    normalized = []
    for o in offers:
        if o.get("product_id") and o.get("product_id") != id:
            continue
        normalized.append(dict(o))

    return {
        "status": "success",
        "product_id": id,
        "offers": normalized,
    }


@router.get("/{id}/buy-links")
async def get_product_buy_links(id: str):
    """Retrieve canonical verified retailer buy links for product_id."""
    from app.services.retailer_offers import is_verification_stale

    offers = get_canonical_product_offers(id)
    if not offers:
        fallback = get_fallback_product(id)
        if not fallback:
            raise HTTPException(status_code=404, detail=f"Product with id '{id}' not found")
        offers = fallback.get("retailer_offers") or fallback.get("buy_links", [])

    normalized = []
    for o in offers:
        if o.get("product_id") and o.get("product_id") != id:
            continue
        normalized.append(dict(o))

    # Separate verified and available buy links from unverified/broken/unavailable
    verified = [
        o for o in normalized
        if o.get("verification_status") == "verified"
        and o.get("availability_status") == "available"
        and not is_verification_stale(o.get("last_verified"))
    ]

    return {
        "status": "success",
        "product_id": id,
        "buy_links": normalized,
        "verified_buy_links": verified,
    }


@router.get("/{id}/compare")
async def get_product_compare(id: str):
    """Retrieve canonical product marketplace comparison and offers for Compare view."""
    comparison = get_canonical_comparison(id)
    if not comparison:
        fallback = get_fallback_product(id)
        if not fallback:
            raise HTTPException(status_code=404, detail=f"Product with id '{id}' not found")
        offers = get_canonical_product_offers(id) or fallback.get("retailer_offers", [])
        comparison = {
            "product_id": id,
            "title": fallback.get("title", ""),
            "offers": offers,
            "best_deal": offers[0] if offers else None,
            "specs": fallback.get("specs", {}),
        }
    else:
        comparison["product_id"] = id
    return {
        "status": "success",
        "product_id": id,
        "comparison": comparison,
    }


@router.get("/{id}/reviews")
async def get_product_reviews(id: str):
    """Retrieve verified reviews for canonical product_id."""
    reviews_list = []
    try:
        product_uuid = uuid.UUID(id)
        db = get_db_service()
        async with db.session() as session:
            stmt = select(Review).where(Review.product_id == product_uuid)
            result = await session.execute(stmt)
            db_reviews = result.scalars().all()
            for r in db_reviews:
                reviews_list.append({
                    "id": str(r.id),
                    "product_id": id,
                    "rating": float(r.rating) if r.rating else None,
                    "title": r.title,
                    "body": r.body,
                    "sentiment": r.sentiment_label,
                    "sentiment_score": r.sentiment_score,
                    "verified_purchase": r.is_verified_purchase,
                    "is_suspicious": r.is_suspicious,
                    "fraud_score": r.fraud_score,
                })
    except Exception:
        pass

    # Fallback to in-memory product reviews if DB is unavailable or has no reviews
    if not reviews_list:
        fallback = get_fallback_product(id)
        if fallback:
            for idx, r in enumerate(fallback.get("reviews", [])):
                rev = dict(r)
                rev["product_id"] = id
                if "id" not in rev:
                    rev["id"] = f"REV-{id}-{idx+1}"
                reviews_list.append(rev)

    if not reviews_list:
        fallback = get_fallback_product(id)
        if not fallback:
            raise HTTPException(status_code=404, detail=f"Product with id '{id}' not found")

    return {
        "status": "success",
        "product_id": id,
        "count": len(reviews_list),
        "reviews": reviews_list,
    }


@router.get("/{id}/evidence")
async def get_product_evidence(id: str):
    """Retrieve traceable evidence documents and technical claims for product."""
    try:
        product_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    db = get_db_service()
    async with db.session() as session:
        stmt = select(Document).where(Document.product_id == product_uuid)
        result = await session.execute(stmt)
        docs = result.scalars().all()

        return {
            "status": "success",
            "product_id": id,
            "count": len(docs),
            "evidence_documents": [
                {
                    "id": str(d.id),
                    "title": d.title,
                    "doc_type": d.doc_type,
                    "storage_path": d.storage_path,
                    "source_url": d.source_url,
                    "parsed_content": d.parsed_content,
                }
                for d in docs
            ],
        }
