from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    employee_count = Column(Integer, nullable=True)
    target_markets = Column(String, nullable=True)  # comma-separated e.g. "EU,CA,CO"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    integrations = relationship("Integration", backref="organization")
    evidence_items = relationship("EvidenceItem", backref="organization")
    documents = relationship("ComplianceDocument", backref="organization")
    obligations = relationship("Obligation", backref="organization")


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    provider = Column(String, nullable=False)  # aws, gcp, azure, github, gitlab, bamboohr, gusto
    type = Column(String, nullable=False)  # cloud, dev, hr
    status = Column(String, default="pending")  # pending, active, error
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    access_token_encrypted = Column(Text, nullable=True)


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    category = Column(String, nullable=False)  # access_control, data_retention, model_card, hr_training, etc
    source_data = Column(Text, nullable=True)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="collected")


class ComplianceDocument(Base):
    __tablename__ = "compliance_documents"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    doc_type = Column(String, nullable=False)  # eu_ai_act_technical_file, us_state_checklist
    jurisdiction = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="draft")


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    jurisdiction = Column(String, nullable=False)
    requirement = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="open")  # open, in_progress, met, overdue
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
