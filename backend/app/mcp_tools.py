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
                "max_price": {"type": "number", "description": "Maximum discounted price in INR"},
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


def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_products":
        return json.dumps(db.search_products(tool_input["query"]))

    if tool_name == "filter_products":
        return json.dumps(
            db.filter_products(
                category=tool_input.get("category"),
                max_price=tool_input.get("max_price"),
                min_rating=tool_input.get("min_rating"),
            )
        )

    if tool_name == "get_recommendations":
        n8n_url = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/recommend")
        try:
            resp = httpx.post(n8n_url, json=tool_input, timeout=5.0)
            resp.raise_for_status()
            return resp.text
        except (httpx.RequestError, httpx.HTTPStatusError):
            # n8n unavailable - query DB directly (not a fallback, just direct access)
            results = db.filter_products(
                category=tool_input.get("category"),
                max_price=tool_input.get("max_price"),
                min_rating=tool_input.get("min_rating"),
                keywords=tool_input.get("keywords"),
            )
            return json.dumps({"products": results[:5], "comparison": [], "fallback": False})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
