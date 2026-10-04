from sqlalchemy.orm import Session
import models


def generate_requirements_for_org(db: Session, org: models.Organization):
    """Reads static seeded rule templates and materializes ComplianceRequirement rows
    for this org based on its market/state footprint and employee count."""
    org_states = set(s for s in org.us_states_operating.split(",") if s)
    templates = db.query(models.ComplianceRuleTemplate).all()

    existing_keys = set(
        (r.requirement_key, r.jurisdiction)
        for r in db.query(models.ComplianceRequirement).filter(models.ComplianceRequirement.org_id == org.id).all()
    )

    created = []
    for t in templates:
        if not (t.min_employees <= org.employee_count <= t.max_employees):
            continue
        if t.requires_eu_market and not org.eu_market:
            continue
        if t.requires_us_state and t.requires_us_state not in org_states:
            continue
        if (t.requirement_key, t.jurisdiction) in existing_keys:
            continue

        req = models.ComplianceRequirement(
            org_id=org.id,
            framework=t.framework,
            jurisdiction=t.jurisdiction,
            requirement_key=t.requirement_key,
            description=t.description,
            status="pending",
            due_date=t.due_date,
        )
        db.add(req)
        created.append(req)

    if created:
        db.commit()
    return created


def list_requirements(db: Session, org_id: int):
    return db.query(models.ComplianceRequirement).filter(models.ComplianceRequirement.org_id == org_id).all()


def update_requirement_status(db: Session, org_id: int, req_id: int, status: str):
    valid_statuses = {"pending", "in-progress", "reviewed", "met"}
    if status not in valid_statuses:
        return None
    req = db.query(models.ComplianceRequirement).filter(
        models.ComplianceRequirement.id == req_id,
        models.ComplianceRequirement.org_id == org_id,
    ).first()
    if not req:
        return None
    req.status = status
    db.commit()
    db.refresh(req)
    return req
