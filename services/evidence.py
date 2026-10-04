from sqlalchemy.orm import Session
import models


def ingest_evidence(db: Session, company_id: int, source_tool: str, category: str, description: str):
    item = models.EvidenceItem(
        company_id=company_id,
        source_tool=source_tool,
        category=category,
        description=description,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_evidence(db: Session, company_id: int):
    return (
        db.query(models.EvidenceItem)
        .filter(models.EvidenceItem.company_id == company_id)
        .order_by(models.EvidenceItem.collected_at.desc())
        .all()
    )
