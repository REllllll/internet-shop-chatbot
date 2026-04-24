import json
import pytest
import httpx


class TestN8NIntegration:
    @pytest.mark.asyncio
    async def test_n8n_webhook_endpoint(self):
        """Test that n8n webhook is accessible and returns valid response"""
        payload = {
            "category": "Electronics",
            "max_price": 100,
            "min_rating": 4.0,
            "keywords": ["cable"],
            "use_case": "charging"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:5678/webhook/recommend",
                    json=payload,
                    timeout=10.0
                )
                assert response.status_code == 200
                data = response.json()
                assert "products" in data or "ranked" in data
        except httpx.ConnectError:
            pytest.skip("n8n service not running")

    def test_backend_calls_n8n(self):
        """Test that backend can call n8n workflow"""
        from app.mcp_tools import execute_tool
        
        result = execute_tool("get_recommendations", {
            "category": "Electronics",
            "max_price": 50,
            "keywords": ["usb"]
        })
        
        data = json.loads(result)
        assert "products" in data
        assert isinstance(data["products"], list)
