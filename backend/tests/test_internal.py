import os
import importlib

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
    response = client.get("/internal/products?max_price=3")
    assert all(p["discounted_price"] <= 249.0 for p in response.json())


def test_internal_products_filter_by_keywords(client):
    response = client.get("/internal/products?keywords=speaker")
    data = response.json()
    assert len(data) == 1
    assert data[0]["product_id"] == "B003"


def test_internal_products_filter_by_multiple_keywords(client):
    response = client.get("/internal/products?keywords=cable,lightning")
    data = response.json()
    assert any(p["product_id"] == "B001" for p in data)


def test_cors_allows_loopback_frontend_origin(client):
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_cors_uses_configured_origins(monkeypatch, test_db):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://example.com")

    import app.main

    module = importlib.reload(app.main)
    client = TestClient(module.app)
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://example.com"
