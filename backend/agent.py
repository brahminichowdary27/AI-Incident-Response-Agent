import json

from backend.llm import generate_response
from hindsight_client import Hindsight


HINDSIGHT_URL = "http://localhost:8888"

# Final Hindsight memory bank for the hackathon
BANK_ID = "incident-response-final"


async def analyze_incident(incident_description):

    hindsight = Hindsight(
        base_url=HINDSIGHT_URL
    )

    try:

        # ---------------------------------------------------------
        # RECALL RELEVANT HISTORICAL EXPERIENCE FROM HINDSIGHT
        # ---------------------------------------------------------

        recall_result = await hindsight.arecall(
            bank_id=BANK_ID,
            query=incident_description,

            types=[
                "observation",
                "experience",
                "world"
            ],

            max_tokens=900,
            budget="mid",

            prefer_observations=True,

            # Original source facts behind observations
            include_source_facts=True,
            max_source_facts_tokens=1600,

            # Original retained text
            include_chunks=True,
            max_chunk_tokens=1800
        )

        historical_incidents = []

        # Hindsight returns source facts at the response level.
        source_facts = getattr(
            recall_result,
            "source_facts",
            {}
        ) or {}

        # Hindsight returns original source chunks
        # at the response level.
        chunks = getattr(
            recall_result,
            "chunks",
            {}
        ) or {}

        # ---------------------------------------------------------
        # PROCESS TOP HISTORICAL MEMORIES
        # ---------------------------------------------------------

        for result in recall_result.results[:3]:

            memory_text = result.text

            memory_type = getattr(
                result,
                "type",
                None
            )

            if memory_type:
                memory_text = (
                    f"[Memory Type: {memory_type}]\n"
                    f"{memory_text}"
                )

            # -----------------------------------------------------
            # ADD ORIGINAL SOURCE FACTS
            # -----------------------------------------------------

            source_fact_ids = getattr(
                result,
                "source_fact_ids",
                None
            ) or []

            if source_fact_ids:

                memory_text += (
                    "\n\nOriginal Historical Facts:\n"
                )

                for fact_id in source_fact_ids:

                    fact = source_facts.get(
                        fact_id
                    )

                    if fact:

                        fact_text = getattr(
                            fact,
                            "text",
                            None
                        )

                        fact_type = getattr(
                            fact,
                            "type",
                            None
                        )

                        if fact_text:

                            if fact_type:

                                memory_text += (
                                    f"- [{fact_type}] "
                                    f"{fact_text}\n"
                                )

                            else:

                                memory_text += (
                                    f"- {fact_text}\n"
                                )

            # -----------------------------------------------------
            # ADD ORIGINAL RETAINED CHUNK
            # -----------------------------------------------------

            chunk_id = getattr(
                result,
                "chunk_id",
                None
            )

            if chunk_id:

                chunk = chunks.get(
                    chunk_id
                )

                if chunk:

                    chunk_text = getattr(
                        chunk,
                        "text",
                        None
                    )

                    if chunk_text:

                        memory_text += (
                            "\n\nOriginal Retained Post-Mortem:\n"
                            f"{chunk_text}\n"
                        )

            historical_incidents.append({
                "id": result.id,
                "memory": memory_text
            })

        # ---------------------------------------------------------
        # BUILD HISTORICAL EVIDENCE
        # ---------------------------------------------------------

        evidence_parts = []

        for index, incident in enumerate(
            historical_incidents,
            start=1
        ):

            evidence_parts.append(
                f"""
HISTORICAL MEMORY {index}
-------------------------
{incident["memory"]}
"""
            )

        if evidence_parts:

            evidence = "\n".join(
                evidence_parts
            )

        else:

            evidence = (
                "No relevant historical memories found."
            )

        # ---------------------------------------------------------
        # AI INCIDENT ANALYSIS
        # ---------------------------------------------------------

        prompt = f"""
You are an AI incident response assistant.

Your job is to analyze the CURRENT production incident
using current observations and relevant historical
experience retrieved from Hindsight.

========================================================
CURRENT INCIDENT
========================================================

{incident_description}

========================================================
HISTORICAL EVIDENCE FROM HINDSIGHT
========================================================

{evidence}

========================================================
STRICT EVIDENCE RULES
========================================================

1. The CURRENT INCIDENT is the primary source of truth
for current symptoms and conditions.

2. Never invent a current symptom, metric, infrastructure
condition, deployment, root cause, or event.

3. A fact mentioned only in historical evidence MUST NOT
be described as a current fact.

4. Never say the current incident has "confirmed" a root
cause unless the current incident description explicitly
confirms it.

5. Historical incidents are evidence, not proof.

6. Prefer historical incidents that match multiple signals:
   - service
   - error pattern
   - traffic conditions
   - infrastructure condition
   - database behavior
   - failure pattern

7. Do NOT select a historical incident merely because it
contains the same HTTP status code.

8. For example:
   - HTTP 503 alone is not enough to conclude payment
     gateway failure.
   - Database connections near their configured maximum
     are a stronger signal for database connection
     saturation.

9. If a historical incident contains a confirmed root
cause and successful resolution that closely matches the
CURRENT INCIDENT, mention that historical pattern.

10. Do not blindly copy a historical root cause.

11. Recommend investigation before risky remediation.

12. Historical remediation should be presented as a
possible action only after appropriate investigation.

13. Clearly distinguish:
   CURRENT OBSERVATIONS
   HISTORICAL EVIDENCE
   INFERENCE

14. If evidence is insufficient, say that the root cause
is uncertain.

15. Do not claim CPU saturation, memory exhaustion,
deployment changes, configuration changes, database
failures, or any other condition unless it is explicitly
present in the CURRENT INCIDENT or clearly identified as
historical evidence.

16. The reasoning must explain WHY the selected historical
memory is relevant.

17. The recommended remediation should follow logically
from the investigation and evidence.

========================================================
OUTPUT FORMAT
========================================================

Return ONLY valid JSON.

Use exactly this structure:

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

Do not add markdown.
Do not add explanations outside the JSON.
"""

        # ---------------------------------------------------------
        # GENERATE RESPONSE USING LOCAL OLLAMA
        # ---------------------------------------------------------

        ai_response = generate_response(
            prompt
        )

        # ---------------------------------------------------------
        # PARSE JSON
        # ---------------------------------------------------------

        try:

            analysis = json.loads(
                ai_response
            )

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

        # ---------------------------------------------------------
        # RETURN RESULT
        # ---------------------------------------------------------

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