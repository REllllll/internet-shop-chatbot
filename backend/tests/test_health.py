import os

from fastapi.testclient import TestClient


def test_health_returns_ready_and_database_path(test_db):
    os.environ["ANTHROPIC_API_KEY"] = "test-key"

    from app.main import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database_path": test_db,
    }
