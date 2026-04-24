# Docker AppleDouble Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove existing `._*` files from the repo and stop them from breaking Git visibility or Docker builds again.

**Architecture:** Treat this as repository hygiene, not application logic. Harden ignore rules at the repo root and in every Docker build context, then do a one-time filesystem cleanup and verify with fresh discovery and Docker build commands.

**Tech Stack:** Git ignore rules, Docker ignore rules, shell verification commands, Docker Compose

---

### Task 1: Harden ignore coverage

**Files:**
- Modify: `.gitignore`
- Modify: `frontend/.dockerignore`
- Modify: `backend/.dockerignore`
- Create: `docker/n8n-init/.dockerignore`

- [ ] **Step 1: Patch root Git ignore rules**

Ensure `.gitignore` contains both recursive and root-safe AppleDouble ignores:

```gitignore
._*
**/._*
```

- [ ] **Step 2: Patch frontend Docker ignore rules**

Ensure `frontend/.dockerignore` contains:

```dockerignore
._*
**/._*
node_modules/
dist/
```

- [ ] **Step 3: Patch backend Docker ignore rules**

Ensure `backend/.dockerignore` contains:

```dockerignore
._*
**/._*
__pycache__/
**/__pycache__/
*.pyc
.pytest_cache/
.venv/
```

- [ ] **Step 4: Add Docker ignore for the `docker/n8n-init` build context**

Create `docker/n8n-init/.dockerignore` with:

```dockerignore
._*
**/._*
__pycache__/
**/__pycache__/
*.pyc
```

### Task 2: Clean the filesystem state

**Files:**
- Delete from working tree: all `._*` files under the repository root

- [ ] **Step 1: Remove AppleDouble files**

Run:

```bash
find . -name '._*' -type f -delete
```

Expected: command exits `0` with no errors.

- [ ] **Step 2: Confirm cleanup**

Run:

```bash
find . -name '._*' -type f
```

Expected: no output.

### Task 3: Verify Docker build behavior

**Files:**
- Verify only, no file edits

- [ ] **Step 1: Check Git visibility**

Run:

```bash
git status --short
```

Expected: no untracked `._*` entries appear.

- [ ] **Step 2: Rebuild Docker images**

Run:

```bash
docker compose -f docker/docker-compose.yml build
```

Expected: build progresses without AppleDouble `xattr` sender failures.
