"""SQLite storage: products + price history snapshots."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from models import Product

DB_PATH = Path(__file__).parent / "gscout.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    site        TEXT NOT NULL,
    category    TEXT NOT NULL,
    name        TEXT NOT NULL,
    brand       TEXT,
    url         TEXT NOT NULL,
    UNIQUE(site, url)
);

CREATE TABLE IF NOT EXISTS price_snapshots (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id   INTEGER NOT NULL REFERENCES products(id),
    price        REAL,
    list_price   REAL,
    discount_pct INTEGER,
    captured_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def save_products(products: list[Product]) -> int:
    """Upsert products and append a fresh price snapshot for each. Returns count."""
    init_db()
    with get_conn() as conn:
        for p in products:
            cur = conn.execute(
                "INSERT INTO products (site, category, name, brand, url) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(site, url) DO UPDATE SET "
                "category=excluded.category, name=excluded.name, brand=excluded.brand",
                (p.site, p.category, p.name, p.brand, p.url),
            )
            row = conn.execute(
                "SELECT id FROM products WHERE site=? AND url=?", (p.site, p.url)
            ).fetchone()
            product_id = row["id"]
            conn.execute(
                "INSERT INTO price_snapshots "
                "(product_id, price, list_price, discount_pct) VALUES (?, ?, ?, ?)",
                (product_id, p.price, p.list_price, p.discount_pct),
            )
        conn.commit()
    return len(products)


def list_latest(site: str | None = None, category: str | None = None,
                min_discount: int = 0) -> list[dict]:
    """Return each product with its most recent price snapshot, with filters."""
    init_db()
    query = """
        SELECT p.id, p.site, p.category, p.name, p.brand, p.url,
               s.price, s.list_price, s.discount_pct, s.captured_at
        FROM products p
        JOIN price_snapshots s ON s.id = (
            SELECT id FROM price_snapshots
            WHERE product_id = p.id ORDER BY captured_at DESC, id DESC LIMIT 1
        )
        WHERE 1=1
    """
    params: list = []
    if site:
        query += " AND p.site = ?"
        params.append(site)
    if category:
        query += " AND p.category = ?"
        params.append(category)
    if min_discount:
        query += " AND s.discount_pct >= ?"
        params.append(min_discount)
    query += " ORDER BY s.discount_pct DESC, p.site"
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]
