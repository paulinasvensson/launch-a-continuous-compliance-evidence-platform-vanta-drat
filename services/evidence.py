from sqlalchemy.orm import Session

import models


def list_evidence(db: Session, org_id: int, category: str | None = None, status: str | None = None):
    query = db.query(models.EvidenceItem).filter(models.EvidenceItem.org_id == org_id)
    if category:
        query = query.filter(models.EvidenceItem.category == category)
    if status:
        query = query.filter(models.EvidenceItem.status == status)
    return query.order_by(models.EvidenceItem.collected_at.desc()).all()
