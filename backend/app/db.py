import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


def _db_path() -> str:
    return os.getenv(
        "DATABASE_PATH",
        str(Path(__file__).parents[2] / "data" / "products.db"),
    )


@contextmanager
def get_db():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def search_products(query: str, limit: int = 20) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT p.* FROM products p
               JOIN products_fts fts ON p.product_id = fts.product_id
               WHERE products_fts MATCH ?
               LIMIT ?""",
            (query, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def filter_products(
    category: str | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    keywords: list[str] | None = None,
    limit: int = 50,
) -> list[dict]:
    conditions, params = [], []
    if category:
        conditions.append("category LIKE ?")
        params.append(f"{category}%")
    if max_price is not None:
        conditions.append("discounted_price <= ?")
        params.append(max_price)
    if min_rating is not None:
        conditions.append("rating >= ?")
        params.append(min_rating)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    with get_db() as conn:
        rows = conn.execute(
            f"SELECT * FROM products {where} LIMIT ?", params + [limit]
        ).fetchall()

    results = [dict(r) for r in rows]
    if keywords:
        kw = [k.lower() for k in keywords]
        results = [
            r for r in results
            if any(
                w in (r["product_name"] or "").lower()
                or w in (r["about_product"] or "").lower()
                for w in kw
            )
        ]
    return results
