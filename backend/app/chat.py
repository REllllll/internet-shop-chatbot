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

MALFORMED_TOOL_RETRY_PROMPT = (
    "Your previous tool call was malformed. "
    "Only call get_recommendations when category and at least one of "
    "(max_price, use_case, keywords) are present. "
    "If that information is missing, ask one clarifying question instead."
)
MALFORMED_TOOL_ERROR = (
    "I hit a tool formatting error while preparing recommendations. "
    "Please restate your request with a product category and one preference such as budget, use case, or keywords."
)


class ChatRequest(BaseModel):
    message: str


class MalformedToolCallError(ValueError):
    pass


def _extract_text_content(blocks) -> str:
    texts = []
    for block in blocks:
        if getattr(block, "type", None) == "text" and getattr(block, "text", None):
            texts.append(block.text.strip())
    return " ".join(text for text in texts if text)


def _format_tool_result_message(tool_name: str, tool_input: dict, result: str) -> str:
    return (
        f"Tool {tool_name} returned JSON results for query {tool_input}:\n"
        f"{result}\n"
        "Use this data to answer the user directly, without calling another tool unless the user asks for a new lookup."
    )


def _get_or_create_session(session_id: str | None) -> ConversationSession:
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    sid = session_id or str(uuid.uuid4())
    session = ConversationSession(session_id=sid)
    _sessions[sid] = session
    return session


def _is_valid_recommendation_request(tool_input: dict) -> bool:
    if not isinstance(tool_input, dict):
        return False
    if not tool_input.get("category"):
        return False
    return any(tool_input.get(field) for field in ("max_price", "use_case", "keywords"))


def _validate_tool_call(tool_name: str, tool_input: dict) -> None:
    if tool_name == "get_recommendations" and not _is_valid_recommendation_request(tool_input):
        raise MalformedToolCallError("get_recommendations requires category plus one additional preference")


def _stream_response(session: ConversationSession, user_message: str):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    session.messages.append({"role": "user", "content": user_message})
    retry_instruction = ""
    retries = 0

    while True:
        with client.messages.stream(
            model=model,
            max_tokens=1024,
            system=f"{SYSTEM_PROMPT}\n\n{retry_instruction}".strip(),
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

        if final.stop_reason != "tool_use":
            session.messages.append({"role": "assistant", "content": final.content})
            break

        try:
            for block in final.content:
                if block.type == "tool_use":
                    _validate_tool_call(block.name, block.input)
        except MalformedToolCallError:
            if retries < 1:
                retries += 1
                retry_instruction = MALFORMED_TOOL_RETRY_PROMPT
                continue

            yield f"data: {json.dumps({'type': 'text', 'content': MALFORMED_TOOL_ERROR})}\n\n"
            session.messages.append({"role": "assistant", "content": MALFORMED_TOOL_ERROR})
            break

        retry_instruction = ""
        assistant_text = _extract_text_content(final.content)
        if assistant_text:
            session.messages.append({"role": "assistant", "content": assistant_text})

        tool_result_messages = []
        for block in final.content:
            if block.type == "tool_use":
                yield f"data: {json.dumps({'type': 'tool_call', 'tool': block.name})}\n\n"
                result = execute_tool(block.name, block.input)
                tool_result_messages.append(_format_tool_result_message(block.name, block.input, result))
                if block.name == "get_recommendations":
                    try:
                        yield f"data: {json.dumps({'type': 'products', 'data': json.loads(result)})}\n\n"
                    except json.JSONDecodeError:
                        pass

        if tool_result_messages:
            session.messages.append({"role": "user", "content": "\n\n".join(tool_result_messages)})

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
