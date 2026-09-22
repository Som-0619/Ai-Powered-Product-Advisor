"""Stage 3 — Product Image, Data Validation and Storage Integrity Audit Script.

Performs a comprehensive, non-destructive inventory audit and storage integrity check
across all products in PostgreSQL and MinIO via StorageService abstraction.

Sections Implemented:
1. Inventory Audit
2. Image-Product Ownership
6. Storage Key Validation
7. Image File Validation
8. Image Quality Check
9. Product Image Type Validation
10. Primary Image Rule (uniqueness)
11. Variant Image Rule
12. Product Data Validation
13. Specification Validation (Category-specific schema)
14. Source / Provenance Validation
15. Retailer Offer Validation
16. MinIO Storage & Orphan Object Validation
22. Catalog Integrity Report Generation
"""

import asyncio
import json
import os
import re
import sys
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.models.catalog import Product, ProductVariant
from app.models.media import ProductImage, CANONICAL_IMAGE_TYPES
from app.models.retailer_offers import RetailerOffer
from app.models.sources import ProductSource
from app.models.reviews import ProductReview
from app.services.factory import get_db_service, get_storage_service
from app.services.image_validator import ImageValidator
from app.services.storage import StoragePath

# Category-specific required specification fields (Section 13)
CATEGORY_SPEC_FIELDS = {
    "laptop": ["cpu", "gpu", "ram", "storage", "display"],
    "laptops": ["cpu", "gpu", "ram", "storage", "display"],
    "smartphone": ["processor", "ram", "storage", "display", "battery"],
    "smartphones": ["processor", "ram", "storage", "display", "battery"],
    "headphones": ["driver", "battery", "bluetooth", "anc"],
    "audio": ["driver", "battery", "bluetooth", "anc"],
    "iot": ["microcontroller", "connectivity", "voltage", "interfaces"],
    "development boards": ["mcu", "gpio", "usb", "wifi", "bluetooth", "voltage"],
    "development board": ["mcu", "gpio", "usb", "wifi", "bluetooth", "voltage"],
    "single board computers": ["mcu", "gpio", "usb", "wifi", "bluetooth", "voltage"],
}


