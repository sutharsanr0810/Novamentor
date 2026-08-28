"""
NovaMentor Pro — AI-Driven Multi-Agent Academic Framework
Features: Multi-Agent Debate, PDF Grounding, Architecture Diagrams, Viva Examiner Scoring
"""

import datetime
import hashlib
import os
import re
import streamlit as st
from google import genai
from google.genai import types

# Optional PDF parsing
try:
    from pypdf import PdfReader
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

# --- PAGE SETUP ---
st.set_page_config(
    page_title="NovaMentor Pro",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- UTILITIES: FILE PARSER ---
def extract_file_content(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    try:
        filename = uploaded_file.name.lower()
        if filename.endswith(".pdf") and PDF_ENABLED:
            reader = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text[:15000]  # Safe token budget
        elif filename.endswith((".txt", ".md", ".py", ".csv")):
            return uploaded_file.getvalue().decode("utf-8")[:15000]
        else:
            return f"[Uploaded file: {uploaded_file.name} — binary format omitted]"
    except Exception as e:
        return f"[Error extracting file content: {str(e)}]"


# --- UTILITIES: EXPORT BUILDER ---
def build_markdown_report(title: str, context: str, file_name: str, chat_histories: dict, roundtable_log: list) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc_title = title.strip() if title.strip() else "Academic Project Guidance Report"

    lines = [
        f"# 🧭 NovaMentor Academic Guidance & Defense Dossier",
        f"**Project Title:** {doc_title}  ",
        f"**Generated On:** {timestamp}  ",
        f"**Attached Reference File:** {file_name or 'None'}  ",
        f"\n---\n",
        f"## 📋 Project Context & Scope",
        f"{context.strip() if context.strip() else 'No project context recorded.'}",
        f"\n---\n",
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


# --- SPECIALIZED AGENT CLASSES ---
class BaseMentorAgent:
    name: str = "Base Agent"
    role_description: str = "Academic project mentor."
    system_prompt: str = "You are an academic mentor."

    def respond(self, prompt: str, context: str = "", reference_doc: str = "", api_key: str = "") -> str:
        clean_key = (api_key or "").strip().strip("'").strip('"')
        if not clean_key:
            return (
                f"**[{self.name} — Offline Mode]**\n"
                f"Please provide an active Google Gemini API key in the sidebar to generate live technical guidance."
            )

        try:
            client = genai.Client(api_key=clean_key)
            full_prompt = (
                f"### Overall Project Context:\n{context or 'No context provided.'}\n\n"
                f"### Uploaded Reference Document Content:\n{reference_doc or 'None'}\n\n"
                f"### Student Query:\n{prompt}"
            )

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.4,
                ),
            )
            return response.text
        except Exception as err:
            return f"**API Error:** `{str(err)}`"


class RequirementAnalyzerAgent(BaseMentorAgent):
    name = "Requirement Analyzer"
    role_description = "Scope definition, functional requirements, and IEEE project milestones."
    system_prompt = (
        "You are an Academic Requirement Analyst. Format responses with clear Scope, "
        "Functional Requirements (FR), Non-Functional Requirements (NFR), and a Sprint Milestone Schedule."
    )


class ArchitectureAgent(BaseMentorAgent):
    name = "System Architect"
    role_description = "Pipeline design, hardware/software selection, and Mermaid.js diagrams."
    system_prompt = (
        "You are a Senior Academic System Architect. Propose robust technical pipelines. "
        "Whenever explaining architectures or data pipelines, ALWAYS include a valid `mermaid` code block "
        "so Streamlit can render it visually."
    )


class ResearchReviewerAgent(BaseMentorAgent):
    name = "Literature Reviewer"
    role_description = "Identifies IEEE research gaps, baseline benchmark models, and evaluation metrics."
    system_prompt = (
        "You are an Academic Literature Reviewer. Highlight research gaps, standard baseline models, "
        "benchmark datasets, and IEEE validation metrics (e.g., F1, mAP, Latency, Precision)."
    )


class ImplementationAgent(BaseMentorAgent):
    name = "Implementation Guide"
    role_description = "Provides production-ready pseudocode, optimization methods, and library setups."
    system_prompt = (
        "You are a Senior Implementation Engineer. Provide clean, modular Python/C++ code snippets, "
        "optimization guidelines (CUDA, TensorRT, multi-threading), and dependency requirements."
    )


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


AGENT_REGISTRY = {
    "Requirement Analyzer": RequirementAnalyzerAgent,
    "System Architect": ArchitectureAgent,
    "Literature Reviewer": ResearchReviewerAgent,
    "Implementation Guide": ImplementationAgent,
    "Viva & Defense Examiner": VivaPrepAgent,
}


# --- AUTHENTICATION ---
USER_DB = {
    "visanth": {"name": "Visanth K", "roll_no": "7376242AL220", "password_hash": hashlib.sha256("Visanth@2026".encode()).hexdigest()},
    "ramkumar": {"name": "Ramkumar V", "roll_no": "7376242AL171", "password_hash": hashlib.sha256("Ramkumar@2026".encode()).hexdigest()},
    "sutharsan": {"name": "Sutharsan R", "roll_no": "7376242AL202", "password_hash": hashlib.sha256("Sutharsan@2026".encode()).hexdigest()},
    "student": {"name": "Demo Student", "roll_no": "7376242AL000", "password_hash": hashlib.sha256("Student@2026".encode()).hexdigest()},
}

# --- INITIALIZE STATE ---
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
if "gemini_api_key" not in st.session_state:
    secret_key = ""
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "") or st.secrets.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = os.environ.get("GEMINI_API_KEY", "")
    st.session_state.gemini_api_key = secret_key
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "roundtable_log" not in st.session_state:
    st.session_state.roundtable_log = []


