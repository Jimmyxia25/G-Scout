"""Per-site adapters + scrape orchestration.

Strategy (per the chosen '真实抓取 + 容错降级' approach):
  1. Build a category search/listing URL for the site.
  2. Try static HTTP fetch, then Playwright render.
  3. Parse embedded schema.org/JSON-LD Product data (most of these
     retailers embed it) into Product objects.
  4. If anything fails or yields nothing (anti-bot block, layout change),
     fall back to that site's representative SAMPLE_PRODUCTS so the
     end-to-end pipeline stays demoable.
"""
from __future__ import annotations

import json

from config import SITES
from models import Product
from scrapers.fetch import fetch_static, fetch_rendered
from scrapers.sample_data import SAMPLE_PRODUCTS

# Category -> per-site search/listing path. Best-effort; refine per site later.
CATEGORY_PATHS = {
    "rei": {
        "apparel": "/search?q=insulated+jacket",
        "footwear": "/search?q=hiking+shoes",
    },
    "backcountry": {
        "apparel": "/insulated-jackets",
        "footwear": "/hiking-shoes",
    },
    "steepandcheap": {
        "apparel": "/search?q=jacket",
        "footwear": "/search?q=hiking+shoes",
    },
    "publiclands": {
        "apparel": "/search?q=jacket",
        "footwear": "/search?q=hiking+boots",
    },
}


def _to_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _iter_jsonld_objects(html: str):
    """Yield every JSON object found in <script type=application/ld+json> tags."""
    from selectolax.parser import HTMLParser

    tree = HTMLParser(html)
    for node in tree.css('script[type="application/ld+json"]'):
        raw = node.text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            cur = stack.pop()
            if isinstance(cur, list):
                stack.extend(cur)
            elif isinstance(cur, dict):
                yield cur
                if "@graph" in cur and isinstance(cur["@graph"], list):
                    stack.extend(cur["@graph"])


def _parse_products(html: str, site: str, category: str, base_url: str) -> list[Product]:
    """Extract Product objects from schema.org JSON-LD embedded in the page."""
    products: list[Product] = []
    for obj in _iter_jsonld_objects(html):
        if obj.get("@type") not in ("Product", ["Product"]):
            continue
        name = obj.get("name")
        if not name:
            continue
        offers = obj.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        price = _to_float(offers.get("price"))
        list_price = _to_float(offers.get("highPrice")) or price
        brand = obj.get("brand")
        if isinstance(brand, dict):
            brand = brand.get("name")
        url = obj.get("url") or base_url
        if url and url.startswith("/"):
            url = base_url.rstrip("/") + url
        products.append(
            Product(site, category, name, brand, url, price, list_price)
        )
    return products


def scrape_site_category(site: str, category: str) -> tuple[list[Product], str]:
    """Scrape one site+category. Returns (products, status).

    status is "live" if real data was parsed, else "fallback".
    """
    base_url = SITES[site]["base_url"]
    path = CATEGORY_PATHS.get(site, {}).get(category)

    if path:
        target = base_url.rstrip("/") + path
        html = fetch_static(target) or fetch_rendered(target)
        if html:
            parsed = _parse_products(html, site, category, base_url)
            if parsed:
                return parsed, "live"

    # Fallback: representative sample data for this site+category.
    fallback = [
        p for p in SAMPLE_PRODUCTS if p.site == site and p.category == category
    ]
    return fallback, "fallback"


def scrape_all(categories: list[str] | None = None) -> tuple[list[Product], dict]:
    """Scrape every price-source site across the given categories.

    Returns (products, report) where report maps "site/category" -> status.
    Review-kind sites (e.g. Switchback) are skipped as price sources.
    """
    from config import CATEGORIES

    cats = categories or list(CATEGORIES.keys())
    products: list[Product] = []
    report: dict[str, str] = {}

    for site, meta in SITES.items():
        if meta["kind"] != "price":
            continue
        for category in cats:
            items, status = scrape_site_category(site, category)
            products.extend(items)
            report[f"{site}/{category}"] = f"{status} ({len(items)})"
    return products, report
