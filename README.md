# Continuous Compliance Evidence Platform (MVP)

Continuous compliance-evidence platform for SMEs shipping AI features into the
EU and across US state privacy jurisdictions. It ingests evidence from
cloud/dev/HR tools (stubbed connectors behind a common adapter interface),
generates EU AI Act technical documentation, and tracks obligations across
the 2026 US state privacy-law patchwork.

## Core flow
1. `POST /orgs` — create an organization profile (free) and auto-seed
   obligations based on declared target markets (EU / US states).
2. `POST /integrations/connect` — register a cloud/dev/HR tool connection
   (paid).
3. `POST /integrations/{id}/sync` — pull mock evidence for that provider
   (paid).
4. `GET /evidence` — review collected evidence (paid).
5. `POST /documents/generate` — render an EU AI Act technical file from
   current evidence via Jinja2 (paid).
6. `GET /documents/{id}` — view a generated document (free).
7. `GET /obligations` / `PATCH /obligations/{id}` — track and update
   compliance obligations (paid).

## Connectors
All provider connectors (AWS, GCP, Azure, GitHub, GitLab, BambooHR, Rippling)
implement `services/connectors.py:BaseConnector.fetch_evidence()`. Real OAuth
flows are out of scope for this MVP — each connector returns realistic mock
evidence payloads so the sync and documentation pipeline can be fully
demoed. New providers can be added by implementing the same interface and
registering them in `CONNECTOR_REGISTRY`.

## Run locally
