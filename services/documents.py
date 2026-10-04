import json
from datetime import datetime, timezone

from jinja2 import Template
from sqlalchemy.orm import Session

import models

# Versioned, editable templates. In production these would live in a
# dedicated template store/CMS; kept as data here, not hardcoded logic.
TEMPLATES = {
    "eu_ai_act_technical_file": {
        "version": 1,
        "jinja": """
EU AI Act Technical Documentation
Organization: {{ org_name }}
Generated: {{ generated_at }}

1. General description of the AI system
   Industry: {{ industry }}
   Employee count: {{ employee_count }}

2. Risk management evidence
{% for e in access_control %}   - [{{ e.collected_at }}] {{ e.data }}
{% endfor %}

3. Data governance & model evidence
{% for e in model_card %}   - [{{ e.collected_at }}] {{ e.data }}
{% endfor %}

4. Human oversight / training evidence
{% for e in hr_training %}   - [{{ e.collected_at }}] {{ e.data }}
{% endfor %}
""",
    },
    "us_state_checklist": {
        "version": 1,
        "jinja": """
US State Privacy-Law Obligation Checklist
Organization: {{ org_name }}
Jurisdiction: {{ jurisdiction }}
Generated: {{ generated_at }}

Evidence collected:
{% for cat, items in evidence_by_category.items() %}  {{ cat }}:
{% for e in items %}    - [{{ e.collected_at }}] {{ e.data }}
{% endfor %}{% endfor %}
""",
    },
}


def _grouped_evidence(db: Session, org_id: int):
    items = db.query(models.EvidenceItem).filter(models.EvidenceItem.org_id == org_id).all()
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(item.category, []).append(
            {"collected_at": item.collected_at.isoformat() if item.collected_at else "", "data": json.loads(item.source_data or "{}")}
        )
    return grouped


def generate_document(db: Session, org_id: int, doc_type: str, jurisdiction: str) -> models.ComplianceDocument:
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        raise ValueError("organization not found")

    template_def = TEMPLATES.get(doc_type)
    if not template_def:
        raise ValueError(f"unknown doc_type: {doc_type}")

    grouped = _grouped_evidence(db, org_id)
    now = datetime.now(timezone.utc).isoformat()

    template = Template(template_def["jinja"])
    content = template.render(
        org_name=org.name,
        industry=org.industry,
        employee_count=org.employee_count,
        jurisdiction=jurisdiction,
        generated_at=now,
        access_control=grouped.get("access_control", []),
        model_card=grouped.get("model_card", []),
        hr_training=grouped.get("hr_training", []),
        evidence_by_category=grouped,
    )

    previous = (
        db.query(models.ComplianceDocument)
        .filter(
            models.ComplianceDocument.org_id == org_id,
            models.ComplianceDocument.doc_type == doc_type,
            models.ComplianceDocument.jurisdiction == jurisdiction,
        )
        .order_by(models.ComplianceDocument.version.desc())
        .first()
    )
    next_version = (previous.version + 1) if previous else 1

    doc = models.ComplianceDocument(
        org_id=org_id,
        doc_type=doc_type,
        jurisdiction=jurisdiction,
        content=content,
        version=next_version,
        status="draft",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, doc_id: int) -> models.ComplianceDocument | None:
    return db.query(models.ComplianceDocument).filter(models.ComplianceDocument.id == doc_id).first()
