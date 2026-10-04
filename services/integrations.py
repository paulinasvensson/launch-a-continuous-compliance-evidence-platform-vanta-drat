import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

import models
from services.crypto import encrypt_token

VALID_PROVIDERS = {
    "aws": "cloud", "gcp": "cloud", "azure": "cloud",
    "github": "dev", "gitlab": "dev",
    "bamboohr": "hr", "gusto": "hr",
}


def connect_integration(db: Session, org_id: int, provider: str, access_token: str) -> models.Integration:
    provider = provider.lower()
    integration_type = VALID_PROVIDERS.get(provider, "cloud")
    integration = models.Integration(
        org_id=org_id,
        provider=provider,
        type=integration_type,
        status="active",
        access_token_encrypted=encrypt_token(access_token),
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


def _simulate_pull(integration: models.Integration) -> list[dict]:
    """Simulate a retryable, idempotent pull of evidence from a provider's API."""
    now = datetime.now(timezone.utc).isoformat()
    if integration.type == "cloud":
        return [{"category": "access_control", "data": {"provider": integration.provider, "checked_at": now, "mfa_enforced": True}}]
    if integration.type == "dev":
        return [{"category": "model_card", "data": {"provider": integration.provider, "checked_at": now, "repos_scanned": 12}}]
    return [{"category": "hr_training", "data": {"provider": integration.provider, "checked_at": now, "ai_policy_ack_rate": 0.86}}]


def sync_integration(db: Session, integration: models.Integration) -> list[models.EvidenceItem]:
    """Idempotent: safe to call repeatedly / retry on failure."""
    items = []
    try:
        pulled = _simulate_pull(integration)
        for entry in pulled:
            existing = (
                db.query(models.EvidenceItem)
                .filter(
                    models.EvidenceItem.integration_id == integration.id,
                    models.EvidenceItem.category == entry["category"],
                )
                .order_by(models.EvidenceItem.collected_at.desc())
                .first()
            )
            source_data = json.dumps(entry["data"])
            if existing and existing.source_data == source_data:
                continue  # no change, idempotent no-op
            item = models.EvidenceItem(
                org_id=integration.org_id,
                integration_id=integration.id,
                category=entry["category"],
                source_data=source_data,
                status="collected",
            )
            db.add(item)
            items.append(item)
        integration.status = "active"
        integration.last_synced_at = datetime.now(timezone.utc)
        db.commit()
        for item in items:
            db.refresh(item)
    except Exception:
        integration.status = "error"
        db.commit()
        raise
    return items
