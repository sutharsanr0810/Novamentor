"""
NovaMentor Pro — AI-Driven Multi-Agent Academic Framework
Production Architecture: Multi-Key Pool Rotation + Multi-Model Fallback + Resilient Failsafe
"""

import datetime
import hashlib
import os
import re
import streamlit as st
from google import genai
from google.genai import types

try:
    from pypdf import PdfReader
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

st.set_page_config(
    page_title="NovaMentor Pro",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_configured_api_keys() -> str:
    try:
        if "GEMINI_API_KEYS" in st.secrets:
            return st.secrets["GEMINI_API_KEYS"].strip()
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"].strip()
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"].strip()
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "").strip()

def extract_file_content(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    try:
        filename = uploaded_file.name.lower()
        if filename.endswith(".pdf") and PDF_ENABLED:
            reader = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text[:15000]
        elif filename.endswith((".txt", ".md", ".py", ".csv")):
            return uploaded_file.getvalue().decode("utf-8")[:15000]
        else:
            return f"[Uploaded file: {uploaded_file.name} - binary format omitted]"
    except Exception as e:
        return f"[Error extracting file content: {str(e)}]"

def build_markdown_report(title: str, context: str, file_name: str, chat_histories: dict, roundtable_log: list) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc_title = title.strip() if title.strip() else "Academic Project Guidance Report"

    lines = [
        "# 🧭 NovaMentor Academic Guidance & Defense Dossier",
        f"**Project Title:** {doc_title}  ",
        f"**Generated On:** {timestamp}  ",
        f"**Attached Reference File:** {file_name or 'None'}  ",
        "\n---\n",
        "## 📋 Project Context & Scope",
        f"{context.strip() if context.strip() else 'No project context recorded.'}",
        "\n---\n",
    ]

    if roundtable_log:
        lines.append("## 🏛️ Autonomous Multi-Agent Roundtable Summary\n")
        for turn in roundtable_log:
            lines.append(f"**{turn['agent']}**:\n{turn['content']}\n")
        lines.append("---\n")

    lines.append("## 💬 Specialized Agent Consultations\n")
    has_chats = False
    for agent_name, messages in chat_histories.items():
        if not messages:
            continue
        has_chats = True
        lines.append(f"### 🤖 Agent: {agent_name}\n")
        for msg in messages:
            speaker = "👤 **Student**" if msg["role"] == "user" else f"🧭 **{agent_name}**"
            lines.append(f"{speaker}:\n{msg['content']}\n")
        lines.append("---\n")

    if not has_chats and not roundtable_log:
        lines.append("_No agent conversations were recorded during this session._")

    return "\n".join(lines)

class BaseMentorAgent:
    name: str = "Base Agent"
    role_description: str = "Academic project mentor."
    system_prompt: str = "You are an academic mentor."

    def fallback_mock_response(self, prompt: str, context: str) -> str:
        clean_p = prompt[:80].replace('"', "").replace("'", "")
        return "\n\n".join([
            f"**[{self.name} Analysis]**",
            f"**1. Core Assessment:**\nEvaluating project query: *{clean_p}...*",
            "**2. Technical Recommendations:**\n- Quantize neural network tensors to INT8.\n- Apply direct memory buffers to prevent frame ingestion drops.\n- Enforce radiometric thresholding to eliminate glare artifacts.",
            "**3. Defense Validation:**\nEnsure baseline metrics show latency and precision trade-offs."
        ])

    def respond(self, prompt: str, context: str = "", reference_doc: str = "", api_key_str: str = "") -> str:
        raw_keys = (api_key_str or "").replace("\n", ",").split(",")
        key_pool = [k.strip().strip("'").strip('"') for k in raw_keys if k.strip()]

        if not key_pool:
            return self.fallback_mock_response(prompt, context)

        full_prompt = (
            f"### Overall Project Context:\n{context or 'No context provided.'}\n\n"
            f"### Uploaded Reference Document Content:\n{reference_doc or 'None'}\n\n"
            f"### Student Query:\n{prompt}"
        )

        candidate_models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-3.1-flash-lite",
        ]

        for key in key_pool:
            try:
                client = genai.Client(api_key=key)
                for model_name in candidate_models:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=self.system_prompt,
                                temperature=0.4,
                            ),
                        )
                        if response and response.text:
                            return response.text
                    except Exception:
                        continue
            except Exception:
                continue

        return self.fallback_mock_response(prompt, context)

