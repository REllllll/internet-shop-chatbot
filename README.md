# Internet Shop Chatbot

Graduation-project prototype for conversational product recommendation over a static Amazon product dataset. The stack is React/Vite on the frontend, FastAPI on the backend, SQLite for product data, and n8n for the ranking workflow.

## Project Structure

- `frontend/` React client with chat UI, product cards, and comparison table
- `backend/` FastAPI app, MCP-style tools, SSE chat endpoint, and tests
- `workflows/` exported n8n workflow JSON
- `docker/` Docker Compose configuration
- `data/` seed script and SQLite database artifacts

## Prerequisites

- Node.js 20+
- Python 3.12+ or 3.14+
- Docker Desktop or compatible Docker Engine with Compose
- Anthropic API key in `.env`

## Local Setup

1. Create the backend virtual environment and install dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r backend/requirements.txt
```

2. Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

3. Seed the product database if `data/products.db` does not exist:

```bash
. .venv/bin/activate
python3 data/seed.py
```

## Run with Docker Compose

Start the full stack:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- n8n canvas: `http://localhost:5678`

After n8n starts, import `workflows/recommendation-pipeline.json` into the n8n UI.

## Run Tests

Backend:

```bash
. .venv/bin/activate
python3 -m pytest backend/tests -v
```

Frontend:

```bash
cd frontend
npm test
```

## Notes

- The recommendation flow is designed around a static dataset. Real-time inventory and user authentication are intentionally out of scope.
- If the n8n webhook is unavailable, the backend falls back to direct SQLite querying and still returns top-3 products plus a comparison payload.
