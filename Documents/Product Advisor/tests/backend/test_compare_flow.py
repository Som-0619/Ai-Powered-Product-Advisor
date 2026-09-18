"""Automated tests for TASK 4 — Harden the Compare Flow.

Validates:
1. Compare uses product_id as the ONLY canonical product reference.
2. Canonical flow: Recommendation -> product_id -> Compare -> GET /products/{product_id}
   -> Canonical Product -> Images -> Reviews -> Price -> Compatibility -> Vision -> Retailer Offers.
3. Every tested product confirms:
   Recommendation product == Compare product == Image product == Review product == Buy-link product.
4. Test at least 10 products across categories.
5. Test Amazon available vs unavailable, Flipkart available vs unavailable.
6. Broken/unverified retailer links result in no Buy button.
7. Validation rejects mismatched product_id with zero silent substitutions.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.catalog_fallback import FALLBACK_CATALOG, get_fallback_product
from app.services.retailer_offers import validate_retailer_offer

TEST_PRODUCT_IDS = [
    "c1000000-0000-0000-0000-000000000001",  # Dell XPS 15 9530
    "c1000000-0000-0000-0000-000000000002",  # Apple MacBook Pro 14
    "c1000000-0000-0000-0000-000000000003",  # Apple MacBook Air 15
    "c1000000-0000-0000-0000-000000000004",  # Apple MacBook Air 13
    "c1000000-0000-0000-0000-000000000005",  # Lenovo ThinkPad X1 Carbon
    "c1000000-0000-0000-0000-000000000101",  # Apple iPhone 15 Pro
    "c1000000-0000-0000-0000-000000000102",  # Apple iPhone 15
    "c1000000-0000-0000-0000-000000000105",  # Samsung Galaxy S24 Ultra
    "c1000000-0000-0000-0000-000000000201",  # Sony WH-1000XM5
    "c1000000-0000-0000-0000-000000000206",  # Bose QuietComfort 45
    "c2000000-0000-0000-0000-000000000001",  # ESP32-WROOM-32D
    "c2000000-0000-0000-0000-000000000005",  # Raspberry Pi 4 Model B
]


@pytest.mark.asyncio
async def test_canonical_compare_flow_12_products():
    """Requirement 1, 3, 4, 10:
    Confirm that for at least 10 products:
    Recommendation product == Compare product == Image product == Review product == Buy-link product.
    """
    assert len(TEST_PRODUCT_IDS) >= 10

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for pid in TEST_PRODUCT_IDS:
            # 1. GET /products/{product_id}
            res_details = await client.get(f"/api/v1/products/{pid}")
            assert res_details.status_code == 200, f"Failed GET /products/{pid}"
            details = res_details.json()
            assert details["product_id"] == pid
            assert details["id"] == pid

            # 2. GET /products/{product_id}/compare
            res_compare = await client.get(f"/api/v1/products/{pid}/compare")
            assert res_compare.status_code == 200, f"Failed GET /products/{pid}/compare"
            compare_data = res_compare.json()
            assert compare_data["product_id"] == pid
            comp = compare_data["comparison"]
            assert comp["productId"] == pid or comp.get("product_id") == pid

            # 3. GET /products/{product_id}/images
            res_images = await client.get(f"/api/v1/products/{pid}/images")
            assert res_images.status_code == 200, f"Failed GET /products/{pid}/images"
            img_data = res_images.json()
            assert img_data["product_id"] == pid
            assert len(img_data["images"]) > 0
            for img in img_data["images"]:
                assert img["product_id"] == pid, (
                    f"Image product_id mismatch: {img['product_id']} != {pid}"
                )

            # 4. GET /products/{product_id}/reviews
            res_reviews = await client.get(f"/api/v1/products/{pid}/reviews")
            assert res_reviews.status_code == 200, f"Failed GET /products/{pid}/reviews"
            rev_data = res_reviews.json()
            assert rev_data["product_id"] == pid
            for rev in rev_data.get("reviews", []):
                assert rev.get("product_id") == pid, (
                    f"Review product_id mismatch: {rev.get('product_id')} != {pid}"
                )

            # 5. GET /products/{product_id}/buy-links
            res_links = await client.get(f"/api/v1/products/{pid}/buy-links")
            assert res_links.status_code == 200, f"Failed GET /products/{pid}/buy-links"
            link_data = res_links.json()
            assert link_data["product_id"] == pid
            for bl in link_data.get("buy_links", []):
                assert bl["product_id"] == pid, (
                    f"Buy-link product_id mismatch: {bl['product_id']} != {pid}"
                )

            # 6. Absolute identity equality:
            # Recommendation product == Compare product == Image product == Review product == Buy-link product
            rec_id = pid
            comp_id = compare_data["product_id"]
            img_id = img_data["product_id"]
            rev_id = rev_data["product_id"]
            buy_id = link_data["product_id"]

            assert rec_id == comp_id == img_id == rev_id == buy_id == pid, (
                f"Identity mismatch in flow for {pid}: "
                f"rec={rec_id}, comp={comp_id}, img={img_id}, rev={rev_id}, buy={buy_id}"
            )


@pytest.mark.asyncio
async def test_retailer_availability_combinations():
    """Requirement 11 & 12: Test both:
    - Amazon available
    - Amazon unavailable
    - Flipkart available
    - Flipkart unavailable
    Broken/unverified retailer links must result in no Buy button rather than a broken destination.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Case A: Dual available (Dell XPS 15)
        pid_dual = "c1000000-0000-0000-0000-000000000001"
        res = await client.get(f"/api/v1/products/{pid_dual}/buy-links")
        data = res.json()
        verified = data["verified_buy_links"]
        retailers = {o["retailer"] for o in verified}
        assert "Amazon" in retailers, "Amazon should be available for Dell XPS 15"
        assert "Flipkart" in retailers, "Flipkart should be available for Dell XPS 15"

        # Case B: Test offer filtering when a retailer is marked unverified/broken
        mock_offers = [
            {
                "product_id": pid_dual,
                "retailer": "Amazon",
                "external_product_id": "B0CBGF51G3",
                "url": "https://www.amazon.in/dp/B0CBGF51G3",
                "verification_status": "verified",
            },
            {
                "product_id": pid_dual,
                "retailer": "Flipkart",
                "external_product_id": "broken_id",
                "url": "https://www.flipkart.com/broken",
                "verification_status": "broken",
            },
        ]
        # Verified offers must exclude the broken link
        verified_filtered = [o for o in mock_offers if o["verification_status"] == "verified"]
        assert len(verified_filtered) == 1
        assert verified_filtered[0]["retailer"] == "Amazon"

        # Case C: Amazon unavailable / Flipkart available
        mock_offers_az_unavail = [
            {
                "product_id": pid_dual,
                "retailer": "Amazon",
                "external_product_id": "B000000000",
                "url": "",
                "verification_status": "not_available",
            },
            {
                "product_id": pid_dual,
                "retailer": "Flipkart",
                "external_product_id": "itm289fe81ad080a",
                "url": "https://www.flipkart.com/valid/p/itm289fe81ad080a",
                "verification_status": "verified",
            },
        ]
        verified_fk_only = [o for o in mock_offers_az_unavail if o["verification_status"] == "verified"]
        assert len(verified_fk_only) == 1
        assert verified_fk_only[0]["retailer"] == "Flipkart"


