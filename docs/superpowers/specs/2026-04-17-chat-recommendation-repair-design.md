# Chat Recommendation Repair Design

## Goal

Repair the broken recommendation path in two places:

1. Restore the n8n recommendation workflow so successful pipeline responses can be returned instead of always falling back.
2. Ensure the right-side recommendation panel can be replaced when later tool calls discover better products than the initial `get_recommendations` result.

## Scope

This design is intentionally narrow. It does not redesign the prompting strategy, ranking model, or UI layout. It only repairs the broken workflow path and the stale recommendation rendering behavior that was observed during Chrome MCP testing.

## Problem Summary

### 1. n8n workflow failure

The `Recommendation Pipeline` webhook returns HTTP 500. n8n execution data shows `Rank Products` fails with `TypeError: products is not iterable [line 15]`.

Root cause:

- `Query Products` emits many n8n items, one product per item.
- `Rank Products` currently reads `const products = $input.first().json;`, which gives a single product object.
- The code then spreads `products` as if it were an array.

### 2. Stale recommendation panel

The backend emits a `products` SSE event only for `get_recommendations`. If the model later realizes those results are wrong and uses `search_products` or `filter_products` to recover, the assistant text changes but the right-side panel stays on the original bad results.

Root cause:

- Backend event emission is tied to one tool name instead of to “tool results that can drive the recommendation panel”.
- Frontend only listens for that single event shape and never receives replacement results for later recovery tools.

## Chosen Approach

### Workflow repair

Update the n8n `Rank Products` code to collect all incoming items with `$input.all().map(item => item.json)` before scoring and sorting. Keep the remainder of the pipeline contract unchanged.

### Recommendation refresh repair

Introduce a backend helper that decides whether a tool result contains displayable recommendation data. Emit a recommendation update SSE event whenever:

- `get_recommendations` returns its normal payload, or
- `search_products` / `filter_products` return product lists that can be promoted into the recommendation panel.

Promotion rules:

- Convert list-style tool results into the existing `RecommendationResult` shape.
- Reuse the existing comparison builder so the UI keeps the same rendering contract.
- Mark promoted results as fallback so the UI can still signal they came from a non-pipeline path.

Frontend behavior:

- Continue appending assistant text exactly as today.
- Replace the right-side recommendation state whenever a recommendation update event arrives, regardless of which tool produced it.

## Data Flow

1. User sends a chat message.
2. Backend streams assistant deltas and tool-use events.
3. If a tool returns recommendation-capable product data, backend emits a recommendation update SSE event with the normalized `RecommendationResult` payload.
4. Frontend updates the recommendation state from that event.
5. Later tool calls can overwrite earlier recommendations in the same conversation turn.

## Files Affected

- `workflows/recommendation-pipeline.json`
- `backend/app/chat.py`
- `backend/app/mcp_tools.py`
- `backend/tests/test_chat.py`
- `frontend/src/hooks/useChat.ts`
- `frontend/src/types.ts` only if event typing needs expansion
- `frontend/src/__tests__/useChat.test.ts`

## Testing Strategy

### Backend

- Add a failing test showing search/filter recovery results should also drive recommendation updates.
- Keep existing malformed-tool and session-history tests green.

### Frontend

- Add a failing hook test where a later recommendation update replaces an earlier one.
- Keep current SSE parsing behavior intact.

### Workflow

- Add a targeted test that calls the live webhook and asserts the response is HTTP 200 with recommendation-shaped JSON when n8n is running.

## Risks

- Promoting generic search results into the recommendation panel could show exploratory results too aggressively. The implementation should only normalize concrete product lists and should cap output to the first three products, matching the current UI.
- The workflow fix must preserve the response shape expected by `execute_tool()` and the frontend.
