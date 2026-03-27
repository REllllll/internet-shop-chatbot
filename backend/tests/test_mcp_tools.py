import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.mcp_tools import TOOL_SCHEMAS, execute_tool


def test_tool_schemas_defines_three_tools():
    names = {t["name"] for t in TOOL_SCHEMAS}
    assert names == {"search_products", "filter_products", "get_recommendations"}


def test_search_products_returns_list(test_db):
    result = execute_tool("search_products", {"query": "lightning"})
    data = json.loads(result)
    assert isinstance(data, list)
    assert any(p["product_id"] == "B001" for p in data)


def test_filter_products_filters_by_price(test_db):
    result = execute_tool("filter_products", {"max_price": 300.0})
    data = json.loads(result)
    assert all(p["discounted_price"] <= 300.0 for p in data)


def test_get_recommendations_calls_n8n(test_db):
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({"products": [], "comparison": []})
    mock_resp.raise_for_status = MagicMock()
    with patch("app.mcp_tools.httpx.post", return_value=mock_resp) as mock_post:
        result = execute_tool("get_recommendations", {"category": "Electronics", "max_price": 2000.0})
        mock_post.assert_called_once()
        assert "products" in json.loads(result)


def test_get_recommendations_falls_back_when_n8n_down(test_db):
    with patch("app.mcp_tools.httpx.post", side_effect=httpx.RequestError("down")):
        result = execute_tool("get_recommendations", {"max_price": 500.0})
        data = json.loads(result)
        assert "products" in data
        assert data.get("fallback") is True


def test_unknown_tool_returns_error(test_db):
    data = json.loads(execute_tool("bogus", {}))
    assert "error" in data
