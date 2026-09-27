from database import SessionLocal
from models import Incident


db = SessionLocal()

incident = Incident(
    title="Payment API returning 503 errors",
    description=(
        "Payment API experienced a sudden increase in HTTP 503 errors. "
        "CPU usage reached 92% and database connections were close to the configured limit."
    ),
    severity="high",
    root_cause="Database connection pool exhaustion",
    resolution=(
        "Increased the database connection pool from 100 to 200 "
        "and restarted the affected application pods."
    ),
    outcome=(
        "HTTP 503 errors dropped from approximately 42% to below 1% "
        "and the payment service recovered."
    ),
    status="resolved"
)

db.add(incident)
db.commit()
db.refresh(incident)

print(f"Incident created with ID: {incident.id}")

db.close()