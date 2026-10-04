from datetime import datetime
from sqlalchemy.orm import Session

import models
from services.connectors import get_connector


def sync_integration(db: Session, integration: models.Integration):
    connector = get_connector(integration.provider)
    fetched = connector.fetch_evidence()

    created = []
    for item in fetched:
        evidence = models.EvidenceItem(
            org_id=integration.org_id,
            integration_id=integration.id,
            category=item["category"],
            source_system=item["source_system"],
            raw_data=item["raw_data"],
        )
        db.add(evidence)
        created.append(evidence)

    integration.status = "active"
    integration.last_synced_at = datetime.utcnow()

    db.commit()
    for evidence in created:
        db.refresh(evidence)

    return created
