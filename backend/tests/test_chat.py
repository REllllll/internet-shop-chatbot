import json
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_db):
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    from app.main import app
    return TestClient(app)


def _mock_stream(text="What are you looking for?"):
    final_msg = MagicMock()
    final_msg.stop_reason = "end_turn"
    block = MagicMock()
    block.type = "text"
    block.text = text
    final_msg.content = [block]

    # Create stream object that is both iterable and has get_final_message
    stream_mock = MagicMock()
    stream_mock.__iter__ = MagicMock(return_value=iter([]))
    stream_mock.get_final_message = MagicMock(return_value=final_msg)
    
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=stream_mock)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx


def _mock_tool_stream(name, tool_input, text=None):
    final_msg = MagicMock()
    final_msg.stop_reason = "tool_use"
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = name
    tool_block.input = tool_input
    tool_block.id = "tool-1"
    final_msg.content = []
    if text is not None:
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = text
        final_msg.content.append(text_block)
    final_msg.content.append(tool_block)

    stream_mock = MagicMock()
    stream_mock.__iter__ = MagicMock(return_value=iter([]))
    stream_mock.get_final_message = MagicMock(return_value=final_msg)

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=stream_mock)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx


def test_chat_returns_sse_stream(client):
    with patch("app.chat.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.stream.return_value = _mock_stream()
        response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


def test_chat_sets_session_cookie(client):
    with patch("app.chat.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.stream.return_value = _mock_stream()
        response = client.post("/chat", json={"message": "hi"})
    # Check Set-Cookie header directly since httponly cookies don't appear in .cookies
    set_cookie = response.headers.get("set-cookie", "")
    assert "session_id" in set_cookie


def test_chat_accumulates_history_across_turns(client):
    with patch("app.chat.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.stream.return_value = _mock_stream("What's your budget?")
        r1 = client.post("/chat", json={"message": "I need a cable"})
        # Extract session_id from Set-Cookie header
        set_cookie = r1.headers.get("set-cookie", "")
        import re
        match = re.search(r'session_id=([^;]+)', set_cookie)
        assert match, f"No session_id found in Set-Cookie header: {set_cookie}"
        session_id = match.group(1)

        MockClient.return_value.messages.stream.return_value = _mock_stream("Here are my picks!")
        client.post("/chat", json={"message": "under 500"}, cookies={"session_id": session_id})

    # Second call's messages arg should contain the first user + assistant turn
    second_call_messages = MockClient.return_value.messages.stream.call_args_list[1][1]["messages"]
    assert len(second_call_messages) >= 2


def test_chat_retries_once_on_malformed_recommendation_tool_call(client):
    with patch("app.chat.anthropic.Anthropic") as MockClient, patch("app.chat.execute_tool") as mock_execute_tool:
        MockClient.return_value.messages.stream.side_effect = [
            _mock_tool_stream("get_recommendations", {"max_price": 500.0}),
            _mock_stream("Which category are you shopping for?"),
        ]

        response = client.post("/chat", json={"message": "under 500"})

    assert response.status_code == 200
    assert MockClient.return_value.messages.stream.call_count == 2
    assert "previous tool call was malformed" in MockClient.return_value.messages.stream.call_args_list[1][1]["system"]
    mock_execute_tool.assert_not_called()


def test_chat_surfaces_error_after_retry_budget_exhausted(client):
    with patch("app.chat.anthropic.Anthropic") as MockClient, patch("app.chat.execute_tool") as mock_execute_tool:
        MockClient.return_value.messages.stream.side_effect = [
            _mock_tool_stream("get_recommendations", {"max_price": 500.0}),
            _mock_tool_stream("get_recommendations", {"keywords": ["speaker"]}),
        ]

        response = client.post("/chat", json={"message": "under 500"})

    assert response.status_code == 200
    assert "tool formatting error" in response.text
    assert MockClient.return_value.messages.stream.call_count == 2
    mock_execute_tool.assert_not_called()


def test_chat_uses_provider_safe_history_after_tool_execution(client):
    with patch("app.chat.anthropic.Anthropic") as MockClient, patch("app.chat.execute_tool") as mock_execute_tool:
        mock_execute_tool.return_value = '[{"title":"USB-C Cable","discounted_price":299}]'
        MockClient.return_value.messages.stream.side_effect = [
            _mock_tool_stream("search_products", {"query": "usb c cable"}, text="I'll look that up."),
            _mock_stream("I found a USB-C cable for Rs. 299."),
        ]

        response = client.post("/chat", json={"message": "Find a usb c cable"})

    assert response.status_code == 200
    second_call_messages = MockClient.return_value.messages.stream.call_args_list[1][1]["messages"]
    assert second_call_messages[1] == {"role": "assistant", "content": "I'll look that up."}
    assert second_call_messages[2]["role"] == "user"
    assert second_call_messages[2]["content"] == (
        "Tool search_products returned JSON results for query {'query': 'usb c cable'}:\n"
        '[{"title":"USB-C Cable","discounted_price":299}]\n'
        "Use this data to answer the user directly, without calling another tool unless the user asks for a new lookup."
    )


def test_chat_keeps_recommendation_products_when_later_tool_does_ad_hoc_lookup(client):
    initial_payload = json.dumps({
        "products": [
            {
                "product_id": "B900",
                "product_name": "Earbud Tips",
                "category": "Electronics|Headphones,Earbuds&Accessories|Earpads",
                "discounted_price": 99.0,
                "actual_price": 199.0,
                "discount_percentage": 50.0,
                "rating": 3.8,
                "rating_count": 120,
                "about_product": "Replacement earbud tips",
                "img_link": "",
                "product_link": "https://amazon.in/B900",
            }
        ],
        "comparison": [
            {"attribute": "Price (₹)", "values": ["99"]},
            {"attribute": "Rating", "values": ["3.8"]},
            {"attribute": "Key Features", "values": ["Replacement earbud tips"]},
        ],
        "fallback": True,
    })
    refined_results = json.dumps([
        {
            "product_id": "B901",
            "product_name": "Commute Headphones",
            "category": "Electronics|Headphones,Earbuds&Accessories|Headphones",
            "discounted_price": 89.0,
            "actual_price": 149.0,
            "discount_percentage": 40.0,
            "rating": 4.4,
            "rating_count": 4200,
            "about_product": "Closed-back headphones for commuting and calls",
            "img_link": "",
            "product_link": "https://amazon.in/B901",
        }
    ])

    with patch("app.chat.anthropic.Anthropic") as MockClient, patch("app.chat.execute_tool") as mock_execute_tool:
        mock_execute_tool.side_effect = [initial_payload, refined_results]
        MockClient.return_value.messages.stream.side_effect = [
            _mock_tool_stream(
                "get_recommendations",
                {"category": "headphones", "max_price": 100.0},
                text="Here is an initial match.",
            ),
            _mock_tool_stream(
                "search_products",
                {"query": "commute headphones"},
                text="I found a better headphone match.",
            ),
            _mock_stream("These are better for your use case."),
        ]

        response = client.post("/chat", json={"message": "I need headphones under 100 for commuting"})

    assert response.status_code == 200
    assert response.text.count('"type": "products"') == 1
    assert "Earbud Tips" in response.text
    assert "Commute Headphones" not in response.text
