from datetime import datetime
from sqlalchemy.orm import Session

import models

EU_AI_ACT_DEADLINE = datetime(2026, 8, 2)
US_STATE_DEADLINE = datetime(2026, 1, 1)

EU_AI_ACT_REQUIREMENTS = [
    "Maintain technical documentation for high-risk AI systems (Annex IV)",
    "Implement risk management system across AI lifecycle",
    "Ensure data governance and data quality for training datasets",
    "Enable human oversight measures for AI system operation",
    "Log system events (automatically generated logs) for traceability",
    "Register high-risk AI system in EU database",
]

US_STATE_PRIVACY_REQUIREMENTS = {
    "CA": [
        "Honor consumer opt-out of sale/sharing (CCPA/CPRA)",
        "Conduct risk assessments for automated decision-making",
    ],
    "VA": [
        "Provide consumer right to opt out of profiling (VCDPA)",
        "Complete data protection assessments for targeted advertising",
    ],
    "CO": [
        "Honor universal opt-out mechanism (Colorado Privacy Act)",
        "Conduct data protection assessments for high-risk processing",
    ],
    "CT": [
        "Provide consumer right to correct inaccurate personal data (CTDPA)",
    ],
    "UT": [
        "Disclose categories of personal data sold or used for targeted ads (UCPA)",
    ],
    "TX": [
        "Honor opt-out of sale of personal data and targeted advertising (TDPSA)",
    ],
}


def seed_default_obligations(db: Session, org: models.Organization):
    markets = [m.strip().upper() for m in (org.target_markets or "").split(",") if m.strip()]
    obligations = []

    if "EU" in markets:
        for requirement in EU_AI_ACT_REQUIREMENTS:
            obligations.append(models.Obligation(
                org_id=org.id,
                jurisdiction="EU",
                regulation="EU AI Act",
                requirement=requirement,
                due_date=EU_AI_ACT_DEADLINE,
                evidence_ids=[],
            ))

    for state in markets:
        requirements = US_STATE_PRIVACY_REQUIREMENTS.get(state)
        if requirements:
            for requirement in requirements:
                obligations.append(models.Obligation(
                    org_id=org.id,
                    jurisdiction=state,
                    regulation=f"{state} Privacy Law",
                    requirement=requirement,
                    due_date=US_STATE_DEADLINE,
                    evidence_ids=[],
                ))

    if obligations:
        db.add_all(obligations)
        db.commit()
        for ob in obligations:
            db.refresh(ob)

    return obligations
