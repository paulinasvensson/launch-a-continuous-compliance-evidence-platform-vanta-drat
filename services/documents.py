from datetime import datetime
from jinja2 import Template
from sqlalchemy.orm import Session

import models

TECH_FILE_TEMPLATE = Template(
    """# {{ title }}

## 1. Organization Profile
Name: {{ org_name }}
Industry: {{ industry }}
Employee count: {{ employee_count }}
Jurisdiction covered: {{ jurisdiction }}

## 2. System Overview
This technical file documents the AI system(s) operated by {{ org_name }} and
the controls in place to satisfy {{ jurisdiction }} obligations.

## 3. Evidence Summary
{% for category, items in evidence_by_category.items() %}
### {{ category }}
{% for item in items %}
- [{{ item.source_system }}] {{ item.raw_data }}
{% endfor %}
{% endfor %}
{% if not evidence_by_category %}
No evidence has been collected yet. Connect an integration and sync to populate this section.
{% endif %}

## 4. Risk Management Measures
Access control, encryption, logging, and code/data change-control evidence
collected above constitute the ongoing risk management record.

## 5. Record Keeping
Evidence is collected continuously from connected systems.
Document generated: {{ generated_at }}
"""
)


def generate_document(db: Session, org: models.Organization, doc_type: str, jurisdiction: str):
    evidence = db.query(models.EvidenceItem).filter(models.EvidenceItem.org_id == org.id).all()

    by_category = {}
    for ev in evidence:
        by_category.setdefault(ev.category, []).append(ev)

    generated_at = datetime.utcnow()
    content = TECH_FILE_TEMPLATE.render(
        title=f"{doc_type} - {jurisdiction}",
        org_name=org.name,
        industry=org.industry,
        employee_count=org.employee_count,
        jurisdiction=jurisdiction,
        evidence_by_category=by_category,
        generated_at=generated_at.isoformat(),
    )

    doc = models.ComplianceDocument(
        org_id=org.id,
        doc_type=doc_type,
        jurisdiction=jurisdiction,
        title=f"{doc_type} - {jurisdiction}",
        content=content,
        status="generated",
        generated_at=generated_at,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
