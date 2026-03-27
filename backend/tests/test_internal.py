import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_db):
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    from app.main import app
    return TestClient(app)


def test_internal_products_returns_list(client):
    response = client.get("/internal/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_internal_products_filter_by_category(client):
    response = client.get("/internal/products?category=Electronics")
    assert response.status_code == 200
    assert all("Electronics" in p["category"] for p in response.json())


def test_internal_products_filter_by_max_price(client):
    response = client.get("/internal/products?max_price=400")
    assert all(p["discounted_price"] <= 400.0 for p in response.json())


def test_internal_products_filter_by_keywords(client):
    response = client.get("/internal/products?keywords=speaker")
    data = response.json()
    assert len(data) == 1
    assert data[0]["product_id"] == "B003"


def test_internal_products_filter_by_multiple_keywords(client):
    response = client.get("/internal/products?keywords=cable,lightning")
    data = response.json()
    assert any(p["product_id"] == "B001" for p in data)
