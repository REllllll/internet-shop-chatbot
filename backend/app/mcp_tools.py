import json
import os

import httpx

from . import db

TOOL_SCHEMAS = [
    {
        "name": "search_products",
        "description": (
            "Full-text search for products by name or description. "
            "Use for ad-hoc lookups mid-conversation (e.g. 'do you have waterproof options?')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "filter_products",
        "description": "Filter products by category, max price, and minimum rating. Use for ad-hoc lookups.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Category prefix, e.g. 'Computers&Accessories'"},
                "max_price": {"type": "number", "description": "Maximum discounted price in USD"},
                "min_rating": {"type": "number", "description": "Minimum rating 0–5"},
            },
        },
    },
    {
        "name": "get_recommendations",
        "description": (
            "Get final personalized product recommendations via the ranking pipeline. "
            "Call ONLY after eliciting category + at least one of (max_price, use_case, keywords). "
            "Do NOT call for exploratory questions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "max_price": {"type": "number"},
                "min_rating": {"type": "number"},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "use_case": {"type": "string"},
            },
        },
    },
]


def _empty_recommendation_payload(*, fallback: bool) -> dict:
    return {
        "products": [],
        "comparison": [],
        "fallback": fallback,
        "empty": True,
    }


def _extract_key_features(product: dict, limit: int = 3) -> str:
    raw_features = (product.get("about_product") or "").split("|")
    cleaned = [feature.strip() for feature in raw_features if feature.strip()]
    return " | ".join(cleaned[:limit]) or "N/A"


def _build_comparison(products: list[dict]) -> list[dict]:
    top3 = products[:3]
    if not top3:
        return []
    return [
        {
            "attribute": "Price (₹)",
            "values": [f"{p.get('discounted_price'):.0f}" if p.get("discounted_price") is not None else "N/A" for p in top3],
        },
        {
            "attribute": "Rating",
            "values": [f"{p.get('rating'):.1f}" if p.get("rating") is not None else "N/A" for p in top3],
        },
        {
            "attribute": "Key Features",
            "values": [_extract_key_features(p) for p in top3],
        },
    ]


def _promote_product_list_to_recommendations(products: list[dict]) -> dict | None:
    if not isinstance(products, list):
        return None
    if not products:
        return _empty_recommendation_payload(fallback=True)

    top3 = [product for product in products[:3] if isinstance(product, dict)]
    if not top3:
        return _empty_recommendation_payload(fallback=True)

    return {
        "products": top3,
        "comparison": _build_comparison(top3),
        "fallback": True,
    }


def recommendation_payload_from_tool_result(tool_name: str, result: str) -> dict | None:
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        return None

    if tool_name != "get_recommendations":
        return None

    if isinstance(parsed, dict) and isinstance(parsed.get("products"), list) and isinstance(parsed.get("comparison"), list):
        if not parsed.get("products"):
            return _empty_recommendation_payload(fallback=bool(parsed.get("fallback")))
        return parsed

    return None


def _dedupe_products(products: list[dict]) -> list[dict]:
    deduped: list[dict] = []
    seen: set[str] = set()
    for product in products:
        product_id = product.get("product_id")
        if not product_id or product_id in seen:
            continue
        seen.add(product_id)
        deduped.append(product)
    return deduped


def _apply_filters(
    products: list[dict],
    *,
    max_price: float | None,
    min_rating: float | None,
) -> list[dict]:
    filtered: list[dict] = []
    for product in products:
        price = product.get("discounted_price")
        rating = product.get("rating")
        if max_price is not None and price is not None and price > max_price:
            continue
        if min_rating is not None and rating is not None and rating < min_rating:
            continue
        filtered.append(product)
    return filtered


def _fallback_recommendations(tool_input: dict) -> dict:
    return _backend_recommendations(tool_input, fallback=True)


