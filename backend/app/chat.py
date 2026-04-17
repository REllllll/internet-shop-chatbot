import json
import os
import uuid
from dataclasses import dataclass, field

import anthropic
from fastapi import APIRouter, Cookie, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .mcp_tools import TOOL_SCHEMAS, execute_tool

router = APIRouter()

SYSTEM_PROMPT = """You are ShopBot, a helpful assistant for an Amazon product catalog (global market, prices in USD).

Rules:
- Ask one clarifying question at a time (max 5 questions total before recommending)
- Gather: product category, budget in USD, use case, minimum acceptable rating
- Once you have category + at least one of (budget / use_case / keywords): call get_recommendations
- Use search_products or filter_products ONLY for ad-hoc mid-conversation lookups
- After get_recommendations returns products, explain WHY each matches the user's needs
- Mention price, rating, and key trade-offs in your explanation
- Keep responses concise (under 150 words per message)"""


@dataclass
class ConversationSession:
    session_id: str
    messages: list[dict] = field(default_factory=list)


_sessions: dict[str, ConversationSession] = {}


class ChatRequest(BaseModel):
    message: str


def _get_or_create_session(session_id: str | None) -> ConversationSession:
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    sid = session_id or str(uuid.uuid4())
    session = ConversationSession(session_id=sid)
    _sessions[sid] = session
    return session


def _stream_response(session: ConversationSession, user_message: str):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    session.messages.append({"role": "user", "content": user_message})

    while True:
        with client.messages.stream(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=session.messages,
        ) as stream:
            for event in stream:
                if (
                    hasattr(event, "type")
                    and event.type == "content_block_delta"
                    and hasattr(event.delta, "text")
                ):
                    yield f"data: {json.dumps({'type': 'text', 'content': event.delta.text})}\n\n"

            final = stream.get_final_message()

        session.messages.append({"role": "assistant", "content": final.content})

        if final.stop_reason != "tool_use":
            break

        tool_results = []
        for block in final.content:
            if block.type == "tool_use":
                yield f"data: {json.dumps({'type': 'tool_call', 'tool': block.name})}\n\n"
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
                if block.name == "get_recommendations":
                    try:
                        yield f"data: {json.dumps({'type': 'products', 'data': json.loads(result)})}\n\n"
                    except json.JSONDecodeError:
                        pass

        session.messages.append({"role": "user", "content": tool_results})

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@router.post("/chat")
def chat(
    request: ChatRequest,
    session_id: str | None = Cookie(default=None),
):
    session = _get_or_create_session(session_id)
    streaming_response = StreamingResponse(
        _stream_response(session, request.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
    streaming_response.set_cookie("session_id", session.session_id, httponly=True, samesite="lax")
    return streaming_response
