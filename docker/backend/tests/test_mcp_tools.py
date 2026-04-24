import json
import pytest
from app.mcp_tools import execute_tool, _build_comparison, _extract_key_features


class TestMCPTools:
    def test_search_products_tool(self):
        result = execute_tool("search_products", {"query": "laptop"})
        data = json.loads(result)
        assert isinstance(data, list)

    def test_filter_products_tool(self):
        result = execute_tool("filter_products", {
            "category": "Electronics",
            "max_price": 100,
            "min_rating": 4.0
        })
        data = json.loads(result)
        assert isinstance(data, list)

    def test_get_recommendations_fallback(self):
        result = execute_tool("get_recommendations", {
            "category": "Electronics",
            "max_price": 50,
            "keywords": ["cable"]
        })
        data = json.loads(result)
        assert "products" in data
        assert "comparison" in data
        assert isinstance(data["products"], list)

    def test_extract_key_features(self):
        product = {
            "about_product": "Feature 1 | Feature 2 | Feature 3 | Feature 4"
        }
        result = _extract_key_features(product, limit=3)
        assert result == "Feature 1 | Feature 2 | Feature 3"

    def test_extract_key_features_empty(self):
        product = {"about_product": ""}
        result = _extract_key_features(product)
        assert result == "N/A"

    def test_build_comparison(self):
        products = [
            {"discounted_price": 25.5, "rating": 4.5, "about_product": "Feature A"},
            {"discounted_price": 30.0, "rating": 4.0, "about_product": "Feature B"},
            {"discounted_price": None, "rating": None, "about_product": ""}
        ]
        comparison = _build_comparison(products)
        assert len(comparison) == 3
        assert comparison[0]["attribute"] == "Price (₹)"
        assert comparison[1]["attribute"] == "Rating"
        assert comparison[2]["attribute"] == "Key Features"
        assert len(comparison[0]["values"]) == 3
