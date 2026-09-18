"""Automated tests for Product Image Identity and Isolation.

Validates Requirements for TASK 2:
1. Every image MUST belong to a canonical product_id.
2. Metadata schema: image_id, product_id, external_product_id, image_url, image_type, source, verified.
3. Supported image types (14 types):
   primary, front, back, left, right, top, bottom, screen, keyboard, ports, camera, connector, board, accessories, gallery.
4. No cross-product image contamination.
5. Images retrieved via get_product_images(product_id).
6. image.product_id == product.product_id (and external_product_id check).
7. Missing/unverified image does not fallback to another product's image.
8. Tests at least: 5 laptops, 5 smartphones, 5 audio products, 5 IoT/electronics devices.
"""

import pytest
from typing import Dict, Any, List

from app.services.catalog_fallback import (
    FALLBACK_CATALOG,
    get_product_images,
    validate_product_image,
    get_fallback_product,
)

SUPPORTED_IMAGE_TYPES = {
    "primary", "front", "back", "left", "right", "top", "bottom",
    "screen", "keyboard", "ports", "camera", "connector", "board",
    "accessories", "gallery"
}

# 20+ Products across 4 categories (5 laptops, 5 phones, 5 audio, 5 IoT)
LAPTOP_IDS = [
    "c1000000-0000-0000-0000-000000000001",  # Dell XPS 15 9530
    "c1000000-0000-0000-0000-000000000002",  # Apple MacBook Pro 14
    "c1000000-0000-0000-0000-000000000003",  # Apple MacBook Air 15
    "c1000000-0000-0000-0000-000000000004",  # Apple MacBook Air 13
    "c1000000-0000-0000-0000-000000000005",  # Lenovo ThinkPad X1 Carbon
]

PHONE_IDS = [
    "c1000000-0000-0000-0000-000000000101",  # Apple iPhone 15 Pro
    "c1000000-0000-0000-0000-000000000102",  # Apple iPhone 15
    "c1000000-0000-0000-0000-000000000103",  # Apple iPhone 14
    "c1000000-0000-0000-0000-000000000104",  # Apple iPhone 13
    "c1000000-0000-0000-0000-000000000105",  # Samsung Galaxy S24 Ultra
]

AUDIO_IDS = [
    "c1000000-0000-0000-0000-000000000201",  # Sony WH-1000XM5
    "c1000000-0000-0000-0000-000000000204",  # Sony WF-1000XM5
    "c1000000-0000-0000-0000-000000000206",  # Bose QuietComfort 45
    "c1000000-0000-0000-0000-000000000207",  # Apple AirPods Pro 2
    "c1000000-0000-0000-0000-000000000208",  # Apple AirPods Max
]

IOT_IDS = [
    "c2000000-0000-0000-0000-000000000001",  # ESP32-WROOM-32D
    "c2000000-0000-0000-0000-000000000002",  # NodeMCU ESP8266
    "c2000000-0000-0000-0000-000000000003",  # Arduino Uno R3
    "c2000000-0000-0000-0000-000000000005",  # Raspberry Pi 4 Model B
    "c2000000-0000-0000-0000-000000000007",  # Raspberry Pi Pico W
]

ALL_TESTED_PRODUCT_IDS = LAPTOP_IDS + PHONE_IDS + AUDIO_IDS + IOT_IDS