def _backend_recommendations(tool_input: dict, *, fallback: bool) -> dict:
    max_price_inr = db.usd_to_inr(tool_input.get("max_price"))
    keywords = tool_input.get("keywords") or []
    min_rating = tool_input.get("min_rating")
    category = tool_input.get("category")
    use_case = tool_input.get("use_case")

    category_candidates = db.filter_products(
        category=category,
        max_price=max_price_inr,
        min_rating=min_rating,
        limit=200,
    )

    search_candidates: list[dict] = []
    if keywords:
        search_candidates = _apply_filters(
            db.search_products(" ".join(keywords), limit=200),
            max_price=max_price_inr,
            min_rating=min_rating,
        )

    candidates = _dedupe_products(category_candidates + search_candidates)
    ranked = db.rank_products(
        candidates,
        category=category,
        keywords=keywords,
        use_case=use_case,
    )
    top3 = ranked[:3]
    if not top3:
        return _empty_recommendation_payload(fallback=fallback)
    return {"products": top3, "comparison": _build_comparison(top3), "fallback": fallback}


def _keyword_terms(tool_input: dict) -> list[str]:
    return db.tokenize_query_parts(*(tool_input.get("keywords") or []))


def _product_matches_requested_keywords(product: dict, keyword_terms: list[str]) -> bool:
    if not keyword_terms:
        return True

    haystack_name = (product.get("product_name") or "").lower()
    haystack_category = (product.get("category") or "").lower()
    return any(term in haystack_name or term in haystack_category for term in keyword_terms)


def _product_category_matches_keywords(product: dict, keyword_terms: list[str]) -> bool:
    if not keyword_terms:
        return True
    haystack_category = (product.get("category") or "").lower()
    return any(term in haystack_category for term in keyword_terms)


def _pipeline_response_looks_relevant(payload: dict, tool_input: dict) -> bool:
    products = payload.get("products")
    if not isinstance(products, list) or not products:
        return True

    keyword_terms = _keyword_terms(tool_input)
    if not keyword_terms:
        return True

    return any(
        isinstance(product, dict) and _product_matches_requested_keywords(product, keyword_terms)
        for product in products
    )


def _should_replace_pipeline_results(payload: dict, tool_input: dict) -> bool:
    keyword_terms = _keyword_terms(tool_input)
    if not keyword_terms:
        return False

    products = payload.get("products")
    if not isinstance(products, list) or not products or not isinstance(products[0], dict):
        return False

    backend_payload = _backend_recommendations(tool_input, fallback=False)
    backend_products = backend_payload.get("products")
    if not isinstance(backend_products, list) or not backend_products or not isinstance(backend_products[0], dict):
        return False

    pipeline_top = products[0]
    backend_top = backend_products[0]
    return (
        _product_category_matches_keywords(backend_top, keyword_terms)
        and not _product_category_matches_keywords(pipeline_top, keyword_terms)
    )


def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_products":
        return json.dumps(db.search_products(tool_input["query"]))

    if tool_name == "filter_products":
        return json.dumps(
            db.filter_products(
                category=tool_input.get("category"),
                max_price=db.usd_to_inr(tool_input.get("max_price")),
                min_rating=tool_input.get("min_rating"),
            )
        )

    if tool_name == "get_recommendations":
        n8n_url = os.getenv("N8N_WEBHOOK_URL", "http://127.0.0.1:5678/webhook/recommend")
        try:
            resp = httpx.post(n8n_url, json=tool_input, timeout=5.0)
            resp.raise_for_status()
            parsed = json.loads(resp.text)
            if (
                isinstance(parsed, dict)
                and isinstance(parsed.get("products"), list)
                and isinstance(parsed.get("comparison"), list)
            ):
                if (
                    not _pipeline_response_looks_relevant(parsed, tool_input)
                    or _should_replace_pipeline_results(parsed, tool_input)
                ):
                    return json.dumps(_backend_recommendations(tool_input, fallback=False))
                return json.dumps(parsed)
            return json.dumps(_fallback_recommendations(tool_input))
        except (httpx.RequestError, httpx.HTTPStatusError):
            return json.dumps(_fallback_recommendations(tool_input))
        except json.JSONDecodeError:
            return json.dumps(_fallback_recommendations(tool_input))

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
