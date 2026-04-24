# Chat Budget And Fallback Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make live product recommendations respect USD user budgets, avoid misleading empty recommendation panels, improve DB fallback relevance, and fix the chat input accessibility warning.

**Architecture:** Keep catalog storage in INR and convert USD budgets at the recommendation/filter boundary before hitting SQLite. Return an explicit empty recommendation payload for no-match cases, and improve the DB fallback by sorting products with lightweight relevance scoring before trimming to the top three.

**Tech Stack:** FastAPI, SQLite, React, Vitest, pytest

---

### Task 1: Lock In Backend Regression Tests

**Files:**
- Modify: `backend/tests/test_mcp_tools.py`
- Test: `backend/tests/test_mcp_tools.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_filter_products_treats_max_price_as_usd(test_db):
    result = execute_tool("filter_products", {"max_price": 10.0})
    data = json.loads(result)
    assert any(product["product_id"] == "B001" for product in data)


def test_get_recommendations_fallback_returns_empty_payload_when_no_products(test_db):
    with patch("app.mcp_tools.httpx.post", side_effect=httpx.RequestError("down")):
        result = execute_tool(
            "get_recommendations",
            {"category": "Computers&Accessories", "max_price": 0.1, "keywords": ["nonexistent"]},
        )
    data = json.loads(result)
    assert data == {"products": [], "comparison": [], "fallback": True, "empty": True}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest backend/tests/test_mcp_tools.py -q`
Expected: FAIL because the current code compares USD directly to INR and always emits comparison rows for empty results.

- [ ] **Step 3: Write minimal implementation**

```python
USD_TO_INR = 83.0

def usd_to_inr(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value * USD_TO_INR, 2)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest backend/tests/test_mcp_tools.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/tests/test_mcp_tools.py backend/app/db.py backend/app/mcp_tools.py
git commit -m "fix: align recommendation budgets with usd inputs"
```

### Task 2: Improve Fallback Recommendation Relevance

**Files:**
- Modify: `backend/app/db.py`
- Modify: `backend/app/mcp_tools.py`
- Test: `backend/tests/test_mcp_tools.py`

- [ ] **Step 1: Write the failing test**

```python
def test_get_recommendations_fallback_prefers_keyword_matches(test_db):
    with patch("app.mcp_tools.httpx.post", side_effect=httpx.RequestError("down")):
        result = execute_tool(
            "get_recommendations",
            {"category": "Computers&Accessories", "max_price": 100.0, "keywords": ["iphone", "lightning", "cable"]},
        )
    data = json.loads(result)
    assert data["products"][0]["product_id"] == "B001"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest backend/tests/test_mcp_tools.py::test_get_recommendations_fallback_prefers_keyword_matches -q`
Expected: FAIL because the fallback currently returns the first DB rows instead of scoring relevance.

- [ ] **Step 3: Write minimal implementation**

```python
def rank_products(products: list[dict], keywords: list[str] | None, use_case: str | None) -> list[dict]:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest backend/tests/test_mcp_tools.py::test_get_recommendations_fallback_prefers_keyword_matches -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/db.py backend/app/mcp_tools.py backend/tests/test_mcp_tools.py
git commit -m "fix: improve fallback recommendation relevance"
```

### Task 3: Fix Frontend Empty State And Accessibility

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/ChatWindow.tsx`
- Create or Modify: `frontend/src/__tests__/App.test.tsx`
- Test: `frontend/src/__tests__/App.test.tsx`

- [ ] **Step 1: Write the failing tests**

```tsx
it('shows a no-results message when recommendation payload is empty', () => {
  ...
})

it('adds accessible name attributes to the chat input', () => {
  ...
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd frontend && npm test -- App.test.tsx`
Expected: FAIL because the UI currently renders “Products found” for empty payloads and the input has no `id`/`name`.

- [ ] **Step 3: Write minimal implementation**

```tsx
if (recommendations && recommendations.empty) {
  return <NoResultsState />
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd frontend && npm test -- App.test.tsx`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/ChatWindow.tsx frontend/src/types.ts frontend/src/__tests__/App.test.tsx
git commit -m "fix: handle empty recommendation state"
```

### Task 4: Full Verification

**Files:**
- Modify: none
- Test: `backend/tests`
- Test: `frontend/src/__tests__`

- [ ] **Step 1: Run backend tests**

Run: `. .venv/bin/activate && python3 -m pytest backend/tests -q`
Expected: PASS

- [ ] **Step 2: Run frontend tests**

Run: `cd frontend && npm test`
Expected: PASS

- [ ] **Step 3: Run a live smoke check**

Run the backend and frontend locally, then exercise an iPhone cable scenario in the browser.
Expected: `$20` budget returns cable results, no-results path shows a dedicated empty state, and the input accessibility warning is gone.
