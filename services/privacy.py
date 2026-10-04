from sqlalchemy.orm import Session
import models


def list_state_obligations(db: Session):
    return db.query(models.StateObligation).all()


def track_obligation(db: Session, company_id: int, state_obligation_id: int, status: str, notes: str = ""):
    track = (
        db.query(models.ObligationTracking)
        .filter(
            models.ObligationTracking.company_id == company_id,
            models.ObligationTracking.state_obligation_id == state_obligation_id,
        )
        .first()
    )
    if track:
        track.status = status
        track.notes = notes
    else:
        track = models.ObligationTracking(
            company_id=company_id,
            state_obligation_id=state_obligation_id,
            status=status,
            notes=notes,
        )
        db.add(track)
    db.commit()
    db.refresh(track)
    return track


def compliance_report(db: Session, company_id: int):
    obligations = db.query(models.StateObligation).all()
    tracks = {
        t.state_obligation_id: t
        for t in db.query(models.ObligationTracking)
        .filter(models.ObligationTracking.company_id == company_id)
        .all()
    }

    report = []
    for ob in obligations:
        track = tracks.get(ob.id)
        report.append(
            {
                "state": ob.state_name,
                "law": ob.law_name,
                "effective_date": ob.effective_date,
                "status": track.status if track else "not_started",
                "notes": track.notes if track else "",
            }
        )
    return report
