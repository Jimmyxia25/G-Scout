"""FastAPI app: trigger scrapes, serve products + the demo page."""
from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

from config import SITES, CATEGORIES
from scrapers.adapters import scrape_all
from storage import init_db, save_products, list_latest

app = FastAPI(title="G-Scout", description="海外户外装备价格/折扣监测")

init_db()


@app.get("/api/meta")
def meta():
    """Site + category registry for the frontend filters."""
    return {
        "sites": {k: {"name": v["name"], "kind": v["kind"]} for k, v in SITES.items()},
        "categories": CATEGORIES,
    }


@app.post("/api/scrape")
def trigger_scrape(category: str | None = Query(default=None)):
    """Run a scrape pass and persist results. Returns a per-site status report."""
    cats = [category] if category else None
    products, report = scrape_all(cats)
    saved = save_products(products)
    return JSONResponse({"saved": saved, "report": report})


@app.get("/api/products")
def products(
    site: str | None = Query(default=None),
    category: str | None = Query(default=None),
    min_discount: int = Query(default=0, ge=0, le=100),
):
    """Latest price snapshot per product, with optional filters."""
    return list_latest(site=site, category=category, min_discount=min_discount)


@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
