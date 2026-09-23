#!/usr/bin/env python3
"""Scrape live Amazon/Flipkart price + stock status via a Browserbase cloud browser.

The catalog's stored prices are static seed data. This script opens each
product's real amazon_url / flipkart_url in a Browserbase cloud browser and
extracts the retailer's *current* displayed price and stock status, so it
can be compared against (or used to refresh) the catalog data.

This is deterministic Playwright, not Stagehand -- selectors are best-effort
and may need updating if a retailer changes their page layout; that's the
known trade-off of the Python+Playwright path over Stagehand's natural-
language extract() (see project notes on why Stagehand wasn't used here:
it requires Node >=22.18 and TypeScript, this backend is Python).

Usage:
    export BROWSERBASE_API_KEY=bb_live_...
    python3 scripts/scrape_retailer_prices.py --limit 10
    python3 scripts/scrape_retailer_prices.py --product-id c1000000-0000-0000-0000-000000000001
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.catalog_fallback import FALLBACK_CATALOG  # noqa: E402
from browserbase_client import browserbase_session  # noqa: E402

# Ordered by likelihood; first matching selector with text wins.
AMAZON_PRICE_SELECTORS = [
    "#corePrice_feature_div .a-price .a-offscreen",
    "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    ".a-price .a-offscreen",
]
AMAZON_STOCK_SELECTORS = ["#availability span", "#outOfStock"]

FLIPKART_PRICE_SELECTORS = [
    "div._30jeq3._16Jk6d",  # classic Flipkart price class (subject to change)
    "div._30jeq3",
]
FLIPKART_STOCK_MARKERS = ["sold out", "out of stock", "currently unavailable"]


def _first_text(page, selectors) -> Optional[str]:
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if el.count() > 0:
                text = el.inner_text(timeout=3000).strip()
                if text:
                    return text
        except Exception:  # noqa: BLE001
            continue
    return None


def parse_price(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    digits = re.sub(r"[^\d.]", "", text)
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def scrape_amazon(page, url: str) -> dict:
    page.goto(url, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(1500)
    price_text = _first_text(page, AMAZON_PRICE_SELECTORS)
    stock_text = _first_text(page, AMAZON_STOCK_SELECTORS)
    return {
        "retailer": "Amazon",
        "price_text": price_text,
        "price": parse_price(price_text),
        "stock_text": stock_text,
    }


def scrape_flipkart(page, url: str) -> dict:
    page.goto(url, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(1500)
    price_text = _first_text(page, FLIPKART_PRICE_SELECTORS)
    body_text = page.inner_text("body").lower()
    out_of_stock = any(marker in body_text for marker in FLIPKART_STOCK_MARKERS)
    return {
        "retailer": "Flipkart",
        "price_text": price_text,
        "price": parse_price(price_text),
        "stock_text": "Out of stock" if out_of_stock else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape live retailer prices with Browserbase")
    parser.add_argument("--limit", type=int, default=10, help="Number of products to scrape (default 10)")
    parser.add_argument("--product-id", type=str, default=None, help="Scrape a single product by id")
    args = parser.parse_args()

    products = FALLBACK_CATALOG
    if args.product_id:
        products = [p for p in products if p["id"] == args.product_id]
        if not products:
            print(f"No product found with id {args.product_id}")
            sys.exit(1)
    else:
        products = [p for p in products if p.get("amazon_url") or p.get("flipkart_url")][: args.limit]

    print(f"Scraping live prices for {len(products)} product(s) via a single Browserbase session...\n")

    with browserbase_session("scrape-retailer-prices") as page:
        for p in products:
            print(f"- {p['title']}")
            print(f"    catalog price: {p.get('currency', 'INR')} {p.get('price')}")

            if p.get("amazon_url"):
                try:
                    r = scrape_amazon(page, p["amazon_url"])
                    print(f"    amazon live:   {r['price_text']} (stock: {r['stock_text'] or 'in stock / unknown'})")
                except Exception as exc:  # noqa: BLE001
                    print(f"    amazon live:   error ({type(exc).__name__})")

            if p.get("flipkart_url"):
                try:
                    r = scrape_flipkart(page, p["flipkart_url"])
                    print(f"    flipkart live: {r['price_text']} (stock: {r['stock_text'] or 'in stock / unknown'})")
                except Exception as exc:  # noqa: BLE001
                    print(f"    flipkart live: error ({type(exc).__name__})")
            print()


if __name__ == "__main__":
    main()
