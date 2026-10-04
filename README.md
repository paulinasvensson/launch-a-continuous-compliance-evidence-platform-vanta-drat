# Continuous Compliance Evidence Platform (MVP)

A minimal FastAPI service that helps SMEs shipping AI features maintain
continuous compliance evidence for the EU AI Act and track obligations
across the fragmenting 2026 US state privacy-law patchwork.

## What it does

- Register an organization profile with its target markets (`EU`, `CA`, `CO`, `VA`, `CT`, ...).
- Connect cloud/dev/HR tool integrations (AWS/GCP/Azure, GitHub/GitLab, BambooHR/Gusto)
  with OAuth-style access tokens, stored encrypted at rest.
- Trigger idempotent/retryable evidence sync jobs per integration, plus an
  automatic background scheduler (APScheduler) that re-syncs every 6 hours.
- Generate EU AI Act technical documentation and US-state obligation
  checklists from collected evidence using versioned Jinja2 templates.
- Track and update per-jurisdiction compliance obligations.

## Run it

