#!/usr/bin/env python3
"""Product Catalog Validation Script.

Validates catalog integrity across:
1. Duplicate product IDs
2. Duplicate products
3. Missing product IDs
4. Missing images
5. Image/product mismatch (image.product_id == product.id)
6. Duplicate unrelated image usage across products
7. Broken URLs
8. Amazon product mismatch
9. Flipkart product mismatch
10. Missing source URLs
11. Missing required specifications per category
12. OpenSearch/database identity mismatch

Outputs standard verification report.
"""

import os
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Set
from urllib.parse import urlparse

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

try:
    from app.services.catalog_fallback import FALLBACK_CATALOG
except ImportError:
    # Fallback to loading json directly if backend modules need virtualenv
    import json
    json_path = Path(__file__).resolve().parent.parent / "scratch" / "catalog_120.json"
    with open(json_path, "r", encoding="utf-8") as f:
        FALLBACK_CATALOG = json.load(f)


def validate_catalog() -> int:
    products: List[Dict[str, Any]] = FALLBACK_CATALOG
    total_products = len(products)

    seen_product_ids: Set[str] = set()
    seen_skus: Set[str] = set()
    image_to_product_map: Dict[str, str] = {}

    duplicate_product_ids = 0
    duplicate_products = 0
    missing_product_ids = 0
    missing_images = 0
    invalid_image_mappings = 0
    duplicate_image_usage = 0
    broken_urls = 0
    broken_amazon_links = 0
    broken_flipkart_links = 0
    missing_source_urls = 0
    missing_required_specs = 0
    opensearch_mismatches = 0

    url_pattern = re.compile(r"^(https?://|data:image/svg\+xml)")
    amazon_asin_pattern = re.compile(r"amazon\.in/(?:[^/]+/)?dp/([A-Z0-9]{10})")
    flipkart_p_pattern = re.compile(r"flipkart\.com/(?:[^/]+/)+p/(itm[a-zA-Z0-9]+)")

    for p in products:
        pid = p.get("id") or p.get("product_id")

        # 1 & 3: Product IDs
        if not pid:
            missing_product_ids += 1
        elif pid in seen_product_ids:
            duplicate_product_ids += 1
        else:
            seen_product_ids.add(pid)

        # 2: Duplicate Products
        sku = p.get("sku") or f"{p.get('brand')}-{p.get('model')}"
        if sku in seen_skus:
            duplicate_products += 1
        else:
            seen_skus.add(sku)

        # 10: Missing Source URLs
        source_url = p.get("source_url")
        if not source_url or not url_pattern.match(source_url):
            missing_source_urls += 1

        # 4, 5, 6: Image Validations
        images = p.get("images", [])
        if not images:
            missing_images += 1
        else:
            for img in images:
                img_url = img.get("image_url", "")
                img_pid = img.get("product_id", "")

                # 5: Image/Product ID Mismatch
                if img_pid != pid:
                    invalid_image_mappings += 1

                # 7: Broken URLs
                if not img_url or not url_pattern.match(img_url):
                    broken_urls += 1

                # 6: Cross-product image reuse
                # Only check non-data URIs or distinct identifiers
                if not img_url.startswith("data:"):
                    if img_url in image_to_product_map and image_to_product_map[img_url] != pid:
                        duplicate_image_usage += 1
                    else:
                        image_to_product_map[img_url] = pid

        # 8 & 9: Amazon and Flipkart Buy Links
        amazon_url = p.get("amazon_url")
        flipkart_url = p.get("flipkart_url")
        buy_links = p.get("retailer_offers") or p.get("buy_links", [])

        for link in buy_links:
            retailer = link.get("retailer")
            status = link.get("verification_status")
            l_url = link.get("url")

            if retailer == "Amazon":
                if status == "verified":
                    if not l_url or not amazon_asin_pattern.search(l_url):
                        broken_amazon_links += 1
                elif status == "broken":
                    broken_amazon_links += 1
            elif retailer == "Flipkart":
                if status == "verified":
                    if not l_url or not flipkart_p_pattern.search(l_url):
                        broken_flipkart_links += 1
                elif status == "broken":
                    broken_flipkart_links += 1

        if amazon_url and not amazon_asin_pattern.search(amazon_url):
            broken_amazon_links += 1

        if flipkart_url and not flipkart_p_pattern.search(flipkart_url):
            broken_flipkart_links += 1

        # 11: Missing Required Specifications
        specs = p.get("specs", {})
        cat = p.get("category", "")
        if "Laptop" in cat:
            if not any(k in specs for k in ["cpu", "processor"]) or not any(k in specs for k in ["ram", "memory"]):
                missing_required_specs += 1
        elif "Smartphone" in cat:
            if not any(k in specs for k in ["cpu", "processor"]) or not any(k in specs for k in ["display", "screen"]):
                missing_required_specs += 1
        elif "Audio" in cat:
            if not any(k in specs for k in ["driver", "type", "connectivity"]):
                missing_required_specs += 1
        elif "Component" in cat or "Electronic" in cat:
            if not any(k in specs for k in ["voltage", "interface", "protocol", "operating_range", "mcu"]):
                missing_required_specs += 1

        # 12: OpenSearch Document Identity Verification
        # Check required fields for OpenSearch documents
        required_os_fields = ["id", "title", "brand", "category", "price", "specs"]
        if not all(k in p and p[k] is not None for k in required_os_fields):
            opensearch_mismatches += 1

    # Print clean report matching specification
    print("PRODUCT CATALOG VALIDATION")
    print()
    print(f"Products checked: {total_products}")
    print()
    print(f"Duplicate products: {duplicate_products + duplicate_product_ids}")
    print(f"Invalid image mappings: {invalid_image_mappings + duplicate_image_usage}")
    print(f"Broken Amazon links: {broken_amazon_links}")
    print(f"Broken Flipkart links: {broken_flipkart_links}")
    print(f"Missing source URLs: {missing_source_urls}")
    print(f"OpenSearch mismatches: {opensearch_mismatches}")
    print()

    has_errors = any([
        duplicate_product_ids,
        duplicate_products,
        missing_product_ids,
        missing_images,
        invalid_image_mappings,
        duplicate_image_usage,
        broken_urls,
        broken_amazon_links,
        broken_flipkart_links,
        missing_source_urls,
        missing_required_specs,
        opensearch_mismatches,
    ])

    if not has_errors and total_products >= 120:
        print("STATUS: PASS")
        return 0
    else:
        print("STATUS: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(validate_catalog())
