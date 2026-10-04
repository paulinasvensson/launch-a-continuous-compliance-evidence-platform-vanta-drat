from datetime import datetime, timezone

from sqlalchemy.orm import Session

import models

# Versioned, editable rule set describing per-jurisdiction obligations.
# Kept as data rather than hardcoded branching logic, since state privacy
# law requirements change frequently.
US_STATE_PRIVACY_RULES = {
    "CA": [
        ("CCPA/CPRA risk assessment", "Document risk assessment for automated decision-making using AI."),
        ("Opt-out mechanism", "Provide consumer opt-out of profiling/automated decisions."),
    ],
    "CO": [
        ("Colorado Privacy Act DPIA", "Conduct data protection impact assessment for profiling."),
    ],
    "VA": [
        ("Virginia CDPA assessment", "Document data protection assessment for AI-driven processing."),
    ],
    "CT": [
        ("Connecticut Data Privacy Act review", "Review automated profiling practices annually."),
    ],
}

EU_AI_ACT_RULES = {
    "EU": [
        ("Technical documentation (Annex IV)", "Maintain up-to-date technical file for high-risk AI systems."),
        ("Risk management system", "Document and maintain ongoing risk management process."),
        ("Post-market monitoring", "Establish post-market monitoring plan for deployed AI system."),
    ]
}


def seed_obligations_for_org(db: Session, org_id: int, jurisdictions: list[str]):
    created = []
    for j in jurisdictions:
        rules = EU_AI_ACT_RULES.get(j) or US_STATE_PRIVACY_RULES.get(j)
        if not rules:
            continue
        for requirement, description in rules:
            exists = (
                db.query(models.Obligation)
                .filter(
                    models.Obligation.org_id == org_id,
                    models.Obligation.jurisdiction == j,
                    models.Obligation.requirement == requirement,
                )
                .first()
            )
            if exists:
                continue
            obligation = models.Obligation(
                org_id=org_id,
                jurisdiction=j,
                requirement=requirement,
                description=description,
                status="open",
            )
            db.add(obligation)
            created.append(obligation)
    db.commit()
    return created


def list_obligations(db: Session, org_id: int, jurisdiction: str | None = None, status: str | None = None):
    query = db.query(models.Obligation).filter(models.Obligation.org_id == org_id)
    if jurisdiction:
        query = query.filter(models.Obligation.jurisdiction == jurisdiction)
    if status:
        query = query.filter(models.Obligation.status == status)
    return query.all()


def update_obligation(db: Session, obligation_id: int, status: str | None, mark_reviewed: bool):
    obligation = db.query(models.Obligation).filter(models.Obligation.id == obligation_id).first()
    if not obligation:
        return None
    if status:
        obligation.status = status
    if mark_reviewed:
        obligation.last_reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(obligation)
    return obligation
