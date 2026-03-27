# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a graduation project: an **internet shop conversational recommendation chatbot**. The system integrates LLM reasoning with real-time product data retrieval and workflow automation to deliver explainable, personalized product recommendations through multi-turn dialogue.

**Key capabilities to implement:**
- Multi-turn preference elicitation (ask targeted questions to narrow down user needs)
- Real-time product retrieval via **Model Context Protocol (MCP)**
- **n8n** workflow orchestration for the recommendation pipeline
- Explainable recommendations with trade-off analysis and product comparisons
- Privacy-by-design: minimal data retention, no unnecessary personal data storage

## Planned Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python |
| Frontend | ReactJS |
| Workflow Automation | n8n |
| LLM Integration | Claude API (via MCP) |
| Protocol | Model Context Protocol (MCP) |
| UI Design | Figma prototypes → ReactJS |

## Architecture

The system has four main components:

1. **Conversational Layer** — preference elicitation module, manages dialogue state across turns, incrementally refines user intent
2. **MCP Retrieval Module** — connects LLM to live product database via MCP tools; handles real-time queries, caching, and fallback sources
3. **Recommendation Engine** — ranks and selects products, generates explanations, produces comparison tables between similar items, suggests complementary products
4. **n8n Workflow** — orchestrates the full pipeline: data retrieval → ranking → response formatting → error handling/retry logic

## LLM Output Constraints

All LLM outputs must be **schema-constrained JSON** — enforce strict JSON schemas and implement automated validation/repair routines to handle non-conforming outputs. This is critical for reliable pipeline integration.

## Development Guidelines

- Follow **privacy-by-design**: process user preference data only for recommendation generation; do not persist it beyond the session
- Use **MCP** as the standard protocol for all LLM ↔ external data communication (database, product APIs) rather than custom API integrations
- Implement **modular n8n workflows** with logging and retry strategies; validate at each node boundary
- Each recommendation must include evidence-based explanation: feature-level reasoning + horizontal comparison across similar products

## Key Reference

Full project specification and research context: `docs/guidlines/interim-report.md`