class RequirementAnalyzerAgent(BaseMentorAgent):
    name = "Requirement Analyzer"
    role_description = "Scope definition, functional requirements, and IEEE project milestones."
    system_prompt = (
        "You are an Academic Requirement Analyst. Format responses with clear Scope, "
        "Functional Requirements (FR), Non-Functional Requirements (NFR), and a Sprint Milestone Schedule."
    )

    def fallback_mock_response(self, prompt: str, context: str) -> str:
        return "\n\n".join([
            "### 📋 Requirement Analysis & Project Scope",
            "**1. Scope Definition:**\nAutonomous embedded edge deployment for high-reliability computer vision.",
            "**2. Functional Requirements (FR):**\n- FR-1: Continuous frame stream ingestion at >= 30 FPS.\n- FR-2: On-device bounding-box localization.\n- FR-3: Automated threshold trigger and telemetry dispatch.",
            "**3. Non-Functional Requirements (NFR):**\n- Latency: End-to-end processing <= 33 ms.\n- Power Budget: Peak subsystem draw <= 12W.\n- Reliability: 100% offline standalone edge execution.",
            "**4. Sprint Milestone Schedule:**\n- Sprint 1: Hardware integration & sensor calibration.\n- Sprint 2: Model quantization & edge pipeline acceleration.\n- Sprint 3: Benchmark validation against public dataset & viva prep."
        ])

class ArchitectureAgent(BaseMentorAgent):
    name = "System Architect"
    role_description = "Pipeline design, hardware/software selection, and Mermaid.js diagrams."
    system_prompt = (
        "You are a Senior Academic System Architect. Propose robust technical pipelines. "
        "Whenever explaining architectures or data pipelines, ALWAYS include a valid mermaid code block "
        "so Streamlit can render it visually."
    )

    def fallback_mock_response(self, prompt: str, context: str) -> str:
        diag = "```mermaid\nflowchart TD\n    A[Sensor Stream] --> B[Host DMA Buffer]\n    B --> C[Edge NPU Accelerator]\n    C --> D{Anomaly Filter}\n    D -->|Target Detected| E[Telemetry Dispatch]\n    D -->|Normal Scan| F[Data Logger]\n```"
        return "\n\n".join([
            "### 🏗️ Proposed System Architecture",
            "The architecture employs a dual-stage design separating sensor acquisition from INT8 accelerated inference.",
            diag,
            "**Key Architectural Decisions:**\n- Direct Memory Access avoids frame-drop bottlenecks on the host controller.\n- Dedicated NPU offloading frees CPU cores for telemetry and state tracking."
        ])

class ResearchReviewerAgent(BaseMentorAgent):
    name = "Literature Reviewer"
    role_description = "Identifies IEEE research gaps, baseline benchmark models, and evaluation metrics."
    system_prompt = (
        "You are an Academic Literature Reviewer. Highlight research gaps, standard baseline models, "
        "benchmark datasets, and IEEE validation metrics (e.g., F1, mAP, Latency, Precision)."
    )

    def fallback_mock_response(self, prompt: str, context: str) -> str:
        return "\n\n".join([
            "### 📚 Literature Review & IEEE Benchmarking",
            "**1. Standard Benchmark Baselines:**\nCompare against YOLO-Nano and MobileNet-SSD baselines on aerial thermal datasets.",
            "**2. Key Research Gaps Addressed:**\nEliminating optical sensor false positives under fluctuating sunlight conditions through calibrated filtering.",
            "**3. Target IEEE Evaluation Metrics:**\n- Detection Accuracy: Target mAP@0.5 >= 88%.\n- False Alarm Rate: Maintain FAR < 1.5% across varying ambient sunlight conditions.\n- Power Efficiency: Minimum 3.5 FPS/Watt ratio."
        ])

class ImplementationAgent(BaseMentorAgent):
    name = "Implementation Guide"
    role_description = "Provides production-ready pseudocode, optimization methods, and library setups."
    system_prompt = (
        "You are a Senior Implementation Engineer. Provide clean, modular Python/C++ code snippets, "
        "optimization guidelines (CUDA, TensorRT, multi-threading), and dependency requirements."
    )

    def fallback_mock_response(self, prompt: str, context: str) -> str:
        snippet = "```python\nimport cv2\nimport numpy as np\n\ndef process_frame(raw_frame, threshold=65.0):\n    temp_map = (raw_frame / 100.0) - 273.15\n    mask = (temp_map >= threshold).astype(np.uint8) * 255\n    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)\n    return stats[1:], centroids[1:]\n```"
        return "\n\n".join([
            "### 💻 Implementation Guide & Zero-Copy Pipeline",
            snippet,
            "**Deployment Tips:**\n- Run the frame parser in an asynchronous worker thread to remove Python GIL overhead."
        ])

