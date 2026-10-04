from sqlalchemy.orm import Session
import models

RISK_RULES = {
    "unacceptable": "This system falls into a prohibited category under the EU AI Act and must not be deployed as-is.",
    "high": "This system is classified as high-risk and requires a full technical file: risk management system, data governance, logging, human oversight, and conformity assessment.",
    "limited": "This system carries transparency obligations: users must be informed they are interacting with an AI system.",
    "minimal": "This system has minimal risk obligations under the EU AI Act; voluntary codes of conduct are recommended.",
}


def generate_technical_documentation(db: Session, ai_system: models.AISystem) -> models.TechnicalDocument:
    risk_note = RISK_RULES.get(ai_system.risk_category, RISK_RULES["minimal"])

    sections = [
        f"# EU AI Act Technical Documentation: {ai_system.name}",
        "",
        "## 1. General Description",
        ai_system.description or "No description provided.",
        "",
        "## 2. Intended Purpose",
        ai_system.purpose or "Not specified.",
        "",
        "## 3. Risk Classification",
        f"Classified risk category: **{ai_system.risk_category}**",
        risk_note,
        "",
        "## 4. Data Governance",
        "Training, validation, and test data sources should be documented here; evidence ingested from connected systems supplements this section.",
        "",
        "## 5. Human Oversight Measures",
        "Describe the human oversight mechanisms in place for this system.",
        "",
        "## 6. Record-Keeping and Logging",
        "Automated logging of system operation is required for high-risk systems per Article 12.",
        "",
        "## 7. Conformity Assessment Status",
        f"Current status: {ai_system.status}",
    ]
    content = "\n".join(sections)

    existing_count = (
        db.query(models.TechnicalDocument)
        .filter(models.TechnicalDocument.ai_system_id == ai_system.id)
        .count()
    )

    doc = models.TechnicalDocument(
        ai_system_id=ai_system.id,
        content=content,
        version=existing_count + 1,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
