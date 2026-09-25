"""Live web retrieval fallback via Browserbase.

Used by the orchestrator only when the internal PostgreSQL/OpenSearch catalog
returns too few candidates for a query (wrong/missing category, or a stated
budget the local catalog can't satisfy). Opens a real Browserbase cloud
browser, searches Amazon India, and extracts actual live listings -- never
fabricated data. Every field is either scraped or omitted.

Returned items are shaped exactly like the internal OpenSearch candidate
dicts the orchestrator already works with (id/title/brand/category/price/
retailer_offers/specs/...), so they flow through the *same* existing
ranking, budget-filtering, and card-building code -- no separate rendering
path, no UI change.

Runs Playwright's SYNC API inside a worker thread (via asyncio.to_thread)
rather than the async API. The sync approach is the one already proven
reliable end-to-end against Browserbase in scripts/verify_and_fix_catalog.py;
running it in a thread lets the calling async code bound it with a hard
asyncio.wait_for timeout without depending on async-Playwright/event-loop
interaction that proved unreliable in this environment.
"""

import asyncio
import re
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from app.core.config import settings
from app.core.logging import logger

KNOWN_BRANDS = [
    "Apple", "Samsung", "OnePlus", "Xiaomi", "Redmi", "Realme", "Vivo", "Oppo", "Google", "Pixel",
    "Motorola", "Nothing", "iQOO", "Asus", "ROG", "Dell", "HP", "Lenovo", "Acer", "MSI", "Sony",
    "Boat", "boAt", "JBL", "Bose", "Sennheiser", "Skullcandy", "Noise", "Zebronics", "Logitech",
    "Corsair", "Razer", "Espressif", "Raspberry Pi", "Arduino", "SparkFun", "Adafruit",
]


def _guess_brand(title: str) -> Optional[str]:
    low = title.lower()
    for b in KNOWN_BRANDS:
        if b.lower() in low:
            return b
    return title.split()[0] if title.split() else None


def _guess_model(title: str, brand: Optional[str]) -> str:
    """Best-effort model name: the title with the brand prefix stripped and
    trailing parenthetical variant/spec details removed. Never fabricated --
    derived purely from the scraped title, empty string if nothing usable."""
    text = title
    if brand:
        text = re.sub(rf"^\s*{re.escape(brand)}\s+", "", text, flags=re.IGNORECASE)
    text = re.split(r"[\(\-]", text)[0].strip()
    return text


