---
name: start-local-services
description: Use when starting the internet-shop-chatbot local Docker stack, especially on macOS external disks where ._* files can break Docker builds
---

# Start Local Services

From the repo root, start the app with:

```bash
find . -path ./.git -prune -o -name '._*' -type f -delete
docker compose -f docker/docker-compose.yml up -d --build
```

Verify the stack with:

```bash
docker compose -f docker/docker-compose.yml ps
```

Local URLs:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- n8n: `http://localhost:5678`

Useful follow-ups:

```bash
docker compose -f docker/docker-compose.yml logs -f
docker compose -f docker/docker-compose.yml down
```
