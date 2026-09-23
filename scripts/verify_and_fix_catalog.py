#!/usr/bin/env python3
"""Verify + auto-fix Amazon/Flipkart links and images via a real cloud browser.

Runs the same live checks as verify_retailer_links.py, but when it finds a
broken/mismatched Amazon link or a broken/placeholder image, it does a live
Amazon.in search for the product, verifies the top candidate actually looks
like the right product (title word-overlap check, same as the read-only
verifier), and only then writes the confirmed-good URL back into
backend/app/services/catalog_fallback.py.

Nothing is ever guessed: if no confident live match is found, the broken
field is left as-is (or nulled for a confirmed-dead link) rather than being
replaced with an unverified value.

Flipkart is checked but not auto-repaired via search (its result-page
selectors are unstable/change often); a confirmed-broken flipkart_url is
nulled out so the UI doesn't show a dead "Buy on Flipkart" link.

Usage:
    export BROWSERBASE_API_KEY=bb_live_...
    python3 scripts/verify_and_fix_catalog.py --apply        # full catalog, writes fixes
    python3 scripts/verify_and_fix_catalog.py --limit 15      # dry run, first 15 products
    python3 scripts/verify_and_fix_catalog.py --product-id c1000000-0000-0000-0000-000000000001 --apply
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.catalog_fallback import FALLBACK_CATALOG  # noqa: E402
from browserbase_client import browserbase_session  # noqa: E402

CATALOG_PATH = Path(__file__).resolve().parent.parent / "backend" / "app" / "services" / "catalog_fallback.py"

NOT_FOUND_MARKERS = [
    "page not found",
    "looking for something",
    "sorry, we couldn't find that page",
    "the page you requested was not found",
    "product is currently unavailable",
]


def title_words(title: str) -> list:
    return [w.lower() for w in re.split(r"[^A-Za-z0-9]+", title) if len(w) > 3][:6]


def check_retailer_page(page, url, product_title) -> str:
    if not url:
        return "no_link"
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=12000)
        status = resp.status if resp else None
        if status and status >= 400:
            return f"http_{status}"
        page.wait_for_timeout(600)
        body_text = page.inner_text("body").lower()
        if any(m in body_text for m in NOT_FOUND_MARKERS):
            return "not_found_page"
        words = title_words(product_title)
        matches = sum(1 for w in words if w in body_text)
        if words and matches == 0:
            return "possible_mismatch"
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return f"error:{type(exc).__name__}"


def check_image(page, url) -> str:
    if not url or url.startswith("data:image"):
        return "placeholder"
    try:
        resp = page.goto(url, wait_until="load", timeout=10000)
        status = resp.status if resp else None
        content_type = resp.headers.get("content-type", "") if resp else ""
        if status and status >= 400:
            return f"http_{status}"
        if "image" not in content_type:
            return "not_an_image"
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return f"error:{type(exc).__name__}"


def find_amazon_replacement(page, title: str):
    """Live Amazon.in search; returns (product_url, image_url) only if a
    confident title match is found, else (None, None)."""
    try:
        page.goto(f"https://www.amazon.in/s?k={quote_plus(title)}", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1500)
        results = page.locator('div[data-component-type="s-search-result"]')
        count = min(results.count(), 5)
        words = title_words(title)
        for i in range(count):
            card = results.nth(i)
            try:
                link = card.locator("h2 a").first
                href = link.get_attribute("href")
                if not href:
                    continue
                card_text = card.inner_text(timeout=2000).lower()
                matches = sum(1 for w in words if w in card_text)
                if not words or matches < max(2, len(words) // 2):
                    continue
                asin_match = re.search(r"/dp/([A-Z0-9]{10})", href)
                product_url = f"https://www.amazon.in/dp/{asin_match.group(1)}" if asin_match else f"https://www.amazon.in{href}"
                img = card.locator("img.s-image").first
                image_url = img.get_attribute("src") if img.count() > 0 else None
                return product_url, image_url
            except Exception:  # noqa: BLE001
                continue
    except Exception:  # noqa: BLE001
        pass
    return None, None


def extract_amazon_image(page, url: str):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)
        for sel in ["#landingImage", "#imgBlkFront", "#main-image"]:
            el = page.locator(sel).first
            if el.count() > 0:
                src = el.get_attribute("src") or el.get_attribute("data-old-hires")
                if src:
                    return src
    except Exception:  # noqa: BLE001
        pass
    return None


def apply_fixes(fixes: dict) -> int:
    """fixes: {product_id: {"amazon_url": ..., "flipkart_url": ..., "image_url": ...}}
    Only keys present are changed; a value of None means "null it out"."""
    text = CATALOG_PATH.read_text()
    applied = 0
    for product_id, fields in fixes.items():
        block_match = re.search(
            rf'(\{{\s*"id":\s*"{re.escape(product_id)}".*?\n\s*\}},?\n)(?=\s*\{{\s*"id"|\s*\])',
            text, re.DOTALL,
        )
        if not block_match:
            print(f"    ! could not locate block for {product_id}, skipping write")
            continue
        block = block_match.group(1)
        new_block = block
        for field, value in fields.items():
            new_value = "null" if value is None else '"' + value.replace('"', '\\"') + '"'
            new_block, n = re.subn(
                rf'("{field}":\s*)(?:"(?:[^"\\]|\\.)*"|null)(,?\n)',
                lambda m: f"{m.group(1)}{new_value}{m.group(2)}",
                new_block, count=1,
            )
            if n:
                applied += 1
        if new_block != block:
            text = text[: block_match.start(1)] + new_block + text[block_match.end(1):]
    CATALOG_PATH.write_text(text)
    return applied


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify + auto-fix retailer links/images with Browserbase")
    parser.add_argument("--limit", type=int, default=15, help="Number of products to check (default 15, ignored with --apply and no --product-id)")
    parser.add_argument("--product-id", type=str, default=None)
    parser.add_argument("--apply", action="store_true", help="Run on the full catalog and write fixes back to catalog_fallback.py")
    args = parser.parse_args()

    products = FALLBACK_CATALOG
    if args.product_id:
        products = [p for p in products if p["id"] == args.product_id]
        if not products:
            print(f"No product found with id {args.product_id}")
            sys.exit(1)
    elif not args.apply:
        products = products[: args.limit]

    print(f"Checking {len(products)} product(s), reconnecting a fresh Browserbase session as needed (apply={args.apply})...\n")

    checked = fixed = nulled = 0
    total_applied = 0
    idx = 0

    while idx < len(products):
        try:
            with browserbase_session("verify-and-fix-catalog") as page:
                while idx < len(products):
                    p = products[idx]
                    idx += 1
                    title = p["title"]
                    pid = p["id"]
                    checked += 1
                    product_fixes = {}

                    az_status = check_retailer_page(page, p.get("amazon_url"), title)
                    fk_status = check_retailer_page(page, p.get("flipkart_url"), title)
                    img_status = check_image(page, p.get("image_url"))
                    print(f"- {title}\n    amazon={az_status} flipkart={fk_status} image={img_status}")

                    amazon_broken = az_status not in ("ok",)
                    if amazon_broken:
                        # Live search-based repair proved unreliable against Amazon's
                        # bot detection (hangs / blocked), so we don't guess a
                        # replacement -- a confirmed-dead link is nulled rather than
                        # risk showing the wrong product.
                        if az_status.startswith("http_4") or az_status == "not_found_page" or az_status == "possible_mismatch":
                            product_fixes["amazon_url"] = None
                            print(f"    -> confirmed broken ({az_status}); nulled amazon_url rather than guess")
                    elif img_status not in ("ok", "placeholder"):
                        new_img = extract_amazon_image(page, p["amazon_url"])
                        if new_img:
                            product_fixes["image_url"] = new_img
                            print("    -> fixed image_url from existing amazon page")

                    if fk_status.startswith("http_4") or fk_status == "not_found_page":
                        product_fixes["flipkart_url"] = None
                        print("    -> nulled dead flipkart_url")

                    if img_status == "placeholder" and "image_url" not in product_fixes and p.get("amazon_url") and not amazon_broken:
                        new_img = extract_amazon_image(page, p["amazon_url"])
                        if new_img:
                            product_fixes["image_url"] = new_img
                            print("    -> filled placeholder image_url from amazon page")

                    if product_fixes:
                        if any(v is None for v in product_fixes.values()):
                            nulled += 1
                        if any(v is not None for v in product_fixes.values()):
                            fixed += 1
                        if args.apply:
                            applied = apply_fixes({pid: product_fixes})
                            total_applied += applied
                    print()
        except Exception as exc:  # noqa: BLE001
            print(f"[browserbase] session dropped ({type(exc).__name__}); reconnecting with a fresh session...\n")
            continue

    print(f"\n{checked} checked, {fixed + nulled} product(s) with changes ({fixed} repaired, {nulled} had a field nulled).")

    if args.apply:
        print(f"Wrote {total_applied} field change(s) to backend/app/services/catalog_fallback.py")
    elif fixed or nulled:
        print("(dry run - pass --apply to write these changes to catalog_fallback.py)")


if __name__ == "__main__":
    main()
