# Thesis Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the software project into line with the graduation-project requirements and remove contradictions between the thesis claims and the shipped implementation.

**Architecture:** Keep the current React + FastAPI + n8n + SQLite architecture, but tighten the recommendation contract, enforce the stated fault-tolerance rules in backend code rather than prompts alone, and make the workflow output match the thesis requirements exactly. After code changes, rerun the evaluation evidence and update the thesis text where it currently over-claims what the code does.

**Tech Stack:** Python 3.14 / FastAPI / Anthropic SDK / SQLite / React + Vite + TypeScript + Vitest / n8n / Docker Compose

---

### Task 1: Fix the Recommendation Payload Contract

**Files:**
- Modify: `backend/app/mcp_tools.py`
- Modify: `backend/tests/test_mcp_tools.py`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/types.ts`
- Test: `backend/tests/test_mcp_tools.py`

- [ ] **Step 1: Make fallback output match FR4 and NFR2**

Change the fallback branch in `backend/app/mcp_tools.py` so it returns exactly three products, sets `fallback` to `True`, and emits comparison rows in the same shape as the n8n workflow.

- [ ] **Step 2: Keep the frontend message consistent with the payload**

Keep the current fallback banner logic in `frontend/src/App.tsx`, but ensure the component assumes exactly three products for recommendation mode and fallback mode.

- [ ] **Step 3: Lock the contract with tests**

Extend `backend/tests/test_mcp_tools.py` to assert:
- fallback mode returns `fallback is True`
- fallback mode returns exactly three products
- fallback mode returns a non-empty comparison payload

- [ ] **Step 4: Verify**

Run: `python3 -m pytest backend/tests/test_mcp_tools.py -v`
Expected: all tests pass.

### Task 2: Make the Comparison Table Match FR6

**Files:**
- Modify: `workflows/recommendation-pipeline.json`
- Modify: `frontend/src/components/ComparisonTable.tsx`
- Modify: `frontend/src/types.ts`
- Add or modify: `frontend/src/__tests__/ComparisonTable.test.tsx`

- [ ] **Step 1: Replace review-count row with key-feature row**

Update the `Build Comparison` node in `workflows/recommendation-pipeline.json` so the rows are:
- `Price`
- `Rating`
- `Key Features`

Derive `Key Features` from `about_product`, splitting on `|` and keeping the first 2-3 concise features per product.

- [ ] **Step 2: Ensure the table renders feature text cleanly**

Update `frontend/src/components/ComparisonTable.tsx` if needed so multi-feature text wraps correctly and remains readable on smaller screens.

- [ ] **Step 3: Add a UI-level test**

Extend `frontend/src/__tests__/ComparisonTable.test.tsx` to assert that feature text from the comparison payload is rendered, not just numeric rows.

- [ ] **Step 4: Verify**

Run: `npm test -- ComparisonTable`
Expected: comparison table tests pass.

### Task 3: Enforce Preference-Gating and Fault-Tolerance in Backend Code

**Files:**
- Modify: `backend/app/chat.py`
- Modify: `backend/app/mcp_tools.py`
- Add or modify: `backend/tests/test_chat.py`
- Add or modify: `backend/tests/test_mcp_tools.py`

- [ ] **Step 1: Add backend-side validation for `get_recommendations`**

Do not rely only on the prompt. Validate that `category` plus at least one of `max_price`, `use_case`, or `keywords` is present before executing the recommendation path.

- [ ] **Step 2: Add malformed tool-call retry**

Wrap the LLM/tool loop so one malformed tool-call response triggers a single retry with a corrective system message. If the retry also fails, stream a user-readable error.

- [ ] **Step 3: Add tests for both failure modes**

Add tests covering:
- blocked recommendation call when minimum preference threshold is missing
- one retry on malformed tool output
- graceful user-visible failure after the retry budget is exhausted

- [ ] **Step 4: Verify**

Run: `python3 -m pytest backend/tests/test_chat.py backend/tests/test_mcp_tools.py -v`
Expected: new validation and retry tests pass.

### Task 4: Resolve the Scope Gap Around Complementary Products

**Files:**
- Either modify: `backend/app/mcp_tools.py`, `workflows/recommendation-pipeline.json`, `frontend/src/App.tsx`, `frontend/src/types.ts`
- Or modify: `docs/guidlines/interim-report.md`, `CLAUDE.md`

- [ ] **Step 1: Choose one of two outcomes**

Outcome A: implement complementary product suggestions as a bounded enhancement.
Outcome B: formally descope it from repo guidance and interim-report carryover docs so the repository scope matches the final thesis scope.

- [ ] **Step 2: Prefer explicit scope consistency over silent omission**

If the feature stays out of scope, remove or revise the stale claims in:
- `docs/guidlines/interim-report.md`
- `CLAUDE.md`

- [ ] **Step 3: Verify**

Run: `rg -n "complement|complementary|supplement" .`
Expected: remaining matches reflect the chosen scope accurately.

### Task 5: Harden Deployment and Project Documentation

**Files:**
- Modify: `workflows/recommendation-pipeline.json`
- Modify: `docker/docker-compose.yml`
- Add: `README.md`
- Modify: `frontend/README.md`

- [ ] **Step 1: Remove `host.docker.internal` dependency**

Change the workflow request URL from `http://host.docker.internal:8000/internal/products` to the compose-network service name `http://backend:8000/internal/products`.

