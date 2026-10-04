from datetime import datetime
from sqlalchemy.orm import Session
from models import TechnicalDocSection, EvidenceItem, Obligation

ANNEX_IV_SECTIONS = [
    ("System Overview", "General description of the AI system, its purpose and intended use."),
    ("Development Process", "Description of methods, design choices, and development lifecycle."),
    ("Data Governance", "Description of training, validation and testing datasets and data governance measures."),
    ("Risk Management", "Description of the risk management system and mitigation measures applied."),
    ("Human Oversight", "Description of human oversight measures built into the system."),
    ("Accuracy & Robustness", "Metrics used to assess accuracy, robustness, and cybersecurity."),
    ("Monitoring & Change Log", "Post-market monitoring plan and log of changes made to the system."),
]


def generate_techdoc(db: Session, org_id: int):
    """Auto-generate/refresh the EU AI Act Annex IV technical documentation
    by aggregating stored evidence linked to EU_AI_ACT obligations."""
    ai_act_obligation_ids = [
        o.id for o in db.query(Obligation).filter(Obligation.jurisdiction == "EU_AI_ACT").all()
    ]
    evidence = (
        db.query(EvidenceItem)
        .filter(EvidenceItem.org_id == org_id, EvidenceItem.obligation_id.in_(ai_act_obligation_ids))
        .all()
    )

    existing = {
        s.section_name: s
        for s in db.query(TechnicalDocSection).filter(TechnicalDocSection.org_id == org_id).all()
    }

    sections = []
    for name, template in ANNEX_IV_SECTIONS:
        related = [e for e in evidence if name.lower().split()[0] in (e.name.lower() + e.source.lower())]
        body = template + "\n\nEvidence considered:\n"
        if related:
            body += "\n".join(f"- [{e.source}] {e.name}: {e.content[:200]}" for e in related)
        else:
            body += "- No evidence yet ingested for this section."

        section = existing.get(name)
        if not section:
            section = TechnicalDocSection(org_id=org_id, section_name=name)
            db.add(section)
        section.content = body
        section.updated_at = datetime.utcnow()
        sections.append(section)

    db.commit()
    for s in sections:
        db.refresh(s)

    return [
        {"section_name": s.section_name, "content": s.content, "updated_at": s.updated_at.isoformat()}
        for s in sections
    ]


def get_techdoc(db: Session, org_id: int):
    sections = (
        db.query(TechnicalDocSection)
        .filter(TechnicalDocSection.org_id == org_id)
        .order_by(TechnicalDocSection.id)
        .all()
    )
    return [
        {"section_name": s.section_name, "content": s.content, "updated_at": s.updated_at.isoformat()}
        for s in sections
    ]
