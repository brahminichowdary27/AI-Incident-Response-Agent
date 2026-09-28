from fastapi import APIRouter
from pydantic import BaseModel

from backend.database import SessionLocal
from backend.models import Incident

from backend.agent import (
    HINDSIGHT_URL,
    HINDSIGHT_API_KEY,
    BANK_ID,
    analyze_incident
)
from hindsight_client import Hindsight


router = APIRouter()


class IncidentRequest(BaseModel):
    description: str


class CreateIncidentRequest(BaseModel):
    title: str
    description: str
    severity: str = "medium"


@router.get("/incidents")
def get_incidents():

    db = SessionLocal()

    incidents = db.query(Incident).all()

    result = []

    for incident in incidents:

        result.append({
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "root_cause": incident.root_cause,
            "resolution": incident.resolution,
            "outcome": incident.outcome,
            "status": incident.status
        })

    db.close()

    return result


@router.post("/incidents")
def create_incident(request: CreateIncidentRequest):

    db = SessionLocal()

    incident = Incident(
        title=request.title,
        description=request.description,
        severity=request.severity,
        status="open"
    )

    db.add(incident)

    db.commit()

    db.refresh(incident)

    result = {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status
    }

    db.close()

    return result


@router.post("/analyze")
async def analyze_new_incident(request: IncidentRequest):

    result = await analyze_incident(
        request.description
    )

    return result


@router.put("/incidents/{incident_id}/outcome")
async def update_incident_outcome(
    incident_id: int,
    root_cause: str,
    resolution: str,
    outcome: str
):

    db = SessionLocal()

    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:

        db.close()

        return {
            "error": "Incident not found"
        }

    # Update incident with confirmed operational outcome
    incident.root_cause = root_cause
    incident.resolution = resolution
    incident.outcome = outcome
    incident.status = "resolved"

    db.commit()

    db.refresh(incident)

    # ---------------------------------------------------------
    # Build structured learning memory for Hindsight
    # ---------------------------------------------------------

    post_mortem = f"""
INCIDENT LEARNING RECORD

Incident:
{incident.title}

Description:
{incident.description}

Severity:
{incident.severity}

Confirmed Root Cause:
{incident.root_cause}

Successful Resolution:
{incident.resolution}

Observed Outcome:
{incident.outcome}

Operational Lesson:
Future incidents showing similar symptoms should
consider this incident as historical evidence.

Important Signals:
- Incident type: {incident.title}
- Severity: {incident.severity}
- Root cause pattern: {incident.root_cause}
- Resolution pattern: {incident.resolution}

Learning Status:
Confirmed successful resolution.

This is a confirmed production incident.
The root cause, resolution, and outcome are confirmed
operational knowledge and should be considered when
analyzing future incidents.

Do not treat this memory as proof that the same root
cause exists in a future incident. Use it as historical
evidence and recommend investigation before remediation.
"""

    # ---------------------------------------------------------
    # Store the learned incident in Hindsight
    # ---------------------------------------------------------

    hindsight = Hindsight(
    base_url=HINDSIGHT_URL,
    api_key=HINDSIGHT_API_KEY
)

    try:

        hindsight_result = await hindsight.aretain(
            bank_id=BANK_ID,
            content=post_mortem,
            context="resolved incident post-mortem and operational learning"
        )

        result = {
            "id": incident.id,
            "status": incident.status,
            "root_cause": incident.root_cause,
            "resolution": incident.resolution,
            "outcome": incident.outcome,
            "hindsight_memory_stored": hindsight_result.success
        }

    finally:

        await hindsight.aclose()

        db.close()

    return result