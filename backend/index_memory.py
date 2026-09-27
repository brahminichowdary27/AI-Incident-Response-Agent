from database import SessionLocal
from models import Incident
from vector_store import add_incident


db = SessionLocal()

incidents = db.query(Incident).all()

for incident in incidents:
    add_incident(
        incident_id=incident.id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        root_cause=incident.root_cause,
        resolution=incident.resolution,
        outcome=incident.outcome
    )

    print(f"Indexed incident {incident.id}: {incident.title}")

db.close()

print("All incidents indexed into ChromaDB.")