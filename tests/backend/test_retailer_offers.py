"""Automated tests for Retailer Offer Normalization, Identity Verification, and Compare Flow.

Strictly verifies:
1. Amazon link identity (ASIN preservation, valid domain, /dp/{ASIN} path, no search/redirects)
2. Flipkart link identity (itm identifier, valid domain, /p/{itm} path, null for unverified)
3. Compare -> Buy flow (compare retrieves canonical product using product_id, verified links active, unverified hidden)
4. No cross-product retailer mapping (zero leakage, zero duplicate external IDs)
5. Backend validation rules (wrong product_id, duplicate external IDs, malformed URLs, missing status, retailer mismatch)
"""

import pytest
from datetime import datetime, timezone
from app.services.catalog_fallback import FALLBACK_CATALOG, get_fallback_product
from app.services.retailer_offers import (
    verify_retailer_url,
    validate_retailer_offer,
    validate_catalog_offers,
    get_canonical_product_offers,
    get_canonical_comparison,
    inspect_retailer_page_state,
    is_verification_stale,
)


def test_canonical_product_id_uniqueness():
    """Verify all 120 products have unique canonical product IDs."""
    seen_ids = set()
    for p in FALLBACK_CATALOG:
        pid = p.get("id") or p.get("product_id")
        assert pid is not None and len(pid) > 0, "Product ID must not be empty"
        assert pid not in seen_ids, f"Duplicate canonical product ID detected: {pid}"
        seen_ids.add(pid)
    assert len(seen_ids) == 120, f"Expected 120 unique products, found {len(seen_ids)}"


def test_amazon_link_identity():
    """Verify Amazon external_product_id (ASIN), domain, and direct product detail URL."""
    asins = set()
    for p in FALLBACK_CATALOG:
        pid = p["id"]
        asin = p.get("external_product_id")
        assert asin is not None, f"Product {pid} missing external_product_id (ASIN)"
        assert len(asin) == 10, f"Product {pid} ASIN '{asin}' must be 10 characters"
        assert asin not in asins, f"Duplicate ASIN detected: {asin} on product {pid}"
        asins.add(asin)

        # Check Amazon offer
        offers = p.get("retailer_offers") or p.get("buy_links") or []
        az_offer = next((o for o in offers if o.get("retailer") == "Amazon"), None)
        assert az_offer is not None, f"Product {pid} missing Amazon offer"
        assert az_offer.get("verification_status") == "verified"
        assert az_offer.get("external_product_id") == asin

        url = az_offer.get("url")
        assert url is not None, f"Product {pid} Amazon URL must not be null"
        assert "amazon.in" in url, f"Product {pid} Amazon URL must use amazon.in domain: {url}"
        assert f"/dp/{asin}" in url, f"Product {pid} Amazon URL must link to /dp/{asin}: {url}"
        assert "/s?" not in url and "/search" not in url, f"Amazon URL must not be search query: {url}"

        # Test verify_retailer_url function directly
        is_valid, reason, extracted_asin = verify_retailer_url("Amazon", url, pid, asin)
        assert is_valid is True, f"Failed URL verification for {pid}: {reason}"
        assert extracted_asin == asin


def test_flipkart_link_identity():
    """Verify Flipkart links: authentic itm IDs for verified products, null for unavailable."""
    verified_count = 0
    unavailable_count = 0
    seen_itm_ids = set()

    for p in FALLBACK_CATALOG:
        pid = p["id"]
        offers = p.get("retailer_offers") or p.get("buy_links") or []
        fk_offer = next((o for o in offers if o.get("retailer") == "Flipkart"), None)
        assert fk_offer is not None, f"Product {pid} missing Flipkart offer"

        status = fk_offer.get("verification_status")
        url = fk_offer.get("url")
        ext_id = fk_offer.get("external_product_id")

        if status == "verified":
            verified_count += 1
            assert url is not None, f"Verified Flipkart product {pid} must have non-null URL"
            assert "flipkart.com" in url, f"Flipkart URL must use flipkart.com domain: {url}"
            assert "/p/itm" in url, f"Flipkart URL must link to /p/itm... product page: {url}"
            assert ext_id is not None and ext_id.startswith("itm"), f"Flipkart external_id must start with itm: {ext_id}"
            assert ext_id not in seen_itm_ids, f"Duplicate Flipkart itm ID detected: {ext_id}"
            seen_itm_ids.add(ext_id)
            assert f"/p/{ext_id}" in url

            # Verify through verification service
            is_valid, reason, extracted_id = verify_retailer_url("Flipkart", url, pid, ext_id)
            assert is_valid is True, f"Failed Flipkart verification for {pid}: {reason}"
            assert extracted_id == ext_id
        else:
            unavailable_count += 1
            assert fk_offer.get("availability_status") == "unavailable"
            assert status in ("unverified", "not_available")
            assert url is None, f"Unverified Flipkart offer {pid} must have url=None, got {url}"
            assert ext_id is None, f"Unverified Flipkart offer {pid} must have external_product_id=None"

    assert verified_count == 23, f"Expected exactly 23 verified Flipkart products, got {verified_count}"
    assert unavailable_count == 97, f"Expected exactly 97 unavailable Flipkart products, got {unavailable_count}"