def _parse_price(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    digits = re.sub(r"[^\d.]", "", text)
    try:
        val = float(digits) if digits else None
        return val if val and val > 0 else None
    except ValueError:
        return None


_SKIP_REVIEW_LINES = {"helpful", "report", "comment", "see more"}


def _parse_review_block(text: str) -> Optional[Dict[str, Any]]:
    """Parse one Amazon review block's plain text into {title, body, rating}.
    Amazon's review DOM nests title/body oddly across a11y spans, so this
    parses the block's rendered line order instead of relying on specific
    data-hook selectors for each field. Returns None if no rating or body
    text could be confidently found -- never fabricates a review."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    rating: Optional[float] = None
    title: Optional[str] = None
    body_lines: List[str] = []
    collecting_body = False

    for i, line in enumerate(lines):
        star_match = re.match(r"^(\d(?:\.\d)?)\s+out of 5 stars", line, re.IGNORECASE)
        if star_match and rating is None:
            rating = float(star_match.group(1))
            if i + 1 < len(lines) and not lines[i + 1].lower().startswith("reviewed in"):
                title = lines[i + 1]
            continue
        low = line.lower()
        if low.startswith("reviewed in"):
            collecting_body = True
            continue
        if low in ("verified purchase",):
            continue
        if low in _SKIP_REVIEW_LINES:
            break
        if collecting_body:
            body_lines.append(line)

    body = " ".join(body_lines).strip()
    if rating is None or not body:
        return None
    return {"title": title or "", "body": body, "rating": rating}


def _extract_specs_and_reviews(page, product_url: str) -> tuple:
    """Visit a product's own page and extract real spec rows (from Amazon's
    product-overview table, falling back to the top feature bullet) and up to
    3 real customer reviews. Returns ({}, []) on any failure -- callers keep
    working with just the search-result fields rather than fabricating
    specs/reviews."""
    specs: Dict[str, str] = {}
    reviews: List[Dict[str, Any]] = []
    try:
        page.goto(product_url, wait_until="domcontentloaded", timeout=9000)
        page.wait_for_timeout(500)

        rows = page.locator("#productOverview_feature_div table tr")
        row_count = min(rows.count(), 8)
        for i in range(row_count):
            try:
                cells = rows.nth(i).locator("td, th")
                if cells.count() >= 2:
                    key = cells.nth(0).inner_text(timeout=1000).strip()
                    val = cells.nth(1).inner_text(timeout=1000).strip()
                    if key and val:
                        specs[key] = val
            except Exception:  # noqa: BLE001
                continue

        if not specs:
            bullets = page.locator("#feature-bullets li span.a-list-item")
            b_count = min(bullets.count(), 3)
            for i in range(b_count):
                try:
                    text = bullets.nth(i).inner_text(timeout=1000).strip()
                    if text:
                        specs[f"Highlight {i + 1}"] = text
                except Exception:  # noqa: BLE001
                    continue

        review_blocks = page.locator('[data-hook="review"]')
        rb_count = min(review_blocks.count(), 4)
        for i in range(rb_count):
            if len(reviews) >= 3:
                break
            try:
                block_text = review_blocks.nth(i).inner_text(timeout=1200)
                parsed = _parse_review_block(block_text)
                if parsed:
                    reviews.append(parsed)
            except Exception:  # noqa: BLE001
                continue
    except Exception:  # noqa: BLE001
        pass

    return specs, reviews


async def search_web_products(
    category_query: str,
    brand: Optional[str] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    limit: int = 6,
) -> List[Dict[str, Any]]:
    """Live-search Amazon India for products matching category/brand/budget.

    Returns [] (never fabricated data) if Browserbase is unavailable, the
    search fails, or nothing verifiable is found within the time budget.
    Every returned item has a real scraped title, a live product URL, and
    (when available) a real scraped price -- items with no verifiable price
    are dropped when a budget constraint is active, since we can't confirm
    they're in range.
    """
    if not settings.WEB_RETRIEVAL_ENABLED or not settings.BROWSERBASE_API_KEY:
        return []

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(
                _search_amazon_sync, category_query, brand, budget_min, budget_max, limit
            ),
            timeout=settings.WEB_RETRIEVAL_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning("Web retrieval timed out; continuing with internal results only")
        return []
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Web retrieval failed, continuing with internal results only: {exc}")
        return []


async def resolve_live_amazon_link(title: str, brand: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Single-item live Amazon lookup for a catalog product that has no stored
    ASIN (mostly electronic components) -- used to replace a generic search
    link with a real direct product page. Reuses the same search+scrape path
    as search_web_products with limit=1, so it also picks up real specs.
    Returns None (never fabricates) if nothing verifiable is found in time.

    Most of the wall time here is Browserbase session startup + navigation,
    not per-item scraping -- a single-item lookup isn't meaningfully faster
    than a multi-item one (~75-90s observed), so this uses the same overall
    budget as search_web_products rather than a short, tighter timeout that
    would cut off genuinely-succeeding lookups before they finish."""
    if not settings.WEB_RETRIEVAL_ENABLED or not settings.BROWSERBASE_API_KEY:
        return None
    # A catalog title's parenthetical variant details ("(8GB / 128GB / Awesome
    # Navy)") make the search query overly specific -- Amazon frequently has
    # no exact listing for that precise config/color and returns an unrelated
    # top result instead. Strip to the brand+model portion, which is enough
    # identity for the guard in the caller to still verify the match.
    search_title = re.split(r"\s*\(", title, maxsplit=1)[0].strip() or title
    for attempt in range(2):
        try:
            items = await asyncio.wait_for(
                asyncio.to_thread(_search_amazon_sync, search_title, brand, None, None, 1),
                timeout=settings.WEB_RETRIEVAL_TIMEOUT_SECONDS,
            )
            break
        except Exception as exc:  # noqa: BLE001
            # Browserbase enforces a burst limit on session creation (5/min);
            # under concurrent load from multiple cards enriching at once, one
            # can lose that race even after staggering. Retry once rather than
            # silently leaving a resolvable link as a search fallback.
            is_rate_limit = "429" in str(exc) or "RateLimitError" in type(exc).__name__
            if is_rate_limit and attempt == 0:
                logger.warning(f"[resolve_live_amazon_link] rate-limited for '{title[:60]}', retrying once in 15s")
                await asyncio.sleep(15)
                continue
            logger.warning(f"[resolve_live_amazon_link] failed for '{title[:60]}': {exc!r}")
            return None
    return items[0] if items else None


