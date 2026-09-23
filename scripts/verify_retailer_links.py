#!/usr/bin/env python3
"""Verify Amazon/Flipkart product links and images via a real cloud browser.

Uses one Browserbase session (see scripts/browserbase_client.py) to open
each product's stored amazon_url, flipkart_url, and primary image_url from
backend/app/services/catalog_fallback.py, and reports whether each one is
actually live and looks like the right product (page not found / removed /
redirected-to-homepage patterns are flagged), rather than just a bare
HTTP status check.

Usage:
    export BROWSERBASE_API_KEY=bb_live_...
    python3 scripts/verify_retailer_links.py --limit 15
    python3 scripts/verify_retailer_links.py --product-id c1000000-0000-0000-0000-000000000001
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.catalog_fallback import FALLBACK_CATALOG  # noqa: E402
from browserbase_client import browserbase_session  # noqa: E402

NOT_FOUND_MARKERS = [
    "page not found",
    "looking for something",
    "sorry, we couldn't find that page",
    "the page you requested was not found",
    "product is currently unavailable",
]


def check_retailer_page(page, url: str, retailer: str, product_title: str) -> str:
    """Navigate to a retailer product page and classify what's actually there."""
    if not url:
        return "no_link"
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=20000)
        status = resp.status if resp else None
        if status and status >= 400:
            return f"http_{status}"
        page.wait_for_timeout(1500)  # let client-side redirects/content settle
        body_text = page.inner_text("body").lower()
        if any(marker in body_text for marker in NOT_FOUND_MARKERS):
            return "not_found_page"
        title_words = [w.lower() for w in product_title.split() if len(w) > 3][:4]
        matches = sum(1 for w in title_words if w in body_text)
        if title_words and matches == 0:
            return "possible_mismatch"
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return f"error:{type(exc).__name__}"


def check_image(page, url: str) -> str:
    if not url or url.startswith("data:image"):
        return "placeholder"
    try:
        resp = page.goto(url, wait_until="load", timeout=15000)
        status = resp.status if resp else None
        content_type = resp.headers.get("content-type", "") if resp else ""
        if status and status >= 400:
            return f"http_{status}"
        if "image" not in content_type:
            return "not_an_image"
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return f"error:{type(exc).__name__}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify retailer links/images with Browserbase")
    parser.add_argument("--limit", type=int, default=15, help="Number of products to check (default 15)")
    parser.add_argument("--product-id", type=str, default=None, help="Check a single product by id")
    args = parser.parse_args()

    products = FALLBACK_CATALOG
    if args.product_id:
        products = [p for p in products if p["id"] == args.product_id]
        if not products:
            print(f"No product found with id {args.product_id}")
            sys.exit(1)
    else:
        products = products[: args.limit]

    print(f"Checking {len(products)} product(s) via a single Browserbase cloud browser session...\n")

    results = []
    with browserbase_session("verify-retailer-links") as page:
        for p in products:
            title = p["title"]
            print(f"- {title}")

            az_status = check_retailer_page(page, p.get("amazon_url"), "Amazon", title)
            print(f"    amazon:   {az_status}")

            fk_status = check_retailer_page(page, p.get("flipkart_url"), "Flipkart", title)
            print(f"    flipkart: {fk_status}")

            img_status = check_image(page, p.get("image_url"))
            print(f"    image:    {img_status}")

            results.append({
                "id": p["id"], "title": title,
                "amazon": az_status, "flipkart": fk_status, "image": img_status,
            })

    problems = [r for r in results if "ok" not in (r["amazon"], r["flipkart"]) or r["image"] not in ("ok", "placeholder")]
    print(f"\n{len(results)} checked, {len(problems)} with a possible issue.")
    for r in problems:
        print(f"  ! {r['title']}: amazon={r['amazon']} flipkart={r['flipkart']} image={r['image']}")


if __name__ == "__main__":
    main()
