# Frontend

React + Vite client for the Internet Shop Chatbot.

## Responsibilities

- Render the split chat and recommendation layout
- Consume streamed SSE events from `POST /chat`
- Show top-3 product cards and the comparison table
- Surface fallback recommendations when the n8n pipeline is unavailable

## Scripts

```bash
npm install
npm run dev
npm test
npm run build
```

## Environment

`VITE_API_URL` can be used to point the client at a backend base URL during local development or container builds.
