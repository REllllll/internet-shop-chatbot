# CORS Origin Config Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make backend CORS origins configurable via environment while allowing both `http://localhost:3000` and `http://127.0.0.1:3000` by default in local development.

**Architecture:** Keep the change inside the backend startup path. Add a small parser for a comma-separated `CORS_ALLOW_ORIGINS` env var, feed that into FastAPI `CORSMiddleware`, and cover the behavior with targeted tests plus a short README update.

**Tech Stack:** FastAPI, CORSMiddleware, pytest, TestClient

---

### Task 1: Add failing backend CORS test

**Files:**
- Modify: `backend/tests/test_internal.py`
- Test: `backend/tests/test_internal.py`

- [ ] **Step 1: Write the failing test**

Add a test that sends a CORS preflight request from `http://127.0.0.1:3000` and expects a successful response with the matching allow-origin header.

```python
def test_cors_allows_loopback_frontend_origin(client):
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
backend/.venv/bin/python -m pytest backend/tests/test_internal.py::test_cors_allows_loopback_frontend_origin -v
```

Expected: FAIL because the current CORS config only allows `http://localhost:3000`.

### Task 2: Make CORS origins configurable

**Files:**
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_internal.py`

- [ ] **Step 1: Add a small origin parser and local defaults**

Implement a helper that reads `CORS_ALLOW_ORIGINS`, splits on commas, trims whitespace, and falls back to:

```python
[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

- [ ] **Step 2: Wire the parsed list into `CORSMiddleware`**

Update the middleware setup so `allow_origins=` uses the helper result instead of a hardcoded single origin.

- [ ] **Step 3: Run the targeted test to verify it passes**

Run:

```bash
backend/.venv/bin/python -m pytest backend/tests/test_internal.py::test_cors_allows_loopback_frontend_origin -v
```

Expected: PASS.

### Task 3: Cover explicit env override and document it

**Files:**
- Modify: `backend/tests/test_internal.py`
- Modify: `README.md`

- [ ] **Step 1: Add an env-override test**

Add a test that sets `CORS_ALLOW_ORIGINS` to a custom origin, reloads `app.main`, and verifies the custom origin is allowed.

```python
def test_cors_uses_configured_origins(monkeypatch, test_db):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://example.com")

    import importlib
    import app.main

    module = importlib.reload(app.main)
    client = TestClient(module.app)

    response = client.options(
        "/chat",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://example.com"
```

- [ ] **Step 2: Document the new backend environment variable**

Add a short note to `README.md` describing `CORS_ALLOW_ORIGINS` as a comma-separated list, and mention the default local origins.

- [ ] **Step 3: Run the focused backend test file**

Run:

```bash
backend/.venv/bin/python -m pytest backend/tests/test_internal.py -v
```

Expected: PASS.
