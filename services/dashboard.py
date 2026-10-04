from models import ComplianceObligation


def get_summary(db, org_id):
    obligations = db.query(ComplianceObligation).filter(ComplianceObligation.org_id == org_id).all()

    by_framework = {}
    for o in obligations:
        fw = by_framework.setdefault(o.framework, {"not_started": 0, "in_progress": 0, "met": 0, "at_risk": 0})
        fw[o.status] = fw.get(o.status, 0) + 1

    total = len(obligations)
    met = sum(1 for o in obligations if o.status == "met")
    at_risk = sum(1 for o in obligations if o.status == "at_risk")

    risk_score = round(((total - met) / total) * 100, 1) if total else 0.0

    return {
        "total_obligations": total,
        "met": met,
        "at_risk": at_risk,
        "overall_risk_score": risk_score,
        "by_framework": by_framework,
    }
