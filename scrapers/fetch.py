"""Base scraping utilities: HTTP fetch with optional Playwright fallback."""
from __future__ import annotations

import httpx

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_static(url: str, timeout: float = 20.0) -> str | None:
    """Plain HTTP GET. Returns HTML text, or None on any failure/block."""
    try:
        resp = httpx.get(
            url, headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True
        )
        if resp.status_code == 200 and resp.text:
            return resp.text
        return None
    except Exception:
        return None


def fetch_rendered(url: str, timeout: float = 30.0) -> str | None:
    """Render with Playwright (handles JS-heavy / anti-bot pages).

    Imported lazily so the app runs even when Playwright/browsers aren't installed.
    Returns None if Playwright is unavailable or the page can't be loaded.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=DEFAULT_HEADERS["User-Agent"])
            page.goto(url, timeout=int(timeout * 1000), wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            html = page.content()
            browser.close()
            return html
    except Exception:
        return None
