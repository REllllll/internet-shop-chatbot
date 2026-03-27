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
