import streamlit as st
import requests


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "https://ai-incident-response-agent-fj85.onrender.com"


st.set_page_config(
    page_title="IncidentMind",
    page_icon="🧠",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("🧠 IncidentMind")

st.markdown(
    """
### AI-Powered Incident Response Agent

IncidentMind analyzes production incidents using **Gemini AI**
and learns from previous incidents using **Hindsight Cloud**.
"""
)


# =========================================================
# ARCHITECTURE
# =========================================================

st.markdown("### How IncidentMind Works")

cols = st.columns(5)

steps = [
    ("🚨", "Incident"),
    ("🧠", "Recall"),
    ("🤖", "Analyze"),
    ("🛠️", "Resolve"),
    ("📚", "Learn")
]

for col, (icon, name) in zip(cols, steps):

    with col:

        st.markdown(
            f"""
            <div style="
                border:1px solid #444;
                border-radius:12px;
                padding:18px;
                text-align:center;
                margin-bottom:20px;
            ">
                <div style="font-size:30px">{icon}</div>
                <b>{name}</b>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# INCIDENT INPUT
# =========================================================

st.markdown("## 🚨 New Incident")

description = st.text_area(
    "Describe the production incident",
    placeholder=(
        "Example: Payment API is returning HTTP 503 errors "
        "during peak traffic. Database connections are "
        "reaching the configured maximum."
    ),
    height=140
)


severity = st.selectbox(
    "Severity",
    [
        "low",
        "medium",
        "high",
        "critical"
    ]
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

if st.button(
    "🔍 Analyze Incident",
    type="primary",
    use_container_width=True
):

    if not description.strip():

        st.warning(
            "Please describe the incident first."
        )

    else:

        with st.spinner(
            "IncidentMind is recalling Hindsight memories and analyzing the incident..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/analyze",
                    json={
                        "description": description
                    },
                    timeout=180
                )


                if response.status_code != 200:

                    st.error(
                        f"Analysis failed: HTTP {response.status_code}"
                    )

                    st.code(
                        response.text
                    )

                else:

                    result = response.json()

                    st.session_state["result"] = result
                    st.session_state["description"] = description
                    st.session_state["severity"] = severity


            except requests.exceptions.RequestException as e:

                st.error(
                    f"Could not connect to IncidentMind API: {e}"
                )


# =========================================================
# DISPLAY RESULT
# =========================================================

if "result" in st.session_state:

    result = st.session_state["result"]

    st.markdown("---")

    # =====================================================
    # HINDSIGHT MEMORY
    # =====================================================

    st.markdown("## 🧠 Hindsight Historical Memory")

    historical = result.get(
        "historical_incidents",
        []
    )


    if historical:

        for index, memory in enumerate(
            historical,
            start=1
        ):

            with st.expander(
                f"Historical Memory {index}"
            ):

                st.write(
                    memory.get(
                        "memory",
                        ""
                    )
                )

    else:

        st.info(
            "No relevant historical memories were found."
        )


    # =====================================================
    # AI ANALYSIS
    # =====================================================

    analysis = result.get(
        "analysis",
        {}
    )

    st.markdown("## 🤖 AI Incident Analysis")


    col1, col2 = st.columns(2)


    with col1:

        st.markdown("### Probable Root Cause")

        st.info(
            analysis.get(
                "probable_root_cause",
                "Unknown"
            )
        )


    with col2:

        st.markdown("### Confidence")

        confidence = analysis.get(
            "confidence",
            "Unknown"
        )

        st.metric(
            "Confidence",
            confidence
        )


    st.markdown("### Reasoning")

    st.write(
        analysis.get(
            "reasoning",
            ""
        )
    )


    # =====================================================
    # INVESTIGATION
    # =====================================================

    st.markdown(
        "### 🔎 Investigation Steps"
    )

    investigation_steps = analysis.get(
        "investigation_steps",
        []
    )


    for step in investigation_steps:

        st.markdown(
            f"- {step}"
        )


    # =====================================================
    # REMEDIATION
    # =====================================================

    st.markdown(
        "### 🛠️ Recommended Remediation"
    )

    remediation = analysis.get(
        "recommended_remediation",
        []
    )


    for action in remediation:

        st.markdown(
            f"- {action}"
        )


    # =====================================================
    # RESOLVE INCIDENT
    # =====================================================

    st.markdown("---")

    st.markdown(
        "## ✅ Resolve & Teach IncidentMind"
    )

    root_cause = st.text_input(
        "Confirmed Root Cause",
        value=analysis.get(
            "probable_root_cause",
            ""
        )
    )


    resolution = st.text_area(
        "Resolution",
        placeholder=(
            "Describe what was done to resolve the incident."
        )
    )


    outcome = st.text_area(
        "Outcome",
        placeholder=(
            "Describe the result after remediation."
        )
    )


    # =====================================================
    # CREATE LOCAL INCIDENT FIRST
    # =====================================================

    if st.button(
        "💾 Resolve & Store in Hindsight",
        type="primary",
        use_container_width=True
    ):

        try:

            # ---------------------------------------------
            # Create incident
            # ---------------------------------------------

            create_response = requests.post(
                f"{API_URL}/incidents",
                json={
                    "title": "IncidentMind analyzed incident",
                    "description": st.session_state["description"],
                    "severity": st.session_state["severity"]
                },
                timeout=60
            )


            if create_response.status_code != 200:

                st.error(
                    f"Could not create incident: "
                    f"{create_response.text}"
                )

            else:

                incident = create_response.json()

                incident_id = incident["id"]


                # -----------------------------------------
                # Resolve + retain
                # -----------------------------------------

                outcome_response = requests.put(
                    f"{API_URL}/incidents/{incident_id}/outcome",
                    params={
                        "root_cause": root_cause,
                        "resolution": resolution,
                        "outcome": outcome
                    },
                    timeout=120
                )


                if outcome_response.status_code != 200:

                    st.error(
                        "Incident was created, but learning failed."
                    )

                    st.code(
                        outcome_response.text
                    )

                else:

                    stored = outcome_response.json()


                    st.success(
                        "Incident resolved successfully!"
                    )


                    st.success(
                        "🧠 IncidentMind learned from this incident "
                        "and stored the post-mortem in Hindsight Cloud."
                    )


                    st.json(
                        stored
                    )


                    st.markdown(
                        """
                        ### 🔁 Agent Learning Loop

                        **Incident → Recall → Analyze → Resolve → Retain → Future Recall**
                        """
                    )


        except requests.exceptions.RequestException as e:

            st.error(
                f"Connection error: {e}"
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "IncidentMind • FastAPI + Gemini + Hindsight Cloud • Persistent AI Incident Memory"
)