from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from entitlements import require_pro
from frontend import PAGE_HTML

from models import Organization, Integration, ComplianceObligation, TechnicalDocument
from services import orgs as orgs_service
from services import integrations as integrations_service
from services import obligations as obligations_service
from services import documents as documents_service
from services import dashboard as dashboard_service

app = FastAPI(title="Continuous AI & Privacy Compliance Evidence Platform")


# ---------- Schemas ----------

class OrgCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    states_operating: List[str] = []
    sells_in_eu: bool = False


class IntegrationConnect(BaseModel):
    org_id: int
    provider: str
    type: str
    access_token: Optional[str] = None


class DocumentGenerate(BaseModel):
    org_id: int
    doc_type: str


# ---------- Routes ----------

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(PAGE_HTML)


@app.post("/orgs")
def create_org(payload: OrgCreate, db: Session = Depends(get_db)):
    org = orgs_service.create_organization(
        db,
        name=payload.name,
        industry=payload.industry,
        employee_count=payload.employee_count,
        states_operating=payload.states_operating,
        sells_in_eu=payload.sells_in_eu,
    )
    return {
        "id": org.id,
        "name": org.name,
        "industry": org.industry,
        "employee_count": org.employee_count,
        "states_operating": org.states_operating,
        "sells_in_eu": org.sells_in_eu,
        "created_at": org.created_at,
    }


@app.post("/integrations/connect", dependencies=[Depends(require_pro)])
def connect_integration(payload: IntegrationConnect, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == payload.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    integration = integrations_service.connect_integration(
        db, org.id, payload.provider, payload.type, payload.access_token
    )
    return {
        "id": integration.id,
        "org_id": integration.org_id,
        "provider": integration.provider,
        "type": integration.type,
        "status": integration.status,
    }


@app.post("/integrations/{integration_id}/sync", dependencies=[Depends(require_pro)])
def sync_integration(integration_id: int, db: Session = Depends(get_db)):
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    evidence = integrations_service.sync_integration(db, integration_id)
    return {
        "integration_id": integration_id,
        "evidence_collected": len(evidence) if evidence else 0,
        "items": [
            {"id": e.id, "type": e.type, "content_ref": e.content_ref, "obligation_id": e.obligation_id}
            for e in (evidence or [])
        ],
    }


@app.get("/obligations")
def list_obligations(org_id: int, db: Session = Depends(get_db)):
    obligations = obligations_service.list_obligations(db, org_id)
    return [
        {
            "id": o.id,
            "framework": o.framework,
            "state_or_region": o.state_or_region,
            "requirement_text": o.requirement_text,
            "status": o.status,
            "due_date": o.due_date,
            "last_checked_at": o.last_checked_at,
        }
        for o in obligations
    ]


@app.get("/obligations/{obligation_id}/evidence", dependencies=[Depends(require_pro)])
def get_obligation_evidence(obligation_id: int, db: Session = Depends(get_db)):
    obligation = db.query(ComplianceObligation).filter(ComplianceObligation.id == obligation_id).first()
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    evidence = obligations_service.list_evidence_for_obligation(db, obligation_id)
    return [
        {
            "id": e.id,
            "type": e.type,
            "content_ref": e.content_ref,
            "collected_at": e.collected_at,
            "is_current": e.is_current,
            "source_integration_id": e.source_integration_id,
        }
        for e in evidence
    ]


@app.post("/documents/generate", dependencies=[Depends(require_pro)])
def generate_document(payload: DocumentGenerate, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == payload.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    doc = documents_service.generate_document(db, org, payload.doc_type)
    return {
        "id": doc.id,
        "doc_type": doc.doc_type,
        "title": doc.title,
        "version": doc.version,
        "status": doc.status,
        "generated_at": doc.generated_at,
    }


@app.get("/documents/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc, history = documents_service.get_document_with_history(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "doc_type": doc.doc_type,
        "title": doc.title,
        "content": doc.content,
        "version": doc.version,
        "status": doc.status,
        "generated_at": doc.generated_at,
        "version_history": [
            {"id": h.id, "version": h.version, "status": h.status, "generated_at": h.generated_at}
            for h in history
        ],
    }


@app.get("/dashboard/summary")
def dashboard_summary(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return dashboard_service.get_summary(db, org_id)