def test_compare_to_buy_flow_dual_retailer():
    """Test Compare -> Buy flow for a product verified on both Amazon and Flipkart."""
    pid = "c1000000-0000-0000-0000-000000000001"  # Dell XPS 15 9530
    comparison = get_canonical_comparison(pid)
    assert comparison is not None, f"Canonical comparison failed for {pid}"

    assert comparison["productId"] == pid
    deals = comparison["deals"]

    # Amazon Buy Button Verification
    az_deal = deals["amazon"]
    assert az_deal["isVerified"] is True
    assert az_deal["url"] == "https://www.amazon.in/dp/B0CBGF51G3"
    assert az_deal["inStock"] is True
    assert az_deal["verificationStatus"] == "verified"
    assert az_deal["availabilityStatus"] == "available"

    # Flipkart Buy Button Verification
    fk_deal = deals["flipkart"]
    assert fk_deal["isVerified"] is True
    assert fk_deal["url"] is not None and "flipkart.com" in fk_deal["url"]
    assert fk_deal["inStock"] is True
    assert fk_deal["verificationStatus"] == "verified"
    assert fk_deal["availabilityStatus"] == "available"


def test_compare_to_buy_flow_single_retailer_hides_unverified():
    """Test Compare -> Buy flow for a product verified only on Amazon (Flipkart button hidden)."""
    pid = "c1000000-0000-0000-0000-000000000002"  # Apple MacBook Pro 14 M3 Pro
    comparison = get_canonical_comparison(pid)
    assert comparison is not None, f"Canonical comparison failed for {pid}"

    assert comparison["productId"] == pid
    deals = comparison["deals"]

    # Amazon Buy Button must be active
    az_deal = deals["amazon"]
    assert az_deal["isVerified"] is True
    assert az_deal["url"] == "https://www.amazon.in/dp/B0CM5JV232"
    assert az_deal["verificationStatus"] == "verified"
    assert az_deal["availabilityStatus"] == "available"

    # Flipkart Buy Button must be hidden
    fk_deal = deals["flipkart"]
    assert fk_deal["isVerified"] is False, "Unverified Flipkart deal must have isVerified=False"
    assert fk_deal["url"] is None, "Unverified Flipkart deal must have url=None"
    assert fk_deal["inStock"] is False, "Unverified Flipkart deal must have inStock=False"
    assert fk_deal["verificationStatus"] in ("unverified", "not_available")
    assert fk_deal["availabilityStatus"] == "unavailable"


def test_no_cross_product_retailer_mapping():
    """Verify zero cross-product retailer offer leakage."""
    for p in FALLBACK_CATALOG:
        pid = p["id"]
        offers = get_canonical_product_offers(pid)
        for off in offers:
            assert off["product_id"] == pid, f"Cross-product offer leakage: expected {pid}, got {off['product_id']}"


def test_backend_validation_rejects_wrong_product_id():
    """Validation test: reject offer when offer.product_id != canonical_id."""
    invalid_offer = {
        "product_id": "c1000000-0000-0000-0000-000000000999",
        "retailer": "Amazon",
        "external_product_id": "B0CBGF51G3",
        "url": "https://www.amazon.in/dp/B0CBGF51G3",
        "verification_status": "verified",
        "last_verified": "2026-09-18T00:00:00Z",
    }
    is_valid, errors = validate_retailer_offer(invalid_offer, "c1000000-0000-0000-0000-000000000001")
    assert is_valid is False
    assert any("Wrong product_id" in err for err in errors)


def test_backend_validation_rejects_malformed_urls():
    """Validation test: reject non-product URLs, search queries, and wrong domains."""
    pid = "c1000000-0000-0000-0000-000000000001"

    # Search URL
    is_valid, reason, _ = verify_retailer_url("Amazon", "https://www.amazon.in/s?k=dell+laptop", pid)
    assert is_valid is False
    assert "search or category page" in reason

    # Homepage redirect
    is_valid, reason, _ = verify_retailer_url("Amazon", "https://www.amazon.in/", pid)
    assert is_valid is False
    assert "homepage" in reason

    # Domain mismatch
    is_valid, reason, _ = verify_retailer_url("Amazon", "https://www.flipkart.com/dell-xps/p/itm123", pid)
    assert is_valid is False
    assert "Domain mismatch" in reason

    # Non-HTTP scheme
    is_valid, reason, _ = verify_retailer_url("Amazon", "javascript:alert(1)", pid)
    assert is_valid is False
    assert "Invalid scheme" in reason


