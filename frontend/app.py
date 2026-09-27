import streamlit as st
import requests


# =========================================================
# CONFIG
# =========================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="IncidentMind",
    page_icon="🧠",
    layout="wide"
)


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #9ca3af;
        margin-bottom: 25px;
    }

    .memory-card {
        padding: 18px;
        border: 1px solid #3f3f46;
        border-radius: 12px;
        margin-bottom: 12px;
        background: #111318;
        min-height: 120px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .flow-box {
        text-align: center;
        padding: 15px;
        border: 1px solid #3f3f46;
        border-radius: 12px;
        background: #111318;
    }

    .small-text {
        color: #9ca3af;
        font-size: 14px;
    }

    .learning-box {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #3f3f46;
        background: #111318;
        margin-top: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "incident_id": None,
    "analysis": None,
    "memories": [],
    "incident_description": "",
    "incident_title": "",
    "severity": "high",
    "resolved": False,
    "resolution_message": ""
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🧠 IncidentMind</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    AI-powered incident response that remembers what happened before,
    reasons from historical experience, and learns from every resolved incident.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SYSTEM FLOW
# =========================================================

flow1, flow2, flow3, flow4, flow5 = st.columns(5)

with flow1:
    st.markdown(
        """
        <div class="flow-box">
        🚨<br>
        <b>Incident</b><br>
        <span class="small-text">New event</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with flow2:
    st.markdown(
        """
        <div class="flow-box">
        🧠<br>
        <b>Recall</b><br>
        <span class="small-text">Hindsight</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with flow3:
    st.markdown(
        """
        <div class="flow-box">
        🤖<br>
        <b>Analyze</b><br>
        <span class="small-text">Local AI</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with flow4:
    st.markdown(
        """
        <div class="flow-box">
        🛠️<br>
        <b>Resolve</b><br>
        <span class="small-text">Engineer</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with flow5:
    st.markdown(
        """
        <div class="flow-box">
        🔄<br>
        <b>Learn</b><br>
        <span class="small-text">Retain</span>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# =========================================================
# NEW INCIDENT
# =========================================================

st.markdown(
    '<div class="section-title">🚨 New Incident</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns([2, 1])

with col1:

    title = st.text_input(
        "Incident Title",
        value=st.session_state.incident_title,
        placeholder="Example: Payment API outage"
    )

with col2:

    severity_options = [
        "low",
        "medium",
        "high",
        "critical"
    ]

    severity = st.selectbox(
        "Severity",
        severity_options,
        index=severity_options.index(
            st.session_state.severity
        )
    )


description = st.text_area(
    "Incident Description",
    value=st.session_state.incident_description,
    height=150,
    placeholder=(
        "Describe the symptoms, errors, affected service, "
        "resource usage, recent deployments, etc."
    )
)


analyze_button = st.button(
    "🤖 Analyze Incident",
    type="primary",
    use_container_width=False
)


# =========================================================
# ANALYZE INCIDENT
# =========================================================

if analyze_button:

    if not title.strip() or not description.strip():

        st.warning(
            "Please enter both an incident title and description."
        )

    else:

        st.session_state.incident_title = title
        st.session_state.incident_description = description
        st.session_state.severity = severity

        try:

            with st.spinner(
                "🧠 Creating incident and recalling Hindsight memory..."
            ):

                # -----------------------------------------
                # CREATE INCIDENT
                # -----------------------------------------

                create_response = requests.post(
                    f"{API_URL}/incidents",
                    json={
                        "title": title,
                        "description": description,
                        "severity": severity
                    },
                    timeout=30
                )

                create_response.raise_for_status()

                incident = create_response.json()

                incident_id = incident["id"]


                # -----------------------------------------
                # AI ANALYSIS
                # -----------------------------------------

                analyze_response = requests.post(
                    f"{API_URL}/analyze",
                    json={
                        "description": description
                    },
                    timeout=180
                )

                analyze_response.raise_for_status()

                result = analyze_response.json()


                # -----------------------------------------
                # STORE RESULT
                # -----------------------------------------

                st.session_state.incident_id = incident_id

                st.session_state.analysis = (
                    result["analysis"]
                )

                st.session_state.memories = (
                    result["historical_incidents"]
                )

                st.session_state.resolved = False

                st.session_state.resolution_message = ""


            st.success(
                f"✅ Incident #{incident_id} analyzed successfully."
            )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Backend error: {e}"
            )


# =========================================================
# HINDSIGHT HISTORICAL MEMORY
# =========================================================

if st.session_state.memories:

    st.divider()

    st.markdown(
        '<div class="section-title">🧠 Hindsight Historical Memory</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Relevant operational knowledge recalled from previous incidents."
    )

    memory_col1, memory_col2 = st.columns(2)

    for index, memory in enumerate(
        st.session_state.memories,
        start=1
    ):

        if index % 2 == 1:
            target_col = memory_col1
        else:
            target_col = memory_col2

        with target_col:

            st.markdown(
                f"""
                <div class="memory-card">
                    <b>Memory {index}</b>
                    <br><br>
                    {memory["memory"]}
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# AI INCIDENT ANALYSIS
# =========================================================

if st.session_state.analysis:

    analysis = st.session_state.analysis

    st.divider()

    st.markdown(
        '<div class="section-title">🤖 AI Incident Analysis</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------
    # ROOT CAUSE + CONFIDENCE
    # -----------------------------------------

    root_col, confidence_col = st.columns(
        [3, 1]
    )

    with root_col:

        st.markdown(
            "### Probable Root Cause"
        )

        st.info(
            analysis.get(
                "probable_root_cause",
                "Unknown"
            )
        )


    with confidence_col:

        st.markdown(
            "### Confidence"
        )

        confidence = analysis.get(
            "confidence",
            "Unknown"
        )

        st.metric(
            "AI Confidence",
            confidence
        )


    # -----------------------------------------
    # REASONING
    # -----------------------------------------

    st.markdown(
        "### 🧩 Reasoning"
    )

    st.write(
        analysis.get(
            "reasoning",
            "No reasoning available."
        )
    )


    # -----------------------------------------
    # INVESTIGATION + REMEDIATION
    # -----------------------------------------

    investigation_col, remediation_col = st.columns(2)


    with investigation_col:

        st.markdown(
            "### 🔎 Investigation Steps"
        )

        steps = analysis.get(
            "investigation_steps",
            []
        )

        if steps:

            for step in steps:

                st.markdown(
                    f"- {step}"
                )

        else:

            st.write(
                "No investigation steps provided."
            )


    with remediation_col:

        st.markdown(
            "### 🛠️ Recommended Remediation"
        )

        actions = analysis.get(
            "recommended_remediation",
            []
        )

        if actions:

            for action in actions:

                st.markdown(
                    f"- {action}"
                )

        else:

            st.write(
                "No remediation recommendations provided."
            )


# =========================================================
# RESOLVE INCIDENT
# =========================================================

if st.session_state.incident_id:

    st.divider()

    st.markdown(
        '<div class="section-title">✅ Resolve Incident</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Confirm the actual root cause, resolution, and outcome. "
        "The completed post-mortem will become persistent Hindsight memory."
    )


    root_cause = st.text_input(
        "Confirmed Root Cause"
    )


    resolution = st.text_area(
        "Resolution",
        height=100
    )


    outcome = st.text_area(
        "Outcome",
        height=100
    )


    resolve_button = st.button(
        "🧠 Resolve & Store in Hindsight",
        type="secondary"
    )


    if resolve_button:

        if (
            not root_cause.strip()
            or not resolution.strip()
            or not outcome.strip()
        ):

            st.warning(
                "Please fill in root cause, resolution, and outcome."
            )

        else:

            try:

                with st.spinner(
                    "🧠 Storing post-mortem in Hindsight..."
                ):

                    response = requests.put(
                        f"{API_URL}/incidents/"
                        f"{st.session_state.incident_id}/outcome",

                        params={
                            "root_cause": root_cause,
                            "resolution": resolution,
                            "outcome": outcome
                        },

                        timeout=180
                    )

                    response.raise_for_status()

                    result = response.json()


                if result.get(
                    "hindsight_memory_stored"
                ):

                    st.session_state.resolved = True

                    st.session_state.resolution_message = (
                        "Incident resolved and post-mortem stored in Hindsight."
                    )

                    st.success(
                        "🧠 Incident resolved and post-mortem stored in Hindsight."
                    )

                else:

                    st.warning(
                        "Incident resolved, but Hindsight memory "
                        "was not confirmed."
                    )


            except requests.exceptions.RequestException as e:

                st.error(
                    f"Failed to resolve incident: {e}"
                )


# =========================================================
# LEARNING STATUS
# =========================================================

if st.session_state.resolved:

    st.divider()

    st.markdown(
        """
        <div class="learning-box">

        ### 🔄 Agent Learned From This Incident

        The confirmed root cause, resolution, and outcome have
        been retained in <b>Hindsight</b>.

        Future incidents can recall this operational experience
        and use it as historical evidence during analysis.

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# START NEW INCIDENT
# ONLY SHOW AFTER AN INCIDENT EXISTS
# =========================================================

if st.session_state.incident_id:

    st.divider()

    if st.button(
        "🔄 Start New Incident"
    ):

        st.session_state.incident_id = None
        st.session_state.analysis = None
        st.session_state.memories = []
        st.session_state.incident_description = ""
        st.session_state.incident_title = ""
        st.session_state.severity = "high"
        st.session_state.resolved = False
        st.session_state.resolution_message = ""

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "IncidentMind • FastAPI + Ollama + Hindsight • Persistent AI Incident Memory"
)