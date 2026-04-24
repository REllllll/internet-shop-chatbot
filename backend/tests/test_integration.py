import json
import os
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_anthropic():
    with patch("app.chat.anthropic.Anthropic") as mock:
        yield mock


class TestInternalAPI:
    def test_get_products_with_category(self, client):
        response = client.get("/internal/products?category=Electronics&limit=5")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) <= 5
        if products:
            assert "product_id" in products[0]
            assert "product_name" in products[0]

    def test_get_products_with_price_filter(self, client):
        response = client.get("/internal/products?max_price=5&limit=10")
        assert response.status_code == 200
        products = response.json()
        for product in products:
            price = product.get("discounted_price")
            if price is not None:
                assert price <= 415

    def test_get_products_with_rating_filter(self, client):
        response = client.get("/internal/products?min_rating=4.0&limit=10")
        assert response.status_code == 200
        products = response.json()
        for product in products:
            rating = product.get("rating")
            if rating is not None:
                assert rating >= 4.0

    def test_get_products_with_keywords(self, client):
        response = client.get("/internal/products?keywords=cable,usb&limit=10")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)


class TestDatabaseQueries:
    def test_search_products(self):
        results = db.search_products("laptop", limit=5)
        assert isinstance(results, list)
        assert len(results) <= 5

    def test_filter_products_by_category(self):
        results = db.filter_products(category="Electronics", limit=10)
        assert isinstance(results, list)
        for product in results:
            assert product["category"].startswith("Electronics")
