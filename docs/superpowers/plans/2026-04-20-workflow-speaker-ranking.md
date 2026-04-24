# Workflow Speaker Ranking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `n8n` recommendation workflow rank actual speaker products ahead of accessory items like cables for speaker-related queries.

**Architecture:** Keep candidate retrieval broad, but replace the `Rank Products` code node with a category-aware scoring function. The workflow should prefer speaker categories, weight product-name and category matches above description noise, and penalize clearly irrelevant categories such as cables, adapters, and smartwatches.

**Tech Stack:** n8n workflow JSON, JavaScript code node, pytest workflow contract tests, Docker Compose

---

### Task 1: Add a failing workflow contract test

**Files:**
- Modify: `backend/tests/test_workflow_contract.py`
- Test: `backend/tests/test_workflow_contract.py`

- [ ] **Step 1: Write the failing test**

Add a contract test that inspects the `Rank Products` code node and asserts it includes:

- a strong speaker category preference such as `bluetoothspeakers` / `outdoorspeakers`
- accessory penalties such as `cables`
- use-case token handling

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
backend/.venv/bin/python -m pytest backend/tests/test_workflow_contract.py -v
```

Expected: FAIL because the current ranking code only multiplies rating/popularity by a shallow keyword match.

### Task 2: Replace workflow ranking logic

**Files:**
- Modify: `workflows/recommendation-pipeline.json`
- Test: `backend/tests/test_workflow_contract.py`

- [ ] **Step 1: Update the `Rank Products` code node**

Implement JavaScript that:

- tokenizes `keywords` and `use_case`
- strongly rewards `speakers`, `bluetoothspeakers`, and `outdoorspeakers` in the category path
- rewards keyword matches in `product_name` and `category` more than `about_product`
- penalizes `cables`, `adapters`, `receivers`, and `smartwatches`

- [ ] **Step 2: Run the workflow contract test to verify it passes**

Run:

```bash
backend/.venv/bin/python -m pytest backend/tests/test_workflow_contract.py -v
```

Expected: PASS.

### Task 3: Redeploy and verify live behavior

**Files:**
- Modify: none
- Test: live Docker/n8n/browser behavior

- [ ] **Step 1: Rebuild or restart services so `n8n` uses the updated workflow**

Run:

```bash
find . -path ./.git -prune -o -name '._*' -type f -delete
docker compose -f docker/docker-compose.yml up -d --build backend
docker compose -f docker/docker-compose.yml up -d n8n-init
```

Expected: backend and workflow importer restart cleanly.

- [ ] **Step 2: Verify backend tests still pass**

Run:

```bash
backend/.venv/bin/python -m pytest backend/tests -v
```

Expected: PASS.

- [ ] **Step 3: Verify the live speaker query**

Run the existing Chrome flow for:

`Recommend Bluetooth speakers under 50 USD for travel, minimum 4-star rating.`

Expected:

- no cable products in the top picks
- visible speaker results such as JBL / boAt / Infinity speaker products
- no `Products found (pipeline unavailable)` label
