"""Shared Browserbase cloud-browser helper.

Creates a single Browserbase session and connects Playwright to it over
CDP (Chrome DevTools Protocol). Used by scripts/verify_retailer_links.py
and scripts/scrape_retailer_prices.py so a whole run reuses one cloud
browser session instead of spinning up a new one per product (Browserbase's
free plan caps browser time/session count).

Requires BROWSERBASE_API_KEY to be exported in the shell (or sourced from
.env) -- no project id is needed, the API key resolves it automatically.
"""

import os
import sys
from contextlib import contextmanager

from browserbase import Browserbase
from playwright.sync_api import sync_playwright


def get_api_key() -> str:
    key = os.environ.get("BROWSERBASE_API_KEY")
    if not key:
        print(
            "BROWSERBASE_API_KEY is not set. Export it or add it to .env, e.g.:\n"
            "  export BROWSERBASE_API_KEY=bb_live_...",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


@contextmanager
def browserbase_session(session_name: str = "product-advisor-script"):
    """Yields a Playwright `page` connected to a fresh Browserbase cloud
    browser session. Prints the full session replay link on exit so the
    run can be reviewed at https://www.browserbase.com/sessions/<id>.
    """
    bb = Browserbase(api_key=get_api_key())
    session = bb.sessions.create()  # project is resolved automatically from the API key

    print(f"[browserbase] session started: {session.id}")
    print(f"[browserbase] live view / replay: https://www.browserbase.com/sessions/{session.id}")

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(session.connect_url)
        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            yield page
        finally:
            browser.close()

    print(f"[browserbase] session complete: https://www.browserbase.com/sessions/{session.id}")