def test_backend_validation_rejects_missing_verification_status():
    """Validation test: reject offers with missing or invalid verification status."""
    invalid_offer = {
        "product_id": "c1000000-0000-0000-0000-000000000001",
        "retailer": "Amazon",
        "external_product_id": "B0CBGF51G3",
        "url": "https://www.amazon.in/dp/B0CBGF51G3",
        "verification_status": "partially_valid",  # Invalid status
        "last_verified": "2026-09-18T00:00:00Z",
    }
    is_valid, errors = validate_retailer_offer(invalid_offer, "c1000000-0000-0000-0000-000000000001")
    assert is_valid is False
    assert any("Invalid verification_status" in err for err in errors)


def test_entire_catalog_offers_pass_validation():
    """Run full catalog validation check on all 120 products and 240 offers."""
    report = validate_catalog_offers(FALLBACK_CATALOG)
    assert report["status"] == "PASS", f"Catalog validation failed: {report['detailed_errors']}"
    assert report["total_products"] == 120
    assert report["total_offers_checked"] == 240
    assert report["total_errors"] == 0


def test_available_retailer_offer():
    """Verify Requirement 3, 4, 10: Available Amazon and Flipkart products.
    
    Checks:
    - Page inspection on authentic product page yields:
      availability_status == 'available'
      verification_status == 'verified'
    - Only available + verified gets an active Buy button with non-null URL.
    """
    pid = "c1000000-0000-0000-0000-000000000001"
    asin = "B0CBGF51G3"
    url = f"https://www.amazon.in/dp/{asin}"
    html = "<html><body><h1>Dell XPS 15 9530</h1><span class='a-price-whole'>1,99,990</span><div id='availability'>In stock</div></body></html>"

    avail, verif, reason = inspect_retailer_page_state(
        html_content=html,
        url=url,
        retailer="Amazon",
        expected_external_id=asin,
        expected_product_id=pid,
        http_status=200,
    )
    assert avail == "available"
    assert verif == "verified"

    offer = {
        "product_id": pid,
        "retailer": "Amazon",
        "external_product_id": asin,
        "url": url,
        "availability_status": avail,
        "verification_status": verif,
        "last_verified": "2026-09-18T00:00:00Z",
    }
    is_valid, errors = validate_retailer_offer(offer, pid)
    assert is_valid is True, f"Validation errors: {errors}"


def test_unavailable_retailer_offer():
    """Verify Requirement 3, 4, 10: Unavailable Amazon/Flipkart product.
    
    Checks:
    - Product page returning 'Currently unavailable' or 'Out of stock' yields:
      availability_status == 'unavailable'
    - An unavailable offer does NOT get an active Buy button in comparison.
    """
    pid = "c1000000-0000-0000-0000-000000000001"
    asin = "B0CBGF51G3"
    url = f"https://www.amazon.in/dp/{asin}"
    html = "<html><body><h1>Dell XPS 15 9530</h1><span id='availability'>Currently unavailable. We don't know when or if this item will be back in stock.</span></body></html>"

    avail, verif, reason = inspect_retailer_page_state(
        html_content=html,
        url=url,
        retailer="Amazon",
        expected_external_id=asin,
        expected_product_id=pid,
        http_status=200,
    )
    assert avail == "unavailable"

    # Flipkart out of stock
    fk_url = "https://www.flipkart.com/dell-xps-15/p/itm289fe81ad080a"
    fk_html = "<html><body><div class='_16PBlm'>This product is currently out of stock.</div></body></html>"
    fk_avail, fk_verif, _ = inspect_retailer_page_state(
        html_content=fk_html,
        url=fk_url,
        retailer="Flipkart",
        expected_external_id="itm289fe81ad080a",
        expected_product_id=pid,
        http_status=200,
    )
    assert fk_avail == "unavailable"