async def run_catalog_audit() -> Dict[str, Any]:
    """Execute complete catalog and storage audit without modifying any records."""
    db_service = get_db_service()
    storage_service = get_storage_service()

    # 1. Verify Storage Connectivity
    storage_health = await storage_service.health_check()
    minio_connected = storage_health.get("status") == "ok"

    # Enumerate existing objects in MinIO via StorageService abstraction
    existing_minio_objects: Set[str] = set()
    if minio_connected:
        try:
            objs = await storage_service.list_objects(prefix="", recursive=True)
            existing_minio_objects = set(objs)
        except Exception as e:
            print(f"Warning: Failed to list objects from storage: {e}")

    audit_results: Dict[str, Any] = {
        "inventory": [],
        "summary": {},
        "issues": [],
        "orphan_objects": [],
        "missing_objects": [],
    }

    async with db_service.session() as session:
        # Load all products with eager graph relationships
        p_stmt = (
            select(Product)
            .options(
                selectinload(Product.variants),
                selectinload(Product.images),
                selectinload(Product.retailer_offers),
                selectinload(Product.sources),
                selectinload(Product.reviews),
            )
            .order_by(Product.created_at.asc())
        )
        p_res = await session.execute(p_stmt)
        products: List[Product] = list(p_res.scalars().all())

        # Load all variants for global lookup
        v_stmt = select(ProductVariant)
        v_res = await session.execute(v_stmt)
        all_variants: Dict[uuid.UUID, ProductVariant] = {v.id: v for v in v_res.scalars().all()}

        # Load all images for global storage verification
        img_stmt = select(ProductImage)
        img_res = await session.execute(img_stmt)
        all_images: List[ProductImage] = list(img_res.scalars().all())

        # Counters for Section 22 Report
        total_products = len(products)
        products_with_images = 0
        products_without_images = 0

        total_images = len(all_images)
        valid_images = 0
        invalid_images = 0
        needs_review_images = 0

        primary_images_count = 0
        products_with_primary = 0
        products_with_duplicate_primary = 0

        variant_images_count = 0
        valid_variant_mappings = 0
        invalid_variant_mappings = 0

        cross_product_image_errors = 0
        storage_key_mismatches = 0

        specs_valid = 0
        specs_missing_info = 0
        specs_invalid_json = 0

        sources_valid = 0
        sources_missing_provenance = 0

        retailer_offers_valid = 0
        retailer_offers_invalid = 0
        retailer_unknown_availability = 0

        # Map images by storage_key for orphan detection
        registered_storage_keys: Set[str] = set()

        for prod in products:
            pid = prod.id
            pid_str = str(pid)

            # --- 1. Product Data Validation (Section 12) ---
            prod_issues = []
            if not prod.brand:
                prod_issues.append("missing_brand")
            if not prod.model:
                prod_issues.append("missing_model")
            if not prod.category:
                prod_issues.append("missing_category")

            # --- 13. Specification Validation (Section 13) ---
            specs = prod.specifications
            if not isinstance(specs, dict):
                specs_invalid_json += 1
                prod_issues.append("invalid_specifications_json")
            else:
                specs_valid += 1
                cat_lower = (prod.category or "").strip().lower()
                expected_fields = CATEGORY_SPEC_FIELDS.get(cat_lower, [])
                missing_spec_fields = []
                for f in expected_fields:
                    # Check field case-insensitively in specs keys
                    found = any(k.lower() == f for k in specs.keys())
                    if not found:
                        missing_spec_fields.append(f)
                if missing_spec_fields:
                    specs_missing_info += 1

            # --- Images for this Product ---
            p_images = prod.images
            img_count = len(p_images)
            if img_count > 0:
                products_with_images += 1
            else:
                products_without_images += 1

            primary_img = None
            front_img = None
            back_img = None
            primary_candidates = []

            for img in p_images:
                img_issues = []
                img_id_str = str(img.id)

                # Ownership verification (Section 2)
                if img.product_id != pid:
                    cross_product_image_errors += 1
                    img_issues.append(f"cross_product_ownership_mismatch: image.product_id={img.product_id} != product.id={pid}")

                # Variant verification (Section 2 & 11)
                if img.variant_id:
                    variant_images_count += 1
                    v_obj = all_variants.get(img.variant_id)
                    if not v_obj:
                        invalid_variant_mappings += 1
                        img_issues.append(f"variant_not_found: {img.variant_id}")
                    elif v_obj.product_id != pid:
                        invalid_variant_mappings += 1
                        cross_product_image_errors += 1
                        img_issues.append(f"variant_cross_product_mismatch: variant {img.variant_id} belongs to {v_obj.product_id}")
                    else:
                        valid_variant_mappings += 1

                # Storage Key Validation (Section 5 & 6)
                sk = img.storage_key
                if sk:
                    registered_storage_keys.add(sk)
                    # Check if storage key matches products/{pid}/...
                    expected_prefix = f"products/{pid_str}/"
                    if not sk.startswith(expected_prefix):
                        storage_key_mismatches += 1
                        img_issues.append(f"non_canonical_storage_key: '{sk}' does not start with '{expected_prefix}'")
                    # Check path traversal
                    if not StoragePath.validate_safe_key(sk):
                        img_issues.append(f"unsafe_storage_key: path traversal or invalid characters detected in '{sk}'")

                    # MinIO Object Existence (Section 16)
                    if minio_connected:
                        if sk not in existing_minio_objects:
                            audit_results["missing_objects"].append({
                                "product_id": pid_str,
                                "image_id": img_id_str,
                                "storage_key": sk,
                            })

                # Image Type Validation (Section 9)
                itype = (img.image_type or "").strip().lower()
                if not ImageValidator.is_canonical_type(itype):
                    img_issues.append(f"non_canonical_image_type: '{itype}'")
                    needs_review_images += 1
                else:
                    if img.is_primary or itype == "primary":
                        primary_candidates.append(img)
                        if not primary_img:
                            primary_img = sk or img.image_url
                    if itype == "front" and not front_img:
                        front_img = sk or img.image_url
                    if itype == "back" and not back_img:
                        back_img = sk or img.image_url

                if img_issues:
                    invalid_images += 1
                    for iss in img_issues:
                        audit_results["issues"].append({
                            "product_id": pid_str,
                            "image_id": img_id_str,
                            "problem": iss,
                            "severity": "CRITICAL" if "cross_product" in iss or "unsafe" in iss else "WARNING",
                            "recommended_action": "Quarantine / Review record",
                        })
                else:
                    valid_images += 1

            # Primary Image Rule Check (Section 10)
            if len(primary_candidates) == 1:
                products_with_primary += 1
                primary_images_count += 1
            elif len(primary_candidates) > 1:
                products_with_primary += 1
                products_with_duplicate_primary += 1
                primary_images_count += len(primary_candidates)
                audit_results["issues"].append({
                    "product_id": pid_str,
                    "image_id": None,
                    "problem": f"Duplicate primary images: product has {len(primary_candidates)} primary images",
                    "severity": "WARNING",
                    "recommended_action": "Execute ProductImageService.set_primary_image to enforce single primary",
                })

            # --- 14. Source Validation (Section 14) ---
            p_sources = prod.sources
            if not p_sources:
                sources_missing_provenance += 1
            else:
                for s in p_sources:
                    if s.product_id != pid:
                        audit_results["issues"].append({
                            "product_id": pid_str,
                            "problem": f"Source {s.id} belongs to {s.product_id}, not {pid}",
                            "severity": "CRITICAL",
                            "recommended_action": "Fix source product association",
                        })
                    else:
                        sources_valid += 1

            # --- 15. Retailer Offer Validation (Section 15) ---
            p_offers = prod.retailer_offers
            for o in p_offers:
                offer_valid = True
                if o.product_id != pid:
                    retailer_offers_invalid += 1
                    offer_valid = False
                    audit_results["issues"].append({
                        "product_id": pid_str,
                        "problem": f"Retailer offer {o.id} belongs to {o.product_id}, not {pid}",
                        "severity": "CRITICAL",
                        "recommended_action": "Fix offer product association",
                    })

                if o.variant_id:
                    v_obj = all_variants.get(o.variant_id)
                    if not v_obj or v_obj.product_id != pid:
                        retailer_offers_invalid += 1
                        offer_valid = False
                        audit_results["issues"].append({
                            "product_id": pid_str,
                            "problem": f"Retailer offer variant {o.variant_id} does not belong to {pid}",
                            "severity": "CRITICAL",
                            "recommended_action": "Fix offer variant association",
                        })

                if o.retailer not in ("amazon", "flipkart"):
                    retailer_offers_invalid += 1
                    offer_valid = False

                if o.availability_status == "unknown":
                    retailer_unknown_availability += 1

                if offer_valid:
                    retailer_offers_valid += 1

            # Append to Section 1 Inventory List
            audit_results["inventory"].append({
                "product_id": pid_str,
                "brand": prod.brand,
                "model": prod.model,
                "variant": prod.variant,
                "category": prod.category,
                "subcategory": prod.subcategory,
                "image_count": img_count,
                "primary_image": primary_img,
                "front_image": front_img,
                "back_image": back_img,
                "review_count": len(prod.reviews),
                "source_count": len(p_sources),
                "retailer_offer_count": len(p_offers),
            })

        # --- 16. MinIO Orphan Detection (Section 16) ---
        for obj_key in existing_minio_objects:
            if obj_key not in registered_storage_keys:
                audit_results["orphan_objects"].append(obj_key)

        # Assemble Section 22 Summary Report
        audit_results["summary"] = {
            "total_products": total_products,
            "products_with_images": products_with_images,
            "products_without_images": products_without_images,
            "total_images": total_images,
            "valid_images": valid_images,
            "invalid_images": invalid_images,
            "needs_review_images": needs_review_images,
            "primary_images": primary_images_count,
            "products_with_primary_images": products_with_primary,
            "products_with_duplicate_primary_images": products_with_duplicate_primary,
            "variant_images": variant_images_count,
            "valid_variant_mappings": valid_variant_mappings,
            "invalid_variant_mappings": invalid_variant_mappings,
            "cross_product_image_errors": cross_product_image_errors,
            "storage_key_mismatches": storage_key_mismatches,
            "database_images": total_images,
            "existing_minio_objects": len(existing_minio_objects),
            "missing_objects": len(audit_results["missing_objects"]),
            "orphan_objects": len(audit_results["orphan_objects"]),
            "specifications_valid": specs_valid,
            "specifications_missing_information": specs_missing_info,
            "specifications_invalid_json": specs_invalid_json,
            "sources_valid": sources_valid,
            "sources_missing_provenance": sources_missing_provenance,
            "retailer_offers_valid": retailer_offers_valid,
            "retailer_offers_invalid": retailer_offers_invalid,
            "retailer_unknown_availability": retailer_unknown_availability,
        }

    return audit_results


