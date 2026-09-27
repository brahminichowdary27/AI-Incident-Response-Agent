from database import SessionLocal
from models import Incident


db = SessionLocal()

incidents = db.query(Incident).all()

for incident in incidents:
    print("ID:", incident.id)
    print("Title:", incident.title)
    print("Severity:", incident.severity)
    print("Status:", incident.status)
    print("Root Cause:", incident.root_cause)
    print("Resolution:", incident.resolution)
    print("Outcome:", incident.outcome)
    print("-" * 50)

db.close()