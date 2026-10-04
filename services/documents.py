import os
from datetime import datetime
from models import TechnicalDocument, ComplianceObligation, EvidenceItem

DOC_TITLES = {
    "eu_ai_act_technical_file": "EU AI Act Technical Documentation",
    "dpia": "Data Protection Impact Assessment",
    "state_privacy_notice": "US State Privacy Notice Summary",
}


def _build_draft_content(org, obligations, evidence_items, doc_type):
    """Template-based draft, enriched with an LLM call if OPENAI_API_KEY is set."""
    sections = [f"# {DOC_TITLES.get(doc_type, doc_type)}", f"Organization: {org.name}", ""]

    sections.append("## Obligations Covered")
    for o in obligations:
        sections.append(f"- [{o.status}] ({o.state_or_region}) {o.requirement_text}")

    sections.append("")
    sections.append("## Supporting Evidence")
    for e in evidence_items:
        sections.append(f"- ({e.type}) {e.content_ref}")

    draft_text = "\n".join(sections)

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            prompt = (
                "Draft a concise, professional compliance document section based on the "
                f"following structured evidence and obligations for document type '{doc_type}'. "
                "Keep it factual and editable:\n\n" + draft_text
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            generated = response.choices[0].message.content
            if generated:
                return generated
        except Exception:
            pass

    return draft_text


def generate_document(db, org, doc_type):
    """Idempotent + versioned: never overwrites prior drafts, creates a new version."""
    obligations = db.query(ComplianceObligation).filter(ComplianceObligation.org_id == org.id).all()
    evidence_items = db.query(EvidenceItem).filter(
        EvidenceItem.org_id == org.id, EvidenceItem.is_current == True  # noqa: E712
    ).all()

    content = _build_draft_content(org, obligations, evidence_items, doc_type)

    latest = (
        db.query(TechnicalDocument)
        .filter(TechnicalDocument.org_id == org.id, TechnicalDocument.doc_type == doc_type)
        .order_by(TechnicalDocument.version.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1

    doc = TechnicalDocument(
        org_id=org.id,
        doc_type=doc_type,
        title=DOC_TITLES.get(doc_type, doc_type),
        content=content,
        version=next_version,
        status="draft",
        generated_at=datetime.utcnow(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document_with_history(db, doc_id):
    doc = db.query(TechnicalDocument).filter(TechnicalDocument.id == doc_id).first()
    if not doc:
        return None, []
    history = (
        db.query(TechnicalDocument)
        .filter(TechnicalDocument.org_id == doc.org_id, TechnicalDocument.doc_type == doc.doc_type)
        .order_by(TechnicalDocument.version.asc())
        .all()
    )
    return doc, history
