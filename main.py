from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import get_db, SessionLocal
from entitlements import require_pro
from frontend import PAGE_HTML
from services import integrations as integrations_service
from services import evidence as evidence_service
from services import documents as documents_service
from services import obligations as obligations_service

app = FastAPI(title="Continuous Compliance Evidence Platform")


# ---------- schemas ----------

class OrgCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    target_markets: Optional[str] = None  # comma-separated, e.g. "EU,CA,VA"


class IntegrationConnect(BaseModel):
    org_id: int
    provider: str
    access_token: str


class DocumentGenerate(BaseModel):
    org_id: int
    doc_type: str
    jurisdiction: str


class ObligationUpdate(BaseModel):
    status: Optional[str] = None
    mark_reviewed: bool = False


# ---------- routes ----------

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(PAGE_HTML)


@app.post("/orgs")
def create_org(payload: OrgCreate, db: Session = Depends(get_db)):
    org = models.Organization(
        name=payload.name,
        industry=payload.industry,
        employee_count=payload.employee_count,
        target_markets=payload.target_markets,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    if payload.target_markets:
        jurisdictions = [j.strip() for j in payload.target_markets.split(",") if j.strip()]
        obligations_service.seed_obligations_for_org(db, org.id, jurisdictions)

    return {
        "id": org.id,
        "name": org.name,
        "industry": org.industry,
        "employee_count": org.employee_count,
        "target_markets": org.target_markets,
        "created_at": org.created_at,
    }


@app.post("/integrations/connect", dependencies=[Depends(require_pro)])
def connect_integration(payload: IntegrationConnect, db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.id == payload.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="organization not found")
    integration = integrations_service.connect_integration(db, payload.org_id, payload.provider, payload.access_token)
    return {
        "id": integration.id,
        "provider": integration.provider,
        "type": integration.type,
        "status": integration.status,
    }


@app.post("/integrations/{id}/sync", dependencies=[Depends(require_pro)])
def sync_integration(id: int, db: Session = Depends(get_db)):
    integration = db.query(models.Integration).filter(models.Integration.id == id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="integration not found")
    try:
        items = integrations_service.sync_integration(db, integration)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"sync failed: {exc}")
    return {"synced_items": len(items), "status": integration.status, "last_synced_at": integration.last_synced_at}


@app.get("/evidence", dependencies=[Depends(require_pro)])
def list_evidence(org_id: int, category: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    items = evidence_service.list_evidence(db, org_id, category, status)
    return [
        {
            "id": i.id,
            "integration_id": i.integration_id,
            "category": i.category,
            "source_data": i.source_data,
            "collected_at": i.collected_at,
            "status": i.status,
        }
        for i in items
    ]


@app.post("/documents/generate", dependencies=[Depends(require_pro)])
def generate_document(payload: DocumentGenerate, db: Session = Depends(get_db)):
    try:
        doc = documents_service.generate_document(db, payload.org_id, payload.doc_type, payload.jurisdiction)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"id": doc.id, "doc_type": doc.doc_type, "jurisdiction": doc.jurisdiction, "version": doc.version, "status": doc.status}


@app.get("/documents/{id}")
def get_document(id: int, db: Session = Depends(get_db)):
    doc = documents_service.get_document(db, id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    return {
        "id": doc.id,
        "doc_type": doc.doc_type,
        "jurisdiction": doc.jurisdiction,
        "content": doc.content,
        "version": doc.version,
        "generated_at": doc.generated_at,
        "status": doc.status,
    }


@app.get("/obligations", dependencies=[Depends(require_pro)])
def list_obligations(org_id: int, jurisdiction: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    items = obligations_service.list_obligations(db, org_id, jurisdiction, status)
    return [
        {
            "id": o.id,
            "jurisdiction": o.jurisdiction,
            "requirement": o.requirement,
            "description": o.description,
            "due_date": o.due_date,
            "status": o.status,
            "last_reviewed_at": o.last_reviewed_at,
        }
        for o in items
    ]


@app.patch("/obligations/{id}", dependencies=[Depends(require_pro)])
def update_obligation(id: int, payload: ObligationUpdate, db: Session = Depends(get_db)):
    obligation = obligations_service.update_obligation(db, id, payload.status, payload.mark_reviewed)
    if not obligation:
        raise HTTPException(status_code=404, detail="obligation not found")
    return {
        "id": obligation.id,
        "status": obligation.status,
        "last_reviewed_at": obligation.last_reviewed_at,
    }


# ---------- background sync scheduler ----------

def _scheduled_sync_all():
    db = SessionLocal()
    try:
        active_integrations = db.query(models.Integration).filter(models.Integration.status != "disabled").all()
        for integration in active_integrations:
            try:
                integrations_service.sync_integration(db, integration)
            except Exception:
                continue
    finally:
        db.close()


scheduler = BackgroundScheduler()
scheduler.add_job(_scheduled_sync_all, "interval", hours=6, id="periodic_evidence_sync")
scheduler.start()