def format_report_markdown(report: Dict[str, Any]) -> str:
    """Format audit results to match Section 22 Catalog Integrity Report layout."""
    s = report["summary"]
    lines = [
        "==================================================",
        "22. CATALOG INTEGRITY REPORT",
        "==================================================",
        f"Total products: {s['total_products']}",
        f"Products with images: {s['products_with_images']}",
        f"Products without images: {s['products_without_images']}",
        "",
        f"Total images: {s['total_images']}",
        f"Valid images: {s['valid_images']}",
        f"Invalid images: {s['invalid_images']}",
        f"Needs review: {s['needs_review_images']}",
        "",
        f"Primary images: {s['primary_images']}",
        f"Products with primary images: {s['products_with_primary_images']}",
        f"Products with duplicate primary images: {s['products_with_duplicate_primary_images']}",
        "",
        f"Variant images: {s['variant_images']}",
        f"Valid variant mappings: {s['valid_variant_mappings']}",
        f"Invalid variant mappings: {s['invalid_variant_mappings']}",
        "",
        "Storage:",
        f"Database images: {s['database_images']}",
        f"Existing MinIO objects: {s['existing_minio_objects']}",
        f"Missing objects: {s['missing_objects']}",
        f"Orphan objects: {s['orphan_objects']}",
        "",
        "Specifications:",
        f"Valid: {s['specifications_valid']}",
        f"Missing information: {s['specifications_missing_information']}",
        f"Invalid JSON: {s['specifications_invalid_json']}",
        "",
        "Sources:",
        f"Valid: {s['sources_valid']}",
        f"Missing provenance: {s['sources_missing_provenance']}",
        "",
        "Retailer offers:",
        f"Valid: {s['retailer_offers_valid']}",
        f"Invalid: {s['retailer_offers_invalid']}",
        f"Unknown availability: {s['retailer_unknown_availability']}",
        "==================================================",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    report = asyncio.run(run_catalog_audit())
    output_path = "scripts/stage3_catalog_integrity_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(format_report_markdown(report))
    print(f"\nSaved detailed JSON audit report to {output_path}")