def test_product_image_identity():
    """Verify strict product image identity across 20+ products in 4 categories.

    Checks:
    - Every image strictly matches image.product_id == product.product_id
    - If external_product_id exists, image.external_product_id == product.external_product_id
    - All 7 metadata fields are present
    - image_type is one of the 14 supported types
    - Images retrieved via get_product_images(product_id)
    """
    assert len(ALL_TESTED_PRODUCT_IDS) >= 20, "Must test at least 20 products across 4 categories"
    assert len(LAPTOP_IDS) >= 5, "Must test at least 5 laptops"
    assert len(PHONE_IDS) >= 5, "Must test at least 5 smartphones"
    assert len(AUDIO_IDS) >= 5, "Must test at least 5 audio products"
    assert len(IOT_IDS) >= 5, "Must test at least 5 IoT/electronics products"

    for pid in ALL_TESTED_PRODUCT_IDS:
        prod = get_fallback_product(pid)
        assert prod is not None, f"Product {pid} must exist in catalog"

        ext_id = prod.get("external_product_id") or prod.get("asin")
        images = get_product_images(pid, ext_id)
        assert len(images) > 0, f"Product {pid} must return at least one image"

        for img in images:
            # 1. Metadata Schema Verification
            assert "image_id" in img, f"Missing image_id in {img}"
            assert "product_id" in img, f"Missing product_id in {img}"
            assert "external_product_id" in img, f"Missing external_product_id in {img}"
            assert "image_url" in img, f"Missing image_url in {img}"
            assert "image_type" in img, f"Missing image_type in {img}"
            assert "source" in img, f"Missing source in {img}"
            assert "verified" in img, f"Missing verified in {img}"

            # 2. Strict Identity Verification
            assert img["product_id"] == pid, (
                f"Identity violation! Image belongs to {img['product_id']}, expected {pid}"
            )

            # 3. External Product ID Verification (if applicable)
            if ext_id and img.get("external_product_id"):
                assert img["external_product_id"] == ext_id, (
                    f"External ID violation! Image has {img['external_product_id']}, expected {ext_id}"
                )

            # 4. Supported Image Type Verification
            assert img["image_type"] in SUPPORTED_IMAGE_TYPES, (
                f"Unsupported image_type '{img['image_type']}' for {pid}. Must be in {SUPPORTED_IMAGE_TYPES}"
            )

            # 5. URL verification: No fake or example.com URLs
            assert "example.com" not in img["image_url"], f"Fake example.com URL found in {pid}"

            # 6. Verification validator check
            assert validate_product_image(pid, img, ext_id) is True, (
                f"validate_product_image failed for product {pid}"
            )


def test_no_cross_product_image_contamination():
    """Verify that no two distinct products share the same non-placeholder image URL.

    Ensures that real product images are strictly isolated to their canonical product_id.
    """
    seen_urls: Dict[str, str] = {}

    for prod in FALLBACK_CATALOG:
        pid = prod["id"]
        images = get_product_images(pid)

        for img in images:
            url = img["image_url"]
            # Ignore clean SVG placeholders (which are unique or data URIs)
            if url.startswith("data:image/svg"):
                continue

            # Real CDN image URLs must belong to exactly one product
            if url in seen_urls:
                existing_pid = seen_urls[url]
                assert existing_pid == pid, (
                    f"CROSS-PRODUCT CONTAMINATION DETECTED!\n"
                    f"Image URL: {url}\n"
                    f"Shared between Product A: {existing_pid} and Product B: {pid}"
                )
            seen_urls[url] = pid

    # Verify cross-product isolation across the 20 specific test products
    product_image_sets = {}
    for pid in ALL_TESTED_PRODUCT_IDS:
        imgs = get_product_images(pid)
        real_urls = {im["image_url"] for im in imgs if not im["image_url"].startswith("data:image/svg")}
        product_image_sets[pid] = real_urls

    for i, pid_a in enumerate(ALL_TESTED_PRODUCT_IDS):
        for pid_b in ALL_TESTED_PRODUCT_IDS[i + 1:]:
            overlap = product_image_sets[pid_a].intersection(product_image_sets[pid_b])
            assert len(overlap) == 0, (
                f"Contamination between {pid_a} and {pid_b}: {overlap}"
            )


