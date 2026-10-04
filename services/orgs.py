from models import Organization, ObligationRule, ComplianceObligation


def create_organization(db, name, industry, employee_count, states_operating, sells_in_eu):
    org = Organization(
        name=name,
        industry=industry,
        employee_count=employee_count,
        states_operating=states_operating or [],
        sells_in_eu=bool(sells_in_eu),
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    _generate_obligations_for_org(db, org)
    return org


def _generate_obligations_for_org(db, org):
    rules = db.query(ObligationRule).all()
    for rule in rules:
        applies = False
        if rule.framework == "eu_ai_act" and org.sells_in_eu:
            applies = True
        if rule.framework == "us_state_privacy" and rule.state_or_region in (org.states_operating or []):
            applies = True
        if applies:
            obligation = ComplianceObligation(
                org_id=org.id,
                framework=rule.framework,
                state_or_region=rule.state_or_region,
                requirement_text=rule.requirement_text,
                status="not_started",
                due_date=rule.due_date,
            )
            db.add(obligation)
    db.commit()
