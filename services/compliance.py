from sqlalchemy.orm import Session
import models


def create_organization(db: Session, name: str, employee_count: int, sells_eu: bool, us_states: str):
    org = models.Organization(
        name=name,
        employee_count=employee_count,
        sells_eu=sells_eu,
        us_states=us_states or "",
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def get_applicable_requirements(db: Session, org: models.Organization):
    """Return requirements applicable to this org based on EU/US footprint."""
    requirements = db.query(models.Requirement).all()
    applicable = []
    states = [s.strip().upper() for s in (org.us_states or "").split(",") if s.strip()]
    for req in requirements:
        if req.framework == "EU_AI_ACT" and org.sells_eu:
            applicable.append(req)
        elif req.framework == "US_PRIVACY" and len(states) > 0:
            applicable.append(req)
    return applicable


def get_compliance_status(db: Session, org: models.Organization):
    applicable = get_applicable_requirements(db, org)
    evidence_by_req = {
        e.requirement_id: e
        for e in db.query(models.EvidenceItem).filter(models.EvidenceItem.organization_id == org.id).all()
    }

    items = []
    collected_count = 0
    for req in applicable:
        ev = evidence_by_req.get(req.id)
        status = ev.status if ev else "missing"
        if status == "collected":
            collected_count += 1
        items.append({
            "requirement_code": req.code,
            "title": req.title,
            "framework": req.framework,
            "status": status,
        })

    total = len(applicable)
    coverage_pct = round((collected_count / total) * 100, 1) if total else 0.0

    return {
        "organization": org.name,
        "total_requirements": total,
        "collected": collected_count,
        "coverage_pct": coverage_pct,
        "items": items,
    }


def generate_technical_file(db: Session, org: models.Organization):
    """Build the EU AI Act technical documentation file from collected evidence."""
    evidence_by_req = {
        e.requirement_id: e
        for e in db.query(models.EvidenceItem).filter(models.EvidenceItem.organization_id == org.id).all()
    }
    ai_requirements = db.query(models.Requirement).filter(models.Requirement.framework == "EU_AI_ACT").all()

    sections = []
    for req in ai_requirements:
        ev = evidence_by_req.get(req.id)
        sections.append({
            "section_code": req.code,
            "title": req.title,
            "description": req.description,
            "status": ev.status if ev else "missing",
            "evidence_source": ev.source if ev else None,
            "evidence_details": ev.details if ev else "No evidence collected yet. Run a sync.",
        })

    return {
        "organization": org.name,
        "document_title": f"EU AI Act Technical Documentation - {org.name}",
        "sections": sections,
    }
