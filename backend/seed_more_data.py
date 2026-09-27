from database import SessionLocal
from models import Incident


db = SessionLocal()

incidents = [
    Incident(
        title="User login failures after deployment",
        description=(
            "Users were unable to log in after a new application deployment. "
            "Authentication requests returned HTTP 401 errors."
        ),
        severity="high",
        root_cause="Incorrect authentication configuration after deployment",
        resolution=(
            "Corrected the authentication environment variables "
            "and redeployed the affected service."
        ),
        outcome=(
            "Login success rate returned to normal and HTTP 401 errors "
            "dropped to near zero."
        ),
        status="resolved"
    ),

    Incident(
        title="Order processing became extremely slow",
        description=(
            "Order processing latency increased significantly. "
            "The application showed high CPU usage and requests were timing out."
        ),
        severity="medium",
        root_cause="CPU saturation caused by an inefficient background job",
        resolution=(
            "Stopped the problematic background job and optimized "
            "the processing logic."
        ),
        outcome=(
            "CPU utilization returned to normal and order processing "
            "latency decreased significantly."
        ),
        status="resolved"
    ),

    Incident(
        title="Database queries timing out",
        description=(
            "Multiple API requests experienced database query timeouts. "
            "Database CPU usage was high and query execution time increased."
        ),
        severity="high",
        root_cause="Missing database index on a frequently queried column",
        resolution=(
            "Added the required database index and restarted the affected "
            "application instances."
        ),
        outcome=(
            "Query execution time returned to normal and API timeout errors "
            "were resolved."
        ),
        status="resolved"
    ),

    Incident(
        title="Notification service stopped sending messages",
        description=(
            "Users stopped receiving email notifications even though "
            "notification requests were being generated successfully."
        ),
        severity="medium",
        root_cause="Notification worker process was not running",
        resolution=(
            "Restarted the notification worker and added a process health check."
        ),
        outcome=(
            "Pending notifications were processed successfully and new "
            "notifications were delivered normally."
        ),
        status="resolved"
    )
]

db.add_all(incidents)
db.commit()

for incident in incidents:
    db.refresh(incident)
    print(f"Incident created with ID: {incident.id}")

db.close()