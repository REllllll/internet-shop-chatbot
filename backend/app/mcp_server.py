import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

from app import db

mcp = FastMCP("shopbot-mcp")


def _extract_key_features(product: dict, limit: int = 3) -> str:
    raw_features = (product.get("about_product") or "").split("|")
    cleaned = [feature.strip() for feature in raw_features if feature.strip()]
    return " | ".join(cleaned[:limit]) or "N/A"


def _build_comparison(products: list[dict]) -> list[dict]:
    top3 = products[:3]
    return [
        {
            "attribute": "Price",
            "values": [
                f"{p.get('discounted_price'):.2f}"
                if p.get("discounted_price") is not None
                else "N/A"
                for p in top3
            ],
        },
        {
            "attribute": "Rating",
            "values": [
                f"{p.get('rating'):.1f}"
                if p.get("rating") is not None
                else "N/A"
                for p in top3
            ],
        },
        {
            "attribute": "Key Features",
            "values": [_extract_key_features(p) for p in top3],
        },
    ]


@mcp.tool()
def search_products(query: str) -> str:
    """Full-text search for products by name or description.

    Use for ad-hoc lookups mid-conversation (e.g. 'do you have waterproof options?').
    """
    return json.dumps(db.search_products(query))


@mcp.tool()
def filter_products(
    category: str | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
) -> str:
    """Filter products by category, max price, and minimum rating.

    Use for ad-hoc lookups.
    """
    return json.dumps(
        db.filter_products(
            category=category,
            max_price=max_price,
            min_rating=min_rating,
        )
    )


@mcp.tool()
def get_recommendations(
    category: str,
    max_price: float | None = None,
    min_rating: float | None = None,
    keywords: list[str] | None = None,
    use_case: str | None = None,
) -> str:
    """Get final personalized product recommendations via the ranking pipeline.

    Call ONLY after eliciting category + at least one of (max_price, use_case,
    keywords). Do NOT call for exploratory questions.
    """
    n8n_url = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/recommend")
    payload = {
        "category": category,
        "max_price": max_price,
        "min_rating": min_rating,
        "keywords": keywords or [],
        "use_case": use_case,
    }
    try:
        resp = httpx.post(n8n_url, json=payload, timeout=5.0)
        resp.raise_for_status()
        return resp.text
    except (httpx.RequestError, httpx.HTTPStatusError):
        results = db.filter_products(
            category=category,
            max_price=max_price,
            min_rating=min_rating,
            keywords=keywords,
        )
        top3 = results[:3]
        return json.dumps(
            {"products": top3, "comparison": _build_comparison(top3), "fallback": True}
        )


if __name__ == "__main__":
    mcp.run(transport="stdio")
