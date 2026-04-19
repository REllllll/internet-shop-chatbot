import json
import re
from pathlib import Path


def _load_workflow() -> dict:
    workflow_path = Path(__file__).parents[2] / "workflows" / "recommendation-pipeline.json"
    return json.loads(workflow_path.read_text())


def test_workflow_builds_key_feature_comparison_rows():
    workflow = _load_workflow()
    build_comparison = next(node for node in workflow["nodes"] if node["name"] == "Build Comparison")
    code = build_comparison["parameters"]["jsCode"]

    attributes = re.findall(r"attribute: '([^']+)'", code)

    assert attributes == ["Price (₹)", "Rating", "Discount", "Key Features"]
    assert "Reviews" not in code