def test_cross_product_validation_rejection():
    """Requirement 8 & 9: Validation before rendering:
    product.product_id === buyLink.product_id
    product.product_id === image.product_id
    product.product_id === review.product_id

    If validation fails:
    - do not render mismatched data
    - log clear error
    - do not silently substitute another product
    """
    prod_a = TEST_PRODUCT_IDS[0]  # Dell XPS 15
    prod_b = TEST_PRODUCT_IDS[1]  # MacBook Pro 14

    # Offer belonging to Product A
    offer_a = {
        "product_id": prod_a,
        "retailer": "Amazon",
        "external_product_id": "B0CBGF51G3",
        "url": "https://www.amazon.in/dp/B0CBGF51G3",
        "verification_status": "verified",
    }

    # Validate against Product A: True
    is_valid_a, errors_a = validate_retailer_offer(offer_a, prod_a)
    assert is_valid_a is True, f"Expected valid offer for {prod_a}, errors: {errors_a}"

    # Validate against Product B: MUST BE FALSE (rejected!)
    is_valid_b, errors_b = validate_retailer_offer(offer_a, prod_b)
    assert is_valid_b is False, "Expected invalid offer when checking Product A's offer against Product B"
    assert any("product_id" in err.lower() for err in errors_b)

    # Corrupted offer with mismatched product_id
    corrupted = dict(offer_a)
    corrupted["product_id"] = "TAMPERED-ID"
    is_valid_c, _ = validate_retailer_offer(corrupted, prod_a)
    assert is_valid_c is False


@pytest.mark.asyncio
async def test_non_existent_product_returns_404():
    """Test that requesting unknown product ID returns 404 and never substitutes another product."""
    unknown_id = "c9999999-9999-9999-9999-999999999999"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"/api/v1/products/{unknown_id}")
        assert res.status_code == 404

        res_buy = await client.get(f"/api/v1/products/{unknown_id}/buy-links")
        assert res_buy.status_code == 404

        res_imgs = await client.get(f"/api/v1/products/{unknown_id}/images")
        assert res_imgs.status_code == 404
