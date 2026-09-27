from fastapi import APIRouter
from pydantic import BaseModel

from backend.database import SessionLocal
from backend.models import Incident

from backend.agent import (
    HINDSIGHT_URL,
    BANK_ID,
    analyze_incident
)

from hindsight_client import Hindsight


router = APIRouter()


# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------

class IncidentRequest(BaseModel):
    description: str


class CreateIncidentRequest(BaseModel):
    title: str
    description: str
    severity: str = "medium"


# ---------------------------------------------------------
# GET ALL INCIDENTS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# CREATE NEW INCIDENT
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# ANALYZE INCIDENT
# ---------------------------------------------------------

@router.post("/analyze")
async def analyze_new_incident(request: IncidentRequest):

    result = await analyze_incident(
        request.description
    )

    return result


# ---------------------------------------------------------
# RESOLVE INCIDENT + STORE POST-MORTEM IN HINDSIGHT
# ---------------------------------------------------------

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

    # Update database
    incident.root_cause = root_cause
    incident.resolution = resolution
    incident.outcome = outcome
    incident.status = "resolved"

    db.commit()

    db.refresh(incident)

    # -----------------------------------------------------
    # Build post-mortem
    # -----------------------------------------------------

    post_mortem = f"""
Incident: {incident.title}

Description:
{incident.description}

Severity:
{incident.severity}

Root Cause:
{incident.root_cause}

Resolution:
{incident.resolution}

Outcome:
{incident.outcome}

Status:
Resolved

This incident is a confirmed production incident.

The root cause, resolution, and outcome are confirmed
operational knowledge and should be considered when
analyzing future incidents.
"""

    # -----------------------------------------------------
    # Store learning in Hindsight
    # -----------------------------------------------------

    hindsight = Hindsight(
        base_url=HINDSIGHT_URL
    )

    try:

        hindsight_result = await hindsight.aretain(
            bank_id=BANK_ID,
            content=post_mortem,
            context="resolved incident post-mortem"
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