- [ ] **Step 2: Document the actual graduation-project run path**

Create a root `README.md` that documents:
- prerequisites
- database seeding
- `docker compose -f docker/docker-compose.yml up --build`
- n8n workflow import
- test commands

- [ ] **Step 3: Replace the stock frontend README**

Update `frontend/README.md` so it describes the actual app instead of the Vite template.

- [ ] **Step 4: Verify**

Run: `docker compose -f docker/docker-compose.yml config`
Expected: compose config resolves cleanly.

### Task 6: Repair the Test Tooling and Verification Story

**Files:**
- Modify: `frontend/package.json`
- Modify: `backend/requirements.txt` only if needed for parity with the intended local workflow
- Optionally add: repo-level test instructions in `README.md`

- [ ] **Step 1: Fix the frontend test dependency**

Add `@testing-library/dom` explicitly to `frontend/package.json` so the frontend test suite works from a clean install.

- [ ] **Step 2: Define the supported backend test command**

Document the exact backend setup command, for example:
`python3 -m pip install -r backend/requirements.txt`

- [ ] **Step 3: Verify both suites from a clean dependency install**

Run:
- `npm test`
- `python3 -m pytest backend/tests -v`

Expected: both suites run successfully on a standard local environment.

### Task 7: Reconcile the Thesis Text with the Implemented System

**Files:**
- Modify: `/Volumes/Sytles Disk/projects/guraduation-thesis/final report/main.tex`
- Modify: `/Volumes/Sytles Disk/projects/guraduation-thesis/final report/chapters/implementation.tex`
- Modify: `/Volumes/Sytles Disk/projects/guraduation-thesis/final report/chapters/evaluation.tex`

- [ ] **Step 1: Remove over-claims before submission**

Update thesis claims that currently say all FRs and NFRs are already satisfied if the code still does not implement them.

- [ ] **Step 2: Keep implementation and evaluation chapters consistent**

Make sure the implementation chapter, evaluation chapter, and abstract all describe the same comparison behavior, fallback behavior, and retry behavior.

- [ ] **Step 3: Re-run the evaluation after code changes**

Repeat the FR2, FR5, FR6, NFR2, and NFR3 checks and replace the narrative with the observed results from the fixed codebase.

- [ ] **Step 4: Verify**

Run: `rg -n "all eight functional requirements|all six non-functional requirements|fallback|feature bullet|malformed tool" '/Volumes/Sytles Disk/projects/guraduation-thesis/final report'`
Expected: no stale contradictions remain.
