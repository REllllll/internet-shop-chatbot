import os
import re
import sqlite3
from math import log
from contextlib import contextmanager
from pathlib import Path

USD_TO_INR = 83.0


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


def _normalize_fts_query(query: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", query or "")
    if not tokens:
        return ""
    return " AND ".join(f'"{token}"' for token in tokens)


def usd_to_inr(amount: float | None) -> float | None:
    if amount is None:
        return None
    return round(amount * USD_TO_INR, 2)


def tokenize_query_parts(*parts: str | None) -> list[str]:
    tokens: list[str] = []
    for part in parts:
        tokens.extend(token.lower() for token in re.findall(r"[A-Za-z0-9]+", part or ""))
    seen: set[str] = set()
    deduped: list[str] = []
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        deduped.append(token)
    return deduped


def search_products(query: str, limit: int = 20) -> list[dict]:
    normalized_query = _normalize_fts_query(query)
    if not normalized_query:
        return []

    with get_db() as conn:
        rows = conn.execute(
            """SELECT p.* FROM products p
               JOIN products_fts fts ON p.product_id = fts.product_id
               WHERE products_fts MATCH ?
               LIMIT ?""",
            (normalized_query, limit),
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


def rank_products(
    products: list[dict],
    *,
    category: str | None = None,
    keywords: list[str] | None = None,
    use_case: str | None = None,
) -> list[dict]:
    terms = tokenize_query_parts(*(keywords or []), use_case)
    category_text = (category or "").lower()

    def score(product: dict) -> float:
        haystack_name = (product.get("product_name") or "").lower()
        haystack_about = (product.get("about_product") or "").lower()
        haystack_category = (product.get("category") or "").lower()

        match_score = 0.0
        if category_text:
            if haystack_category.startswith(category_text):
                match_score += 8.0
            elif category_text in haystack_category:
                match_score += 4.0

        for term in terms:
            in_name = term in haystack_name
            in_about = term in haystack_about
            in_category = term in haystack_category
            if in_name:
                match_score += 6.0
            if in_about:
                match_score += 3.0
            if in_category:
                match_score += 1.5

        rating = product.get("rating") or 0.0
        rating_count = product.get("rating_count") or 0
        popularity_score = rating + log(rating_count + 1)
        return match_score * 10 + popularity_score

    return sorted(products, key=score, reverse=True)
