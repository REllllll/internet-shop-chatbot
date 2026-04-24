# Chat Recommendation Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the n8n recommendation workflow and make later tool results able to replace stale recommendations in the chat UI.

**Architecture:** Repair the workflow at the source by ranking all incoming n8n items instead of a single object. In parallel, normalize recommendation-capable tool results in the backend into one SSE payload shape so the frontend can update the recommendation panel whenever a better product set arrives later in the same conversation.

**Tech Stack:** FastAPI, Anthropic streaming API, React 19, Vite, Vitest, n8n webhook workflow, Docker Compose

---

### Task 1: Repair the n8n ranking workflow

**Files:**
- Modify: `workflows/recommendation-pipeline.json`

- [ ] **Step 1: Write the failing workflow verification command**

Run:

```bash
curl -i -sS -X POST http://localhost:5678/webhook/recommend \
  -H 'Content-Type: application/json' \
  --data '{"category":"Electronics","max_price":100,"keywords":["cable"],"use_case":"charging"}'
```

Expected before the fix: `HTTP/1.1 500 Internal Server Error` with `{"message":"Error in workflow"}`.

- [ ] **Step 2: Update the workflow to rank all input items**

Replace the `Rank Products` JavaScript so it starts from:

```javascript
const products = $input.all().map(item => item.json);
```

and keeps the rest of the scoring logic on that array.

- [ ] **Step 3: Re-run the webhook verification**

Run the same `curl` command again.

Expected after the fix: `HTTP/1.1 200 OK` and JSON containing `products` and `comparison`.

### Task 2: Normalize recommendation updates from tool results

**Files:**
- Modify: `backend/app/mcp_tools.py`
- Modify: `backend/app/chat.py`
- Test: `backend/tests/test_chat.py`

- [ ] **Step 1: Write a failing backend test for recovery-tool recommendation updates**

Add a test in `backend/tests/test_chat.py` that mocks:

1. First Claude response: `get_recommendations` tool use returning a bad recommendation set.
2. Second Claude response: `search_products` or `filter_products` tool use returning a better product list.
3. Third Claude response: normal assistant text ending the turn.

Assert the streamed response contains two recommendation update payloads and that the later one reflects the recovery-tool results.

- [ ] **Step 2: Run the failing backend test**

Run:

```bash
. .venv/bin/activate && PYTHONPATH=backend pytest backend/tests/test_chat.py -k recommendation_update -v
```

Expected before the fix: the new test fails because only `get_recommendations` emits recommendation data.

- [ ] **Step 3: Implement backend normalization**

In `backend/app/mcp_tools.py`, add helper(s) that:

```python
def recommendation_payload_from_tool_result(tool_name: str, result: str) -> dict | None:
    ...
```

Behavior:

- `get_recommendations`: return parsed payload when it already has `products` and `comparison`.
- `search_products` / `filter_products`: if parsed JSON is a non-empty list of products, convert the first three products into:

```python
{
    "products": top3,
    "comparison": _build_comparison(top3),
    "fallback": True,
}
```

Then in `backend/app/chat.py`, replace the hard-coded `if block.name == "get_recommendations": ...` branch with the helper so any recommendation-capable tool result emits the same SSE event.

- [ ] **Step 4: Re-run the backend test**

Run:

```bash
. .venv/bin/activate && PYTHONPATH=backend pytest backend/tests/test_chat.py -k recommendation_update -v
```

Expected after the fix: PASS.

### Task 3: Make the frontend consume replacement recommendation updates

**Files:**
- Modify: `frontend/src/hooks/useChat.ts`
- Modify: `frontend/src/types.ts` if needed
- Test: `frontend/src/__tests__/useChat.test.ts`

- [ ] **Step 1: Write the failing frontend hook test**

Add a test that streams two recommendation update events in one conversation attempt and asserts the hook ends with the later payload in `recommendations`.

- [ ] **Step 2: Run the failing frontend test**

Run:

```bash
cd frontend && npm test -- --run useChat.test.ts
```

Expected before the fix: the new test fails if the hook is still keyed only to the old event contract.

- [ ] **Step 3: Update the hook to consume normalized recommendation events**

Keep the current text streaming behavior. Update the event handling so the hook sets recommendation state whenever the backend emits the normalized recommendation event, allowing later events to overwrite earlier recommendations.

- [ ] **Step 4: Re-run the frontend test**

Run:

```bash
cd frontend && npm test -- --run useChat.test.ts
```

Expected after the fix: PASS.

### Task 4: Regression verification

**Files:**
- Verify only

- [ ] **Step 1: Run focused backend tests**

Run:

```bash
. .venv/bin/activate && PYTHONPATH=backend pytest backend/tests/test_chat.py backend/tests/test_mcp_tools.py -v
```

Expected: all targeted backend tests pass.

- [ ] **Step 2: Run focused frontend tests**

Run:

```bash
cd frontend && npm test -- --run useChat.test.ts ProductCard.test.ts ComparisonTable.test.ts
```

Expected: all targeted frontend tests pass.

- [ ] **Step 3: Re-run browser scenario**

Use Chrome MCP on `http://localhost:3000` with:

1. `I need headphones`
2. `Under 100 dollars`
3. `Mostly for commuting and work calls`

Expected:

- No n8n 500 fallback banner caused by workflow failure.
- If later tool results refine the selection, the right-side panel updates to the refined products.
- Currency selector still updates displayed prices.
