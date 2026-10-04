from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    employee_count = Column(Integer, nullable=True)
    states_operating = Column(JSON, default=list)
    sells_in_eu = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    integrations = relationship("Integration", backref="organization")
    obligations = relationship("ComplianceObligation", backref="organization")
    evidence_items = relationship("EvidenceItem", backref="organization")
    documents = relationship("TechnicalDocument", backref="organization")


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    provider = Column(String, nullable=False)  # aws, gcp, azure, github, bamboohr, rippling
    type = Column(String, nullable=False)  # cloud | dev | hr
    status = Column(String, default="connected")
    last_synced_at = Column(DateTime, nullable=True)
    access_token_encrypted = Column(String, nullable=True)


class ObligationRule(Base):
    """Structured reference data for compliance rules. Seeded, not hardcoded in endpoints."""
    __tablename__ = "obligation_rules"

    id = Column(Integer, primary_key=True, index=True)
    framework = Column(String, nullable=False)  # eu_ai_act | us_state_privacy
    state_or_region = Column(String, nullable=False)  # EU, CA, CO, CT, VA, UT, etc
    requirement_text = Column(Text, nullable=False)
    due_date = Column(Date, nullable=True)


class ComplianceObligation(Base):
    __tablename__ = "compliance_obligations"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    framework = Column(String, nullable=False)
    state_or_region = Column(String, nullable=False)
    requirement_text = Column(Text, nullable=False)
    status = Column(String, default="not_started")  # not_started|in_progress|met|at_risk
    due_date = Column(Date, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    obligation_id = Column(Integer, ForeignKey("compliance_obligations.id"), nullable=True)
    source_integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=True)
    type = Column(String, nullable=False)  # policy|log|config|screenshot|attestation
    content_ref = Column(Text, nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow)
    is_current = Column(Boolean, default=True)


class TechnicalDocument(Base):
    __tablename__ = "technical_documents"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    doc_type = Column(String, nullable=False)  # eu_ai_act_technical_file|dpia|state_privacy_notice
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    generated_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="draft")  # draft|final


def seed_if_empty(db):
    if db.query(ObligationRule).first():
        return

    rules = [
        ObligationRule(
            framework="eu_ai_act",
            state_or_region="EU",
            requirement_text="Establish and maintain a risk management system for the AI system across its lifecycle.",
            due_date=date(2026, 8, 2),
        ),
        ObligationRule(
            framework="eu_ai_act",
            state_or_region="EU",
            requirement_text="Compile technical documentation demonstrating conformity with AI Act requirements before placing on market.",
            due_date=date(2026, 8, 2),
        ),
        ObligationRule(
            framework="eu_ai_act",
            state_or_region="EU",
            requirement_text="Implement data governance measures ensuring training, validation and testing data quality.",
            due_date=date(2026, 8, 2),
        ),
        ObligationRule(
            framework="eu_ai_act",
            state_or_region="EU",
            requirement_text="Enable human oversight measures appropriate to the risk level of the AI system.",
            due_date=date(2026, 8, 2),
        ),
        ObligationRule(
            framework="eu_ai_act",
            state_or_region="EU",
            requirement_text="Maintain automatically generated logs for traceability of AI system operation.",
            due_date=date(2026, 8, 2),
        ),
        ObligationRule(
            framework="us_state_privacy",
            state_or_region="CA",
            requirement_text="Provide notice of automated decision-making technology use and opt-out rights (CCPA/CPRA ADMT rules).",
            due_date=date(2026, 1, 1),
        ),
        ObligationRule(
            framework="us_state_privacy",
            state_or_region="CO",
            requirement_text="Conduct data protection assessments for profiling that presents heightened risk of harm.",
            due_date=date(2026, 7, 1),
        ),
        ObligationRule(
            framework="us_state_privacy",
            state_or_region="CT",
            requirement_text="Provide consumers a mechanism to opt out of profiling in furtherance of solely automated decisions.",
            due_date=date(2026, 7, 1),
        ),
        ObligationRule(
            framework="us_state_privacy",
            state_or_region="VA",
            requirement_text="Conduct and document data protection assessments for high-risk processing activities.",
            due_date=date(2026, 1, 1),
        ),
        ObligationRule(
            framework="us_state_privacy",
            state_or_region="UT",
            requirement_text="Disclose use of AI/automated profiling in consumer-facing privacy notice.",
            due_date=date(2026, 1, 1),
        ),
        ObligationRule(
            framework="us_state_privacy",
            state_or_region="TX",
            requirement_text="Provide clear notice and opt-out for sale of personal data used to train AI models.",
            due_date=date(2026, 1, 1),
        ),
    ]
    db.add_all(rules)
    db.commit()
