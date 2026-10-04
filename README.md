# Continuous Compliance Evidence Platform (EU AI Act + US State Privacy)

MVP for SMEs deploying AI features that must track EU AI Act technical
documentation duties and the fragmenting 2026 US state privacy-law patchwork,
without enterprise-grade GRC tooling or in-house counsel.

## What it does

- Create an organization profile with jurisdictions (EU sales flag + operating states).
- Auto-generates applicable compliance obligations from structured, seeded
  reference rules (`ObligationRule`) — not hardcoded in endpoint logic, so
  regulatory text/dates can be updated independently of code.
- Connect pluggable OAuth-style integrations (AWS, GCP, Azure, GitHub,
  BambooHR, Rippling) and sync evidence pulls from them.
- Map evidence to obligations and track status (not_started/in_progress/met/at_risk).
- Generate versioned, idempotent technical documentation drafts
  (EU AI Act technical file, DPIA, state privacy notice) from current
  evidence, optionally enriched by an LLM (OpenAI) if `OPENAI_API_KEY` is set.
- Dashboard summary of aggregate compliance risk across frameworks.

## Endpoints

- `POST /orgs` — free — create org + auto-generate applicable obligations
- `POST /integrations/connect` — paid — register a tool connection
- `POST /integrations/{id}/sync` — paid — pull evidence from a connected tool
- `GET /obligations?org_id=` — free — list obligations/status
- `GET /obligations/{id}/evidence` — paid — evidence mapped to an obligation
- `POST /documents/generate` — paid — generate a new versioned draft document
- `GET /documents/{id}` — free — retrieve a document + version history
- `GET /dashboard/summary?org_id=` — free — aggregate risk status

## Run

