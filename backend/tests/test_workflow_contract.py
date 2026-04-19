import json
from pathlib import Path


def _load_workflow() -> dict:
    workflow_path = Path(__file__).parents[2] / "workflows" / "recommendation-pipeline.json"
    return json.loads(workflow_path.read_text())


def test_workflow_queries_backend_service_name():
    workflow = _load_workflow()
    query_products = next(node for node in workflow["nodes"] if node["name"] == "Query Products")
    assert query_products["parameters"]["url"] == "http://backend:8000/internal/products"


def test_workflow_builds_key_feature_comparison_rows():
    workflow = _load_workflow()
    build_comparison = next(node for node in workflow["nodes"] if node["name"] == "Build Comparison")
    code = build_comparison["parameters"]["jsCode"]

    assert "Key Features" in code
    # Comparison rows should not include reviews.
    assert "Reviews" not in code