def _search_amazon_sync(
    category_query: str,
    brand: Optional[str],
    budget_min: Optional[float],
    budget_max: Optional[float],
    limit: int,
) -> List[Dict[str, Any]]:
    """Runs in a worker thread -- blocking sync Playwright + Browserbase calls
    are safe here since they don't block the FastAPI event loop, and a hung
    call just makes this thread outlive the request rather than the request
    itself (the caller's asyncio.wait_for still returns on time)."""
    from browserbase import Browserbase
    from playwright.sync_api import sync_playwright

    # Don't duplicate the brand name into the query when the title/category
    # text already starts with it (common when this is called with a full
    # catalog product title) -- "Samsung Samsung Galaxy A35..." confuses
    # Amazon's search into returning a poor top match far more often than
    # the clean, single-brand query does.
    brand_already_present = bool(brand) and category_query.strip().lower().startswith(brand.strip().lower())
    query_text = f"{(brand + ' ') if (brand and not brand_already_present) else ''}{category_query}".strip()
    search_url = f"https://www.amazon.in/s?k={quote_plus(query_text)}"
    if budget_min is not None or budget_max is not None:
        lo = int((budget_min or 0) * 100)
        hi = int((budget_max or 10_000_000) * 100)
        search_url += f"&rh=p_36%3A{lo}-{hi}"

    bb = Browserbase(api_key=settings.BROWSERBASE_API_KEY)
    session = bb.sessions.create()
    logger.info(f"[web_retrieval] Browserbase session {session.id} for query '{query_text}'")

    results: List[Dict[str, Any]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(session.connect_url)
        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(1200)

            cards = page.locator('div[data-component-type="s-search-result"]')
            count = min(cards.count(), limit * 3)  # over-fetch, filter down below

            for i in range(count):
                if len(results) >= limit:
                    break
                card = cards.nth(i)
                try:
                    # Amazon's current markup doesn't reliably nest the product
                    # link inside <h2> (sponsored cards especially), but every
                    # real result card carries its ASIN directly as a data-asin
                    # attribute -- use that instead of parsing an <a href>.
                    asin = card.get_attribute("data-asin", timeout=2000)
                    # Each card actually has TWO <h2> elements: a small
                    # "a-size-mini" one holding just the brand name link
                    # ("Samsung", "Lava"...), and the real product title in an
                    # "a-size-medium" one elsewhere in the card. `h2 span`
                    # .first was grabbing the brand-only h2, silently mis-
                    # labeling every scraped product with a one-word title --
                    # the root cause of "wrong product" complaints, since a
                    # card that says just "Samsung" can't be told apart from
                    # any other Samsung listing downstream. Target the real
                    # title h2 specifically, with graceful fallbacks.
                    title_el = card.locator("h2.a-size-medium span").first
                    if not title_el.count():
                        title_el = card.locator("h2[aria-label] span").first
                    if not title_el.count():
                        # Last resort: the product image's alt text is also a
                        # real, full title, never the brand-only stub.
                        img_alt_el = card.locator("img.s-image").first
                        title = img_alt_el.get_attribute("alt", timeout=1500) if img_alt_el.count() else None
                        title = title.strip() if title else None
                    else:
                        title = title_el.inner_text(timeout=2000).strip()
                    if not asin or not title:
                        continue

                    product_url = f"https://www.amazon.in/dp/{asin}"

                    price_el = card.locator(".a-price .a-offscreen").first
                    price_text = price_el.inner_text(timeout=1500) if price_el.count() else None
                    price = _parse_price(price_text)

                    # Never guess a price into range -- if a budget was stated and we
                    # couldn't scrape a real price, drop the item rather than show it.
                    if (budget_min is not None or budget_max is not None) and price is None:
                        continue
                    if price is not None:
                        if budget_min is not None and price < budget_min:
                            continue
                        if budget_max is not None and price > budget_max:
                            continue

                    img_el = card.locator("img.s-image").first
                    image_url = img_el.get_attribute("src", timeout=1500) if img_el.count() else None

                    # Skip the per-product detail-page visit (specs/reviews
                    # scrape) -- it was the dominant cost of a live search
                    # (~10-15s per product, sequential), turning a 6-product
                    # search into 90-150s. Search-result-page data (title,
                    # price, image) is enough to show a real, verified,
                    # correctly-linked product fast; specs/reviews for
                    # web-sourced items are honestly left empty rather than
                    # fabricated, same as any other field we don't have.
                    specs, product_reviews = {}, []

                    pid = str(uuid.uuid5(uuid.NAMESPACE_URL, product_url))
                    guessed_brand = _guess_brand(title)
                    # Never claim availability we can't back with a scraped
                    # price -- "unknown" rather than defaulting to "available".
                    availability = "available" if price is not None else "unknown"
                    results.append({
                        "id": pid,
                        "title": title,
                        "brand": guessed_brand,
                        "model": _guess_model(title, guessed_brand),
                        "category": category_query,
                        "price": price,
                        "currency": "INR",
                        "availability": availability,
                        "is_component": False,
                        "retrieval_score": 5.0,
                        "external_product_id": asin,
                        "image_url": image_url,
                        "source": "web",
                        "source_type": "web",
                        "source_url": product_url,
                        "specs": specs,
                        "_reviews": product_reviews,
                        "retailer_offers": [{
                            "product_id": pid,
                            "retailer": "Amazon",
                            "external_product_id": asin,
                            "url": product_url,
                            "price": price,
                            "currency": "INR",
                            "availability_status": availability,
                            "verification_status": "verified",
                        }] if price is not None else [],
                    })
                except Exception:  # noqa: BLE001
                    continue
        finally:
            browser.close()

    logger.info(f"[web_retrieval] found {len(results)} verified live product(s) for '{query_text}'")
    return results
