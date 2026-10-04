from sqlalchemy.orm import Session
import models
from services.requirements import generate_requirements_for_org


def create_organization(db: Session, name: str, industry: str, employee_count: int,
                         eu_market: bool, us_states_operating: list[str]) -> models.Organization:
    org = models.Organization(
        name=name,
        industry=industry,
        employee_count=employee_count,
        eu_market=eu_market,
        us_states_operating=",".join([s.strip().upper() for s in us_states_operating if s.strip()]),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    # Immediately generate the applicable obligation set from seeded rules
    generate_requirements_for_org(db, org)
    return org


def get_dashboard(db: Session, org_id: int) -> dict:
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        return None

    requirements = db.query(models.ComplianceRequirement).filter(
        models.ComplianceRequirement.org_id == org_id
    ).all()

    integrations = db.query(models.Integration).filter(models.Integration.org_id == org_id).all()
    evidence_count = db.query(models.EvidenceItem).filter(models.EvidenceItem.org_id == org_id).count()
    documents_count = db.query(models.TechnicalDocument).filter(models.TechnicalDocument.org_id == org_id).count()

    by_framework = {}
    for r in requirements:
        fw = by_framework.setdefault(r.framework, {"total": 0, "met": 0, "in_progress": 0, "pending": 0, "reviewed": 0})
        fw["total"] += 1
        fw[r.status.replace("-", "_")] = fw.get(r.status.replace("-", "_"), 0) + 1

    return {
        "organization": {
            "id": org.id,
            "name": org.name,
            "industry": org.industry,
            "employee_count": org.employee_count,
            "eu_market": org.eu_market,
            "us_states_operating": org.us_states_operating,
        },
        "requirements_summary": by_framework,
        "total_requirements": len(requirements),
        "integrations_connected": len(integrations),
        "evidence_items_collected": evidence_count,
        "documents_generated": documents_count,
    }