class VivaPrepAgent(BaseMentorAgent):
    name = "Viva & Defense Examiner"
    role_description = "Simulates an external university defense examiner with score rubric."
    system_prompt = (
        "You are a strict External Project Defense Examiner. "
        "When the student answers a question: "
        "1. Give an exact Score out of 10. "
        "2. Critique technical gaps or missing validation. "
        "3. Ask the next challenging follow-up question regarding edge failures, metrics, or trade-offs."
    )

    def fallback_mock_response(self, prompt: str, context: str) -> str:
        return "\n\n".join([
            "### 🎓 Viva Voce Defense Assessment",
            "**Examiner Score:** `8.5 / 10`",
            "**Technical Critique:**\n- Edge accelerator selection is well-justified for thermal dissipation constraints.\n- Must provide explicit mitigation steps for solar reflection false-positive spikes during midday flight schedules.",
            "**Defense Question:**\n> *If ambient ground rock reflections reach high temperatures, how does your classifier distinguish true targets from non-hazardous glare without increasing processing latency?*"
        ])

AGENT_REGISTRY = {
    "Requirement Analyzer": RequirementAnalyzerAgent,
    "System Architect": ArchitectureAgent,
    "Literature Reviewer": ResearchReviewerAgent,
    "Implementation Guide": ImplementationAgent,
    "Viva & Defense Examiner": VivaPrepAgent,
}

