from models import ComplianceObligation, EvidenceItem


def list_obligations(db, org_id):
    return db.query(ComplianceObligation).filter(ComplianceObligation.org_id == org_id).all()


def list_evidence_for_obligation(db, obligation_id):
    return db.query(EvidenceItem).filter(EvidenceItem.obligation_id == obligation_id).all()