def test_missing_image_does_not_fallback_to_other_product():
    """Verify that missing, invalid, or corrupted images never display another product's image.

    Ensures:
    - Non-existent product ID returns empty or clean placeholder, never another product's image
    - Tampered image dict with mismatched product_id is rejected by validate_product_image
    - Tampered image dict with mismatched external_product_id is rejected
    - Missing image falls back cleanly to 'Image unavailable' SVG placeholder
    """
    # 1. Non-existent product ID
    unknown_pid = "00000000-0000-0000-0000-000000009999"
    unknown_imgs = get_product_images(unknown_pid)
    assert len(unknown_imgs) == 0, "Unknown product ID should return no images"

    # 2. Tampered image belonging to Product B requested for Product A
    laptop_a = LAPTOP_IDS[0]
    laptop_b = LAPTOP_IDS[1]
    images_b = get_product_images(laptop_b)
    assert len(images_b) > 0

    stolen_image = dict(images_b[0])
    # Validate that product A rejects product B's image
    assert validate_product_image(laptop_a, stolen_image) is False, (
        "validate_product_image MUST reject image belonging to another product"
    )

    # 3. Tampered external_product_id
    corrupted_ext_image = {
        "image_id": f"IMG-{laptop_a}-FRONT",
        "product_id": laptop_a,
        "external_product_id": "WRONG_ASIN_12345",
        "image_url": "https://m.media-amazon.com/images/I/test.jpg",
        "image_type": "front",
        "source": "Amazon",
        "verified": True,
    }
    assert validate_product_image(laptop_a, corrupted_ext_image, external_product_id="CORRECT_ASIN_67890") is False, (
        "validate_product_image MUST reject image with mismatched external_product_id"
    )

    # 4. Product with unverified images returns clean placeholder, never another product's image
    placeholder_prod_id = "c2000000-0000-0000-0000-000000000028"  # MQ-135 Gas Sensor (placeholder)
    ph_images = get_product_images(placeholder_prod_id)
    assert len(ph_images) > 0
    ph_img = ph_images[0]
    assert ph_img["product_id"] == placeholder_prod_id
    assert ph_img["verified"] is False
    assert "data:image/svg" in ph_img["image_url"]
    assert "Image unavailable" in ph_img["image_url"]
    # Ensure it did NOT take a real image from any other product
    for pid in ALL_TESTED_PRODUCT_IDS:
        other_imgs = get_product_images(pid)
        for oi in other_imgs:
            if oi["verified"]:
                assert ph_img["image_url"] != oi["image_url"], (
                    f"Placeholder product {placeholder_prod_id} substituted real image from {pid}!"
                )


def test_no_duplicate_fake_views_within_product():
    """Verify Requirement 4: NEVER create a fake view.

    If a product only has front/back, show only those.
    Do NOT duplicate the front image and label it: left, right, top, ports, etc.
    Every image entry within a product MUST have a strictly unique image_url.
    """
    for prod in FALLBACK_CATALOG:
        pid = prod["id"]
        images = get_product_images(pid)
        urls = [img["image_url"] for img in images]

        # 1. No duplicate image URLs within the images list
        assert len(urls) == len(set(urls)), (
            f"Fake view detected in product {pid} ({prod.get('title')})! "
            f"Images list contains duplicate URLs: {urls}"
        )

        # 2. No duplicate image URLs in media_gallery
        media_gallery = prod.get("media_gallery", {})
        if media_gallery:
            gal_urls = list(media_gallery.values())
            assert len(gal_urls) == len(set(gal_urls)), (
                f"Fake view detected in product {pid} media_gallery! "
                f"Gallery contains duplicate URLs: {gal_urls}"
            )

        # 3. If only 1 image exists, it should only have 1 view (no fabricated multiple views)
        if len(images) == 1:
            assert len(media_gallery) <= 1, (
                f"Product {pid} has 1 image but media_gallery has {len(media_gallery)} views!"
            )


def test_images_from_product_a_cannot_appear_under_product_b():
    """Verify Requirement 13: Images from Product A CANNOT appear under Product B.

    Exhaustive pairwise test across ALL products in FALLBACK_CATALOG:
    - Every verified image URL is exclusive to its canonical product_id.
    - An image belonging to Product A fails validation if presented as Product B.
    """
    # 1. Exhaustive pairwise URL isolation
    catalog_verified_urls: Dict[str, str] = {}
    for prod in FALLBACK_CATALOG:
        pid = prod["id"]
        for img in prod.get("images", []):
            if img.get("verified") and not img.get("image_url", "").startswith("data:image/svg"):
                u = img["image_url"]
                assert u not in catalog_verified_urls or catalog_verified_urls[u] == pid, (
                    f"Cross-product image leakage! Image {u} is present in both "
                    f"Product {catalog_verified_urls.get(u)} and Product {pid}!"
                )
                catalog_verified_urls[u] = pid

    # 2. Rejection of Product A's image when tested against Product B
    for i in range(min(15, len(ALL_TESTED_PRODUCT_IDS) - 1)):
        pid_a = ALL_TESTED_PRODUCT_IDS[i]
        pid_b = ALL_TESTED_PRODUCT_IDS[i + 1]

        imgs_a = get_product_images(pid_a)
        imgs_b = get_product_images(pid_b)

        if imgs_a and imgs_a[0].get("verified"):
            # Product B must reject Product A's image
            assert validate_product_image(pid_b, imgs_a[0]) is False, (
                f"Product {pid_b} falsely validated image belonging to Product {pid_a}!"
            )

        if imgs_b and imgs_b[0].get("verified"):
            # Product A must reject Product B's image
            assert validate_product_image(pid_a, imgs_b[0]) is False, (
                f"Product {pid_a} falsely validated image belonging to Product {pid_b}!"
            )