# --- LOGIN VIEW ---
def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🧭 NovaMentor Pro")
        st.markdown("### Multi-Agent Academic Guidance Workspace")
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

        st.info("Pre-configured Logins: `visanth`, `ramkumar`, `sutharsan`, `student` (Password: `Name@2026`)")


# --- MAIN APP WORKSPACE ---
if not st.session_state.authenticated:
    render_login()
else:
    # Sidebar Setup
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_fullname}")
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.user_fullname = ""
            st.rerun()

        st.markdown("---")
        st.markdown("### 🔑 API Configuration")
        st.text_input("Gemini API Key", type="password", key="gemini_api_key", help="Paste your key from Google AI Studio")
        active_key = (st.session_state.gemini_api_key or "").strip()
        if active_key:
            st.success(f"Key Active: `{active_key[:5]}...{active_key[-3:]}`")
        else:
            st.warning("⚠️ No API Key configured.")

        st.markdown("---")
        st.markdown("### 📑 Project Dossier")
        st.text_input("Project Title", key="project_title", placeholder="e.g., Edge AI Attendance System")
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

    # Main Navigation Tabs
    tab_agents, tab_roundtable, tab_export = st.tabs([
        "💬 Individual Agents",
        "🏛️ Multi-Agent Roundtable",
        "📄 Export Dossier",
    ])

    # --- TAB 1: INDIVIDUAL SPECIALIZED AGENTS ---
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

        # Display history
        for msg in st.session_state.chat_histories[selected_agent_name]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input
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
                        api_key=st.session_state.gemini_api_key,
                    )
                    st.markdown(reply)

            st.session_state.chat_histories[selected_agent_name].append({"role": "assistant", "content": reply})
            st.rerun()

    # --- TAB 2: MULTI-AGENT ROUNDTABLE DEBATE ---
    with tab_roundtable:
        st.markdown("### 🏛️ Autonomous Project Committee Review")
        st.write(
            "Trigger a 4-way committee discussion. The **Requirement Analyst**, **System Architect**, "
            "**Literature Reviewer**, and **Examiner** will debate your project specifications and synthesize a consensus."
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
                    ("System Architect", "Based on these requirements, design the end-to-end pipeline and dataflow."),
                    ("Literature Reviewer", "Critique this design against state-of-the-art IEEE benchmarks and identify gaps."),
                    ("Viva & Defense Examiner", "Evaluate the proposal for weaknesses, computational bottlenecks, and assign a feasibility rating."),
                ]

                conversation_so_far = f"Project Context:\n{st.session_state.project_context}\n\n"

                with st.status("Committee in Session...", expanded=True) as status:
                    for agent_name, instruction in committee_order:
                        agent_obj = AGENT_REGISTRY[agent_name]()
                        status.write(f"🧭 **{agent_name}** is reviewing...")
                        
                        prompt = f"{instruction}\n\nTranscript of Committee Debate So Far:\n{conversation_so_far}"
                        reply = agent_obj.respond(
                            prompt=prompt,
                            context=st.session_state.project_context,
                            reference_doc=st.session_state.reference_text,
                            api_key=st.session_state.gemini_api_key,
                        )
                        st.session_state.roundtable_log.append({"agent": agent_name, "content": reply})
                        conversation_so_far += f"\n[{agent_name}]: {reply}\n"

                    status.update(label="Committee Review Complete!", state="complete", expanded=False)
                st.rerun()

        # Display Roundtable History
        if st.session_state.roundtable_log:
            for entry in st.session_state.roundtable_log:
                with st.expander(f"🤖 {entry['agent']}", expanded=True):
                    st.markdown(entry["content"])

    # --- TAB 3: EXPORT DOSSIER ---
    with tab_export:
        st.markdown("### 📄 Export Comprehensive Academic Report")
        report_md = build_markdown_report(
            st.session_state.project_title,
            st.session_state.project_context,
            st.session_state.reference_filename,
            st.session_state.chat_histories,
            st.session_state.roundtable_log,
        )
        st.text_area("Markdown Dossier Preview", report_md, height=350)

        filename = f"{(st.session_state.project_title or 'NovaMentor_Project').replace(' ', '_')}_Report.md"
        st.download_button(
            label="⬇️ Download Markdown Report (.md)",
            data=report_md,
            file_name=filename,
            mime="text/markdown",
            type="primary",
            use_container_width=True,
        )
