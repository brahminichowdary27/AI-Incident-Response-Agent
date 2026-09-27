from hindsight_client import Hindsight


HINDSIGHT_URL = "http://localhost:8888"
BANK_ID = "incident-response-final"


historical_incidents = [

    {
        "title": "Payment API returning 503 errors",
        "content": """
Incident: Payment API returning 503 errors

Symptoms:
The payment API experienced a sudden increase in HTTP 503 errors.
CPU usage reached approximately 92% and database connections were
close to the configured connection limit.

Root Cause:
Database connection pool exhaustion.

Resolution:
The database connection pool was increased from 100 to 200.
Affected application pods were restarted.

Outcome:
HTTP 503 errors dropped from approximately 42% to below 1%.
The payment service recovered successfully.

Operational Learning:
When payment APIs experience 503 errors together with high
database connection utilization, investigate database connection
pool exhaustion and connection limits before making unrelated
changes.
"""
    },

    {
        "title": "User login failures after deployment",
        "content": """
Incident: User login failures after deployment

Symptoms:
Users were unable to log in after a production deployment.
Authentication requests were failing consistently.

Root Cause:
Incorrect authentication configuration values were deployed.

Resolution:
The authentication environment variables were corrected and
the affected application services were redeployed.

Outcome:
User authentication returned to normal.

Operational Learning:
When authentication fails immediately after a deployment,
check authentication configuration and environment variables
before changing application logic.
"""
    },

    {
        "title": "Order processing extremely slow",
        "content": """
Incident: Order processing extremely slow

Symptoms:
Order processing latency increased significantly.
Application CPU utilization became very high.

Root Cause:
An inefficient background processing job caused excessive
CPU consumption.

Resolution:
The problematic background job was stopped and the processing
logic was optimized.

Outcome:
CPU utilization returned to normal and order processing latency
decreased significantly.

Operational Learning:
When application latency increases together with high CPU usage,
investigate background jobs and resource-intensive processes.
"""
    },

    {
        "title": "Database queries timing out",
        "content": """
Incident: Database queries timing out

Symptoms:
Database queries were taking too long to complete and API
requests were experiencing timeouts.

Root Cause:
A frequently queried database column was missing an appropriate
database index.

Resolution:
The required database index was added and affected application
services were restarted.

Outcome:
Database query performance returned to normal and API timeouts
were resolved.

Operational Learning:
When database queries consistently become slow or time out,
inspect query performance and database indexes before increasing
application resources.
"""
    },

    {
        "title": "Notification service stopped sending messages",
        "content": """
Incident: Notification service stopped sending messages

Symptoms:
The notification service stopped delivering messages to users.

Root Cause:
The notification worker process was not running.

Resolution:
The notification worker was restarted and an additional worker
health check was configured.

Outcome:
Notification delivery resumed successfully.

Operational Learning:
When asynchronous notifications stop being delivered,
check worker process health and background worker availability.
"""
    }
]


def seed_hindsight():

    hindsight = Hindsight(
        base_url=HINDSIGHT_URL
    )

    try:

        for incident in historical_incidents:

            print(
                f"Storing: {incident['title']}"
            )

            result = hindsight.retain(
                bank_id=BANK_ID,
                content=incident["content"],
                context="historical incident post-mortem"
            )

            print(
                f"Stored successfully: {result.success}"
            )

        print()
        print("========================================")
        print("Hindsight historical memory seeded.")
        print(f"Bank: {BANK_ID}")
        print(f"Incidents stored: {len(historical_incidents)}")
        print("========================================")

    finally:

        hindsight.close()


if __name__ == "__main__":
    seed_hindsight()