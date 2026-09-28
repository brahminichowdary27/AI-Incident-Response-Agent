import json
import os

from dotenv import load_dotenv
from backend.llm import generate_response
from hindsight_client import Hindsight

load_dotenv()


# ==============================
# HINDSIGHT CLOUD CONFIGURATION
# ==============================

HINDSIGHT_URL = "https://api.hindsight.vectorize.io"
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")

BANK_ID = "incident-response-final"


# ==============================
# INCIDENT ANALYSIS AGENT
# ==============================

async def analyze_incident(incident_description):

    if not HINDSIGHT_API_KEY:
        raise RuntimeError(
            "HINDSIGHT_API_KEY is not configured."
        )

    hindsight = Hindsight(
        base_url=HINDSIGHT_URL,
        api_key=HINDSIGHT_API_KEY
    )

    try:

        # --------------------------------
        # 1. RECALL HISTORICAL INCIDENTS
        # --------------------------------

        recall_result = await hindsight.arecall(
            bank_id=BANK_ID,
            query=incident_description,
            max_tokens=900,
            prefer_observations=False,
            include_source_facts=True,
            max_source_facts_tokens=1000
        )

        historical_incidents = []

        for result in recall_result.results[:3]:

            historical_incidents.append({
                "id": result.id,
                "memory": result.text
            })

        # --------------------------------
        # 2. PREPARE HINDSIGHT EVIDENCE
        # --------------------------------

        evidence_parts = []

        for incident in historical_incidents:

            evidence_parts.append(
                f"Historical Memory: {incident['memory']}"
            )

        if evidence_parts:

            evidence = "\n".join(evidence_parts)

        else:

            evidence = (
                "No relevant historical memories found."
            )

        # --------------------------------
        # 3. BUILD AI PROMPT
        # --------------------------------

        prompt = f"""
You are an incident response assistant.

Analyze this production incident:

INCIDENT:
{incident_description}

HISTORICAL EVIDENCE FROM HINDSIGHT:
{evidence}

IMPORTANT RULES:

1. Use historical memories only when they share
important symptoms, services, or failure conditions
with the current incident.

2. Prioritize memories with multiple matching signals.

3. Treat historical memories as evidence, not proof.

4. Do not use unrelated incidents.

5. Do not invent technical facts.

6. Do not assume that a previous resolution will
definitely solve the current incident.

7. Recommend investigation before risky remediation.

8. If the evidence is insufficient, state that
the root cause is uncertain.

9. Clearly distinguish between historical evidence,
current observations, and inference.

10. Give practical investigation steps that an
engineer can perform.

11. Recommend remediation only after considering
the available evidence.

Return ONLY valid JSON in this exact format:

{{
  "probable_root_cause": "string",
  "reasoning": "string",
  "investigation_steps": [
    "step 1",
    "step 2",
    "step 3"
  ],
  "recommended_remediation": [
    "action 1",
    "action 2"
  ],
  "confidence": "High/Medium/Low"
}}
"""

        # --------------------------------
        # 4. GENERATE AI ANALYSIS
        # --------------------------------

        ai_response = generate_response(prompt)

        # --------------------------------
        # 5. PARSE AI RESPONSE
        # --------------------------------

        try:

            analysis = json.loads(ai_response)

        except json.JSONDecodeError:

            analysis = {
                "probable_root_cause":
                    "Unable to parse AI response",

                "reasoning":
                    ai_response,

                "investigation_steps":
                    [],

                "recommended_remediation":
                    [],

                "confidence":
                    "Unknown"
            }

        # --------------------------------
        # 6. RETURN AGENT RESULT
        # --------------------------------

        return {
            "incident":
                incident_description,

            "historical_incidents":
                historical_incidents,

            "analysis":
                analysis
        }

    finally:

        await hindsight.aclose()