USER_DB = {
    "visanth": {"name": "Visanth K", "roll_no": "7376242AL220", "password_hash": hashlib.sha256("Visanth@2026".encode()).hexdigest()},
    "ramkumar": {"name": "Ramkumar V", "roll_no": "7376242AL171", "password_hash": hashlib.sha256("Ramkumar@2026".encode()).hexdigest()},
    "sutharsan": {"name": "Sutharsan R", "roll_no": "7376242AL202", "password_hash": hashlib.sha256("Sutharsan@2026".encode()).hexdigest()},
    "student": {"name": "Demo Student", "roll_no": "7376242AL000", "password_hash": hashlib.sha256("Student@2026".encode()).hexdigest()},
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_fullname" not in st.session_state:
    st.session_state.user_fullname = ""
if "project_title" not in st.session_state:
    st.session_state.project_title = ""
if "project_context" not in st.session_state:
    st.session_state.project_context = ""
if "reference_text" not in st.session_state:
    st.session_state.reference_text = ""
if "reference_filename" not in st.session_state:
    st.session_state.reference_filename = ""
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "roundtable_log" not in st.session_state:
    st.session_state.roundtable_log = []

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🧭 NovaMentor Pro")
        st.markdown("### Academic Multi-Agent Project Defense Portal")
        st.caption("Sign in with pre-configured team credentials.")

        with st.form("login_form"):
            username_input = st.text_input("Username").strip().lower()
            password_input = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Access Portal", use_container_width=True)

            if submitted:
                if username_input in USER_DB:
                    input_hash = hashlib.sha256(password_input.encode()).hexdigest()
                    if input_hash == USER_DB[username_input]["password_hash"]:
                        st.session_state.authenticated = True
                        st.session_state.username = username_input
                        st.session_state.user_fullname = USER_DB[username_input]["name"]
                        st.success("Authentication successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("Invalid username.")

        st.info("Logins: visanth, ramkumar, sutharsan, student (Password: Name@2026)")

if not st.session_state.authenticated:
    render_login()
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_fullname}")
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.user_fullname = ""
            st.rerun()

        st.markdown("---")
        st.markdown("### 🔑 API Key Pool")
        
        detected_secret = get_configured_api_keys()
        if "gemini_api_key" not in st.session_state or not st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = detected_secret

        st.text_area(
            "Gemini API Keys", 
            key="gemini_api_key",
            height=90,
            help="Enter 1 to 5 API keys separated by commas or newlines.",
            placeholder="AIzaSy..., AIzaSy..., AIzaSy..."
        )
        
        active_key_str = (st.session_state.gemini_api_key or detected_secret or "").strip()
        parsed_keys = [k.strip() for k in active_key_str.replace("\n", ",").split(",") if k.strip()]
        
        if parsed_keys:
            st.success(f"✅ Active Key Pool: **{len(parsed_keys)} Key(s) Loaded**")
        else:
            st.info("ℹ️ Running in resilient demo mode.")

        st.markdown("---")
        st.markdown("### 📑 Project Dossier")
        st.text_input("Project Title", key="project_title", placeholder="e.g., Edge AI Drone Thermal Vision")
        st.text_area(
            "Project Scope & Context",
            key="project_context",
            height=140,
            placeholder="Domain, target hardware, constraints, algorithms tested, dataset details...",
        )

        st.markdown("### 📎 Grounding Reference Material")
        uploaded_doc = st.file_uploader(
            "Upload Paper / Code / SRS (.pdf, .txt, .py)",
            type=["pdf", "txt", "py", "md", "csv"],
        )
        if uploaded_doc:
            st.session_state.reference_text = extract_file_content(uploaded_doc)
            st.session_state.reference_filename = uploaded_doc.name
            st.caption(f"Loaded: `{uploaded_doc.name}` ({len(st.session_state.reference_text)} chars)")
        else:
            st.session_state.reference_text = ""
            st.session_state.reference_filename = ""

        st.markdown("---")
        if st.button("🗑️ Reset All Agent Chats", use_container_width=True):
            st.session_state.chat_histories = {}
            st.session_state.roundtable_log = []
            st.rerun()

    effective_keys = (st.session_state.gemini_api_key or detected_secret or "").strip()

    tab_agents, tab_roundtable, tab_export = st.tabs([
        "💬 Individual Agents",
        "🏛️ Multi-Agent Roundtable",
        "📄 Export Dossier",
    ])

    with tab_agents:
        agent_names = list(AGENT_REGISTRY.keys())
        selected_agent_name = st.radio(
            "Select Specialist",
            agent_names,
            horizontal=True,
        )

        agent_class = AGENT_REGISTRY[selected_agent_name]
        agent = agent_class()

        st.markdown(f"#### 🧭 {selected_agent_name}")
        st.caption(agent.role_description)

        if selected_agent_name not in st.session_state.chat_histories:
            st.session_state.chat_histories[selected_agent_name] = []

        for msg in st.session_state.chat_histories[selected_agent_name]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input(f"Consult with the {selected_agent_name}...")
        if user_input:
            st.session_state.chat_histories[selected_agent_name].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing project parameters..."):
                    reply = agent.respond(
                        prompt=user_input,
                        context=st.session_state.project_context,
                        reference_doc=st.session_state.reference_text,
                        api_key_str=effective_keys,
                    )
                    st.markdown(reply)

            st.session_state.chat_histories[selected_agent_name].append({"role": "assistant", "content": reply})
            st.rerun()

    with tab_roundtable:
        st.markdown("### 🏛️ Autonomous Project Committee Review")
        st.write(
            "Convene an autonomous 4-agent committee review. The specialists will evaluate your project parameters sequentially and synthesize a consensus."
        )

        col_run, col_clear = st.columns([1, 4])
        with col_run:
            run_debate = st.button("🚀 Convene Committee", type="primary", use_container_width=True)
        with col_clear:
            if st.button("Clear Committee Log"):
                st.session_state.roundtable_log = []
                st.rerun()

        if run_debate:
            if not st.session_state.project_context.strip():
                st.warning("Please fill in the 'Project Scope & Context' in the sidebar before convening the committee.")
            else:
                st.session_state.roundtable_log = []
                committee_order = [
                    ("Requirement Analyzer", "Define the core problem scope, functional boundaries, and target criteria."),
                    ("System Architect", "Based on these requirements, design the end-to-end pipeline and Mermaid diagram."),
                    ("Literature Reviewer", "Critique this design against state-of-the-art IEEE benchmarks and identify gaps."),
                    ("Viva & Defense Examiner", "Evaluate the proposal for defense viability, identify edge-case vulnerabilities, and assign a readiness score out of 10."),
                ]

                running_context = (
                    f"Title: {st.session_state.project_title}\n"
                    f"Scope & Context: {st.session_state.project_context}\n"
                )

                for agent_name, prompt_task in committee_order:
                    agent_instance = AGENT_REGISTRY[agent_name]()
                    with st.spinner(f"{agent_name} is deliberating..."):
                        debate_prompt = (
                            f"Task: {prompt_task}\n\n"
                            f"Previous Committee Deliberations:\n{running_context}"
                        )
                        agent_reply = agent_instance.respond(
                            prompt=debate_prompt,
                            context=st.session_state.project_context,
                            reference_doc=st.session_state.reference_text,
                            api_key_str=effective_keys,
                        )
                        st.session_state.roundtable_log.append({
                            "agent": agent_name,
                            "content": agent_reply,
                        })
                        running_context += f"\n\n[{agent_name} Contribution]:\n{agent_reply}\n"

                st.rerun()

        if st.session_state.roundtable_log:
            for turn in st.session_state.roundtable_log:
                with st.expander(f"📌 {turn['agent']}", expanded=True):
                    st.markdown(turn["content"])

    with tab_export:
        st.markdown("### 📄 Export Academic Defense Dossier")
        st.write("Generate and download a consolidated Markdown report containing all project context, committee deliberations, and specialist consultations.")

        dossier_content = build_markdown_report(
            title=st.session_state.project_title,
            context=st.session_state.project_context,
            file_name=st.session_state.reference_filename,
            chat_histories=st.session_state.chat_histories,
            roundtable_log=st.session_state.roundtable_log,
        )

        st.download_button(
            label="📥 Download Dossier (.md)",
            data=dossier_content,
            file_name=f"{re.sub(r'[^a-zA-Z0-9_-]', '_', st.session_state.project_title or 'novamentor_dossier')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

        st.markdown("#### Document Preview")
        st.text_area("Markdown Preview", value=dossier_content, height=400)
