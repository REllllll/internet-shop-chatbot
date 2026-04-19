import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.mcp_tools import TOOL_SCHEMAS, execute_tool, recommendation_payload_from_tool_result


def test_tool_schemas_defines_three_tools():
    names = {t["name"] for t in TOOL_SCHEMAS}
    assert names == {"search_products", "filter_products", "get_recommendations"}


def test_search_products_returns_list(test_db):
    result = execute_tool("search_products", {"query": "lightning"})
    data = json.loads(result)
    assert isinstance(data, list)
    assert any(p["product_id"] == "B001" for p in data)


def test_filter_products_filters_by_price(test_db):
    result = execute_tool("filter_products", {"max_price": 3.0})
    data = json.loads(result)
    assert all(p["discounted_price"] <= 249.0 for p in data)
    assert [p["product_id"] for p in data] == ["B002"]


def test_filter_products_treats_max_price_as_usd(test_db):
    result = execute_tool("filter_products", {"max_price": 10.0})
    data = json.loads(result)
    assert [product["product_id"] for product in data] == ["B001", "B002"]


def test_get_recommendations_calls_n8n(test_db):
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({"products": [], "comparison": []})
    mock_resp.raise_for_status = MagicMock()
    with patch("app.mcp_tools.httpx.post", return_value=mock_resp) as mock_post, \
         patch.dict("os.environ", {}, clear=True):
        result = execute_tool("get_recommendations", {"category": "Electronics", "max_price": 2000.0})
        mock_post.assert_called_once()
        assert mock_post.call_args.args[0] == "http://127.0.0.1:5678/webhook/recommend"
        assert "products" in json.loads(result)


def test_get_recommendations_falls_back_when_n8n_down(test_db):
    with patch("app.mcp_tools.httpx.post", side_effect=httpx.RequestError("down")):
        result = execute_tool("get_recommendations", {"max_price": 30.0})
        data = json.loads(result)
        assert "products" in data
        assert data.get("fallback") is True
        assert len(data["products"]) == 3
        assert [row["attribute"] for row in data["comparison"]] == ["Price (₹)", "Rating", "Key Features"]
        assert all(row["values"] for row in data["comparison"])


def test_get_recommendations_fallback_returns_empty_payload_when_no_products(test_db):
    with patch("app.mcp_tools.httpx.post", side_effect=httpx.RequestError("down")):
        result = execute_tool(
            "get_recommendations",
            {"category": "Computers&Accessories", "max_price": 0.1, "keywords": ["nonexistent"]},
        )
    data = json.loads(result)
    assert data == {"products": [], "comparison": [], "fallback": True, "empty": True}


def test_get_recommendations_fallback_prefers_keyword_matches(test_db):
    with patch("app.mcp_tools.httpx.post", side_effect=httpx.RequestError("down")):
        result = execute_tool(
            "get_recommendations",
            {"category": "Computers&Accessories", "max_price": 10.0, "keywords": ["lightning", "iphone", "cable"]},
        )
    data = json.loads(result)
    assert [product["product_id"] for product in data["products"]] == ["B001", "B002"]


def test_get_recommendations_falls_back_when_n8n_results_do_not_match_keywords(test_db):
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "products": [
            {
                "product_id": "B001",
                "product_name": "USB Cable Lightning",
                "category": "Computers&Accessories|Cables",
                "discounted_price": 399.0,
                "actual_price": 1099.0,
                "discount_percentage": 64.0,
                "rating": 4.2,
                "rating_count": 24269,
                "about_product": "Fast charging lightning cable compatible with bluetooth speakers",
                "img_link": "",
                "product_link": "https://amazon.in/B001",
            }
        ],
        "comparison": [],
    })
    mock_resp.raise_for_status = MagicMock()

    with patch("app.mcp_tools.httpx.post", return_value=mock_resp):
        result = execute_tool(
            "get_recommendations",
            {"category": "Electronics", "max_price": 30.0, "min_rating": 4.0, "keywords": ["speaker"], "use_case": "travel"},
        )

    data = json.loads(result)
    assert data["fallback"] is False
    assert data["products"][0]["product_id"] == "B003"


def test_unknown_tool_returns_error(test_db):
    data = json.loads(execute_tool("bogus", {}))
    assert "error" in data


def test_recommendation_payload_from_search_results_is_not_promoted(test_db):
    search_results = json.dumps([
        {
            "product_id": "B001",
            "product_name": "USB Cable Lightning",
            "category": "Computers&Accessories|Cables",
            "discounted_price": 399.0,
            "actual_price": 1099.0,
            "discount_percentage": 64.0,
            "rating": 4.2,
            "rating_count": 24269,
            "about_product": "Fast charging lightning cable",
            "img_link": "",
            "product_link": "https://amazon.in/B001",
        },
        {
            "product_id": "B002",
            "product_name": "USB-C Cable Android",
            "category": "Computers&Accessories|Cables",
            "discounted_price": 199.0,
            "actual_price": 349.0,
            "discount_percentage": 43.0,
            "rating": 4.0,
            "rating_count": 43994,
            "about_product": "Nylon braided USB-C charging cable",
            "img_link": "",
            "product_link": "https://amazon.in/B002",
        },
    ])

    payload = recommendation_payload_from_tool_result("search_products", search_results)

    assert payload is None