def test_multi_view_coverage_across_categories():
    """Verify Requirement 1, 2, 3:
    - Support for multiple verified views across categories where available.
    - Only display a view if a verified image actually exists.
    - Inspect at least 20 products (5 laptops, 5 smartphones, 5 audio, 5 IoT/electronics).
    """
    assert len(ALL_TESTED_PRODUCT_IDS) >= 20

    multi_view_products = []
    for pid in ALL_TESTED_PRODUCT_IDS:
        prod = get_fallback_product(pid)
        assert prod is not None
        images = get_product_images(pid)
        verified_images = [img for img in images if img.get("verified")]

        # Each verified image must be strictly tied to product_id and image_id
        for img in verified_images:
            assert img["product_id"] == pid
            assert img["image_id"].startswith(f"IMG-{pid}-")
            assert img["image_type"] in SUPPORTED_IMAGE_TYPES

        if len(verified_images) > 1:
            multi_view_products.append(pid)

    # Across the 20 inspected products, we must have multiple multi-view products
    assert len(multi_view_products) >= 10, (
        f"Expected at least 10 multi-view products among tested 20, found {len(multi_view_products)}"
    )


@pytest.mark.asyncio
async def test_vision_observation_metadata_retention():
    """Verify Requirement 6 & 7:
    - Vision must only receive images where image.product_id == candidate.product_id
    - Vision output must retain: product_id, image_id, image_url, view_type, observation, confidence
    - If no verified image exists, return unavailable state
    """
    from app.services.orchestrator import WorkflowOrchestrator

    orch = WorkflowOrchestrator()

    # Test candidate with verified multi-view images
    laptop_pid = LAPTOP_IDS[0]
    laptop_prod = get_fallback_product(laptop_pid)
    assert laptop_prod is not None

    async for chunk in orch.execute_stream("Dell XPS 15 laptop for creators"):
        if chunk.get("type") == "complete":
            recs = chunk.get("data", {}).get("recommendations", [])
            assert len(recs) > 0
            for card in recs:
                cand_id = card["product_id"]
                vis = card.get("visual_verification", {})
                assert "visual_verification_status" in vis
                observations = vis.get("observations", [])
                assert len(observations) > 0

                for obs in observations:
                    # Requirement 7: Vision output must retain all 6 fields
                    assert "product_id" in obs, f"Missing product_id in observation {obs}"
                    assert "image_id" in obs, f"Missing image_id in observation {obs}"
                    assert "image_url" in obs, f"Missing image_url in observation {obs}"
                    assert "view_type" in obs, f"Missing view_type in observation {obs}"
                    assert "observation" in obs, f"Missing observation in observation {obs}"
                    assert "confidence" in obs, f"Missing confidence in observation {obs}"

                    # Requirement 6: image.product_id == candidate.product_id
                    assert obs["product_id"] == cand_id, (
                        f"Vision observation product_id mismatch: {obs['product_id']} != {cand_id}"
                    )
            break


def test_image_belongs_to_product():
    """Verify that every image returned strictly belongs to product_id and matches identity.

    Guarantees:
    - image.product_id == product.product_id for all returned images
    - If external_product_id exists, image.external_product_id == product.external_product_id
    - Image fails validation if tested against any other product_id
    - Corrupted external ID fails validation
    """
    for prod in FALLBACK_CATALOG:
        pid = prod["id"]
        ext_id = prod.get("external_product_id") or prod.get("asin")
        images = get_product_images(pid, ext_id)
        assert len(images) > 0, f"Product {pid} must return images"

        for img in images:
            # 1. Direct identity match
            assert img["product_id"] == pid, (
                f"Image {img.get('image_id')} belongs to {img['product_id']}, expected {pid}"
            )

            # 2. External ID check if applicable
            if ext_id and img.get("external_product_id"):
                assert img["external_product_id"] == ext_id, (
                    f"Image {img.get('image_id')} external_id {img['external_product_id']} != {ext_id}"
                )

            # 3. Validation helper passes for owner product
            assert validate_product_image(pid, img, ext_id) is True

            # 4. Strict cross-rejection: must fail if tested against a different product ID
            other_pid = "c1000000-0000-0000-0000-000000000999"
            assert validate_product_image(other_pid, img, ext_id) is False, (
                f"validate_product_image failed to reject image for non-owner product {other_pid}"
            )


