import json
import re
from pathlib import Path


def _load_workflow() -> dict:
    workflow_path = Path(__file__).parents[2] / "workflows" / "recommendation-pipeline.json"
    return json.loads(workflow_path.read_text())


def test_workflow_queries_local_backend_url():
    workflow = _load_workflow()
    query_products = next(node for node in workflow["nodes"] if node["name"] == "Query Products")
    assert query_products["parameters"]["url"] == "http://127.0.0.1:8000/internal/products"


def test_workflow_builds_key_feature_comparison_rows():
    workflow = _load_workflow()
    build_comparison = next(node for node in workflow["nodes"] if node["name"] == "Build Comparison")
    code = build_comparison["parameters"]["jsCode"]

    attributes = re.findall(r"attribute: '([^']+)'", code)

    assert attributes == ["Price (₹)", "Rating", "Discount", "Key Features"]
    assert "Reviews" not in code


def test_workflow_ranks_all_query_product_items():
    workflow = _load_workflow()
    rank_products = next(node for node in workflow["nodes"] if node["name"] == "Rank Products")
    code = rank_products["parameters"]["jsCode"]

    assert "$input.all().map(item => item.json)" in code


def test_workflow_query_products_reads_filters_from_webhook_body():
    workflow = _load_workflow()
    query_products = next(node for node in workflow["nodes"] if node["name"] == "Query Products")
    params = query_products["parameters"]["queryParameters"]["parameters"]

    values_by_name = {param["name"]: param["value"] for param in params}

    assert values_by_name["category"] == "={{ $json.body.category }}"
    assert values_by_name["max_price"] == "={{ $json.body.max_price }}"
    assert values_by_name["min_rating"] == "={{ $json.body.min_rating }}"
    assert values_by_name["keywords"] == "={{ ($json.body.keywords || []).join(',') }}"


def test_workflow_rank_products_reads_keywords_from_webhook_body():
    workflow = _load_workflow()
    rank_products = next(node for node in workflow["nodes"] if node["name"] == "Rank Products")
    code = rank_products["parameters"]["jsCode"]

    assert "$('Webhook').first().json.body" in code
