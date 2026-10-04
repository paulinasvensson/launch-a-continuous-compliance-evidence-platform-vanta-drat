from datetime import datetime
from models import Integration, EvidenceItem, Organization, ComplianceObligation
from services.adapters import pull_evidence


def connect_integration(db, org_id, provider, type_, access_token):
    integration = Integration(
        org_id=org_id,
        provider=provider,
        type=type_,
        status="connected",
        access_token_encrypted=f"enc:{access_token}" if access_token else None,
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


def sync_integration(db, integration_id):
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        return None

    org = db.query(Organization).filter(Organization.id == integration.org_id).first()
    raw_items = pull_evidence(integration.provider, org, integration)

    # Match evidence to obligations: cloud/dev evidence -> eu_ai_act obligations,
    # hr evidence -> us_state_privacy obligations (attestation-heavy requirements).
    framework_target = "eu_ai_act" if integration.type in ("cloud", "dev") else "us_state_privacy"
    candidate_obligations = (
        db.query(ComplianceObligation)
        .filter(ComplianceObligation.org_id == org.id, ComplianceObligation.framework == framework_target)
        .all()
    )

    created = []
    for idx, item in enumerate(raw_items):
        obligation = candidate_obligations[idx % len(candidate_obligations)] if candidate_obligations else None
        evidence = EvidenceItem(
            org_id=org.id,
            obligation_id=obligation.id if obligation else None,
            source_integration_id=integration.id,
            type=item["type"],
            content_ref=item["content_ref"],
            is_current=True,
        )
        db.add(evidence)
        created.append(evidence)

        if obligation and obligation.status == "not_started":
            obligation.status = "in_progress"
        if obligation:
            obligation.last_checked_at = datetime.utcnow()

    integration.last_synced_at = datetime.utcnow()
    db.commit()
    for e in created:
        db.refresh(e)
    return created