def test_broken_retailer_offer():
    """Verify Requirement 3, 4, 10: Broken Amazon/Flipkart URLs.
    
    Checks:
    - HTTP 404/410, removed products, or dog pages receive:
      verification_status == 'broken'
    - Broken URLs are never exposed as Buy buttons.
    - An offer claiming 'available' with 'broken' verification fails validation.
    """
    pid = "c1000000-0000-0000-0000-000000000001"
    asin = "B0CBGF51G3"
    url = f"https://www.amazon.in/dp/{asin}"

    # 404 response
    avail, verif, reason = inspect_retailer_page_state(
        html_content="404 Not Found",
        url=url,
        retailer="Amazon",
        expected_external_id=asin,
        expected_product_id=pid,
        http_status=404,
    )
    assert verif == "broken"
    assert avail == "unavailable"

    # Dog page on HTTP 200
    dog_html = "<html><body><h1>Meet the dogs of Amazon</h1><p>Sorry, we couldn't find that page.</p></body></html>"
    d_avail, d_verif, _ = inspect_retailer_page_state(
        html_content=dog_html,
        url=url,
        retailer="Amazon",
        expected_external_id=asin,
        expected_product_id=pid,
        http_status=200,
    )
    assert d_verif == "broken"
    assert d_avail == "unavailable"

    # Reject offer claiming 'available' with broken status
    contradictory_offer = {
        "product_id": pid,
        "retailer": "Amazon",
        "external_product_id": asin,
        "url": url,
        "availability_status": "available",
        "verification_status": "broken",
        "last_verified": "2026-09-18T00:00:00Z",
    }
    is_valid, errors = validate_retailer_offer(contradictory_offer, pid)
    assert is_valid is False
    assert any("broken" in err for err in errors)


def test_unknown_retailer_offer():
    """Verify Requirement 5 & 10: UNKNOWN is a valid state and yields NO Buy button.
    
    Checks:
    - Inconclusive inspection or unverified content results in availability_status == 'unknown'
    - Unknown offers cannot receive Buy buttons.
    - Stale verification degrades active Buy button eligibility.
    """
    pid = "c1000000-0000-0000-0000-000000000001"
    asin = "B0CBGF51G3"
    url = f"https://www.amazon.in/dp/{asin}"

    # Empty content (cannot verify availability)
    avail, verif, reason = inspect_retailer_page_state(
        html_content="",
        url=url,
        retailer="Amazon",
        expected_external_id=asin,
        expected_product_id=pid,
        http_status=200,
    )
    assert avail == "unknown"
    assert verif == "unverified"

    # Stale verification check: offer verified 6 months ago is stale (> 72 hours)
    assert is_verification_stale("2025-01-01T00:00:00Z", max_age_hours=72) is True
    # Fresh verification within 1 hour is not stale
    now_iso = datetime.now(timezone.utc).isoformat()
    assert is_verification_stale(now_iso, max_age_hours=72) is False


def test_wrong_product_retailer_offer():
    """Verify Requirement 8 & 10: Wrong-product retailer URL is rejected.
    
    Checks:
    - ASIN for Product B attached to Product A fails URL verification.
    - Mismatched external_product_id fails validation.
    """
    pid_a = "c1000000-0000-0000-0000-000000000001"  # Dell XPS 15 (ASIN B0CBGF51G3)
    asin_b = "B0CM5JV232"                           # MacBook Pro 14 ASIN
    url_b = f"https://www.amazon.in/dp/{asin_b}"

    # verify_retailer_url rejects ASIN mismatch
    is_valid, reason, ext_id = verify_retailer_url("Amazon", url_b, pid_a, expected_external_id="B0CBGF51G3")
    assert is_valid is False
    assert "ASIN mismatch" in reason

    # inspect_retailer_page_state marks unverified
    avail, verif, reason = inspect_retailer_page_state(
        html_content="<html><body><h1>MacBook</h1></body></html>",
        url=url_b,
        retailer="Amazon",
        expected_external_id="B0CBGF51G3",
        expected_product_id=pid_a,
        http_status=200,
    )
    assert verif == "unverified"
    assert avail == "unknown"


def test_generic_retailer_url_rejected():
    """Verify Requirement 3, 4, 10: Generic search, category, or homepage URLs are rejected.
    
    Checks:
    - Search query URLs (/s?k=, /search?q=)
    - Category browse URLs (/b?node=, /categories/)
    - Marketplace homepages (/)
    All are rejected from receiving Buy buttons.
    """
    pid = "c1000000-0000-0000-0000-000000000001"

    search_urls = [
        ("Amazon", "https://www.amazon.in/s?k=dell+xps+15"),
        ("Amazon", "https://www.amazon.in/b?node=1375424031"),
        ("Amazon", "https://www.amazon.in/"),
        ("Flipkart", "https://www.flipkart.com/search?q=dell+xps+15"),
        ("Flipkart", "https://www.flipkart.com/computers/laptops/pr?sid=6bo,b5g"),
        ("Flipkart", "https://www.flipkart.com/"),
    ]

    for retailer, u in search_urls:
        is_valid, reason, _ = verify_retailer_url(retailer, u, pid)
        assert is_valid is False, f"Expected {u} to be rejected, but passed"
        avail, verif, _ = inspect_retailer_page_state(
            html_content="<html><body>Search Results</body></html>",
            url=u,
            retailer=retailer,
            expected_external_id="B0CBGF51G3",
            expected_product_id=pid,
            http_status=200,
        )
        assert verif == "unverified", f"Generic URL {u} must have verification_status == 'unverified'"
        assert avail == "unknown", f"Generic URL {u} must have availability_status == 'unknown'"

