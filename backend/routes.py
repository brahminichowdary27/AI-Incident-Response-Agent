from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

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


# =========================================================
# REQUEST MODELS
# =========================================================

class IncidentRequest(BaseModel):
    description: str


class CreateIncidentRequest(BaseModel):
    title: str
    description: str
    severity: str = "medium"


# =========================================================
# DATABASE HELPER
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        return db
    except Exception:
        db.close()
        raise


# =========================================================
# GET INCIDENTS
# =========================================================

@router.get("/incidents")
def get_incidents():

    db: Session = get_db()

    try:
        incidents = (
            db.query(Incident)
            .order_by(Incident.id.desc())
            .all()
        )

        return incidents

    finally:
        db.close()


# =========================================================
# CREATE INCIDENT
# =========================================================

@router.post("/incidents")
def create_incident(request: CreateIncidentRequest):

    db: Session = get_db()

    try:

        incident = Incident(
            title=request.title,
            description=request.description,
            severity=request.severity,
            status="open"
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status
        }

    finally:
        db.close()


# =========================================================
# ANALYZE NEW INCIDENT
# =========================================================

@router.post("/analyze")
async def analyze_new_incident(request: IncidentRequest):

    try:

        result = await analyze_incident(
            request.description
        )

        return result

    except Exception as e:

        print(
            "ANALYZE ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Incident analysis failed."
        )


# =========================================================
# UPDATE INCIDENT OUTCOME
# =========================================================

@router.put("/incidents/{incident_id}/outcome")
async def update_incident_outcome(
    incident_id: int,
    root_cause: str,
    resolution: str,
    outcome: str
):

    db: Session = get_db()

    try:

        # ---------------------------------------------
        # 1. Find incident
        # ---------------------------------------------

        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if not incident:

            raise HTTPException(
                status_code=404,
                detail="Incident not found."
            )


        # ---------------------------------------------
        # 2. Update local incident record
        # ---------------------------------------------

        incident.root_cause = root_cause
        incident.resolution = resolution
        incident.outcome = outcome
        incident.status = "resolved"

        db.commit()
        db.refresh(incident)


        # ---------------------------------------------
        # 3. Store learning in Hindsight Cloud
        # ---------------------------------------------

        if not HINDSIGHT_API_KEY:

            raise HTTPException(
                status_code=500,
                detail="HINDSIGHT_API_KEY is not configured."
            )


        hindsight = Hindsight(
            base_url=HINDSIGHT_URL,
            api_key=HINDSIGHT_API_KEY
        )


        try:

            memory_content = f"""
Incident Response Post-Mortem

Incident ID:
{incident.id}

Title:
{incident.title}

Description:
{incident.description}

Severity:
{incident.severity}

Root Cause:
{root_cause}

Resolution:
{resolution}

Outcome:
{outcome}

Status:
Resolved

This is confirmed incident-response knowledge that
can be used to improve future incident analysis.
"""


            retain_result = await hindsight.aretain(
                bank_id=BANK_ID,
                content=memory_content,
                context="incident response post-mortem"
            )


        finally:

            await hindsight.aclose()


        # ---------------------------------------------
        # 4. Return result
        # ---------------------------------------------

        return {
            "message": "Incident resolved and learned by Hindsight.",
            "incident_id": incident.id,
            "status": incident.status,
            "hindsight_stored": retain_result.success
        }


    except HTTPException:

        db.rollback()
        raise


    except Exception as e:

        db.rollback()

        print(
            "OUTCOME ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update incident outcome."
        )


    finally:

        db.close()