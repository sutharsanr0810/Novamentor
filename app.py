"""
NovaMentor — AI-Driven Multi-Agent Framework for Academic Project Guidance
Single-File Complete Edition
"""

import datetime
import hashlib
import os
import re
import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NovaMentor",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- UTILITIES: EXPORT GENERATOR ---
def build_markdown_report(title: str, context: str, chat_histories: dict) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc_title = title.strip() if title.strip() else "Academic Project Guidance Report"

    lines = [
        f"# 🧭 NovaMentor Academic Guidance Report",
        f"**Project Title:** {doc_title}  ",
        f"**Generated On:** {timestamp}  ",
        f"\n---\n",
        f"## 📋 Project Context & Scope",
        f"{context.strip() if context.strip() else 'No project context recorded.'}",
        f"\n---\n",
        f"## 💬 Multi-Agent Consultation Transcripts\n",
    ]

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

    if not has_chats:
        lines.append("_No agent conversations were recorded during this session._")

    return "\n".join(lines)


# --- AGENTS: SPECIALIZED AGENT CLASSES ---
class BaseMentorAgent:
    name: str = "Base Agent"
    role_description: str = "Academic project mentor."
    system_prompt: str = "You are a helpful academic project mentor."

    def __init__(self):
        self.history = []

    def respond(self, prompt: str, context: str = "", api_key: str = "") -> str:
        clean_key = (api_key or "").strip().strip("'").strip('"')

        if not clean_key:
            return (
                f"**[{self.name} — Offline Demo Mode]**\n\n"
                f"To receive live AI-generated guidance, please enter a valid Google Gemini API key in the sidebar.\n\n"
                f"*Offline Preview Response for:* '{prompt}'\n"
                f"- Project Context Registered: {'Yes' if context else 'None provided'}\n"
                f"- Recommendation: Define clear scope, baseline metrics, and IEEE reference standards."
            )

        try:
            genai.configure(api_key=clean_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=self.system_prompt,
            )

            full_prompt = (
                f"### Overall Project Context:\n{context or 'No specific context provided.'}\n\n"
                f"### Student Query:\n{prompt}"
            )

            response = model.generate_content(full_prompt)
            return response.text

        except Exception as err:
            return (
                f"**API Error Encountered:**\n"
                f"```text\n{str(err)}\n```\n"
                f"**Troubleshooting:**\n"
                f"1. Ensure the key from [Google AI Studio](https://aistudio.google.com/) is copied correctly.\n"
                f"2. Confirm you haven't exceeded your free tier rate limit."
            )


class RequirementAnalyzerAgent(BaseMentorAgent):
    name = "Requirement Analyzer"
    role_description = "Turns a rough project idea into clear scope, objectives, and milestones."
    system_prompt = (
        "You are an expert Academic Requirement Analyst. Break down student project ideas "
        "into structured Problem Statements, Functional/Non-Functional Requirements, "
        "Hardware/Software constraints, and IEEE-style deliverables."
    )


class ArchitectureAgent(BaseMentorAgent):
    name = "System Architect"
    role_description = "Designs system pipelines, data flows, and hardware/software architectures."
    system_prompt = (
        "You are a Senior Academic System Architect. Propose end-to-end technical pipelines, "
        "data flow diagrams (using Mermaid.js where helpful), component interaction layouts, "
        "and optimal module selections for computer science and engineering projects."
    )


class ResearchReviewerAgent(BaseMentorAgent):
    name = "Literature Reviewer"
    role_description = "Finds research gaps, baseline models, and academic benchmarks."
    system_prompt = (
        "You are an Academic Research Mentor. Identify relevant IEEE/ACM research gaps, "
        "state-of-the-art baseline models, benchmark datasets, and standard evaluation metrics (e.g., F1, mAP, Latency)."
    )


class ImplementationAgent(BaseMentorAgent):
    name = "Implementation Guide"
    role_description = "Provides pseudocode, optimization advice, and tech-stack choices."
    system_prompt = (
        "You are a Senior Software Engineer and Implementation Mentor. Provide clean, modular "
        "Python/C++ pseudocode, pipeline optimization techniques, and library recommendations (PyTorch, OpenCV, TensorRT)."
    )


class VivaPrepAgent(BaseMentorAgent):
    name = "Viva & Defense Examiner"
    role_description = "Conducts mock project defense Q&A sessions with rigorous examiner questions."
    system_prompt = (
        "You are a strict Project Defense Examiner. Ask critical questions about trade-offs, "
        "computational bottlenecks, edge failure cases, ethical implications, and performance validation."
    )


AGENT_REGISTRY = {
    "Requirement Analyzer": RequirementAnalyzerAgent,
    "System Architect": ArchitectureAgent,
    "Literature Reviewer": ResearchReviewerAgent,
    "Implementation Guide": ImplementationAgent,
    "Viva & Defense Examiner": VivaPrepAgent,
}


# --- AUTHENTICATION HELPERS ---
def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number (0-9)."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        return False, "Password must contain at least one special symbol (e.g., @, #, $, !)."
    return True, "Password is valid."


USER_DB = {
    "visanth": {
        "name": "Visanth K",
        "roll_no": "7376242AL220",
        "password_hash": hashlib.sha256("Visanth@2026".encode()).hexdigest(),
    },
    "ramkumar": {
        "name": "Ramkumar V",
        "roll_no": "7376242AL171",
        "password_hash": hashlib.sha256("Ramkumar@2026".encode()).hexdigest(),
    },
    "sutharsan": {
        "name": "Sutharsan R",
        "roll_no": "7376242AL202",
        "password_hash": hashlib.sha256("Sutharsan@2026".encode()).hexdigest(),
    },
    "student": {
        "name": "Demo Student",
        "roll_no": "7376242AL000",
        "password_hash": hashlib.sha256("Student@2026".encode()).hexdigest(),
    },
}

# --- INITIALIZE SESSION STATE ---
default_secret_key = ""
try:
    default_secret_key = (
        st.secrets.get("GEMINI_API_KEY", "")
        or st.secrets.get("GOOGLE_API_KEY", "")
        or os.environ.get("GEMINI_API_KEY", "")
    )
except Exception:
    default_secret_key = os.environ.get("GEMINI_API_KEY", "")

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
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = default_secret_key
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}


# --- RENDER LOGIN VIEW ---
def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🧭 NovaMentor")
        st.markdown("### Multi-Agent Academic Portal Login")
        st.caption("Enter your credentials to access the workspace.")

        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input("Username").strip().lower()
            password_input = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                is_valid, error_msg = validate_password_strength(password_input)
                if not is_valid:
                    st.error(f"⚠️ {error_msg}")
                elif username_input in USER_DB:
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

        st.info(
            "**Password Criteria Required:**\n"
            "- Minimum 8 characters\n"
            "- At least 1 number (0-9)\n"
            "- At least 1 special symbol (@, #, $, !, etc.)\n\n"
            "**Pre-configured Credentials:**\n"
            "- `visanth` / `Visanth@2026`\n"
            "- `ramkumar` / `Ramkumar@2026`\n"
            "- `sutharsan` / `Sutharsan@2026`\n"
            "- `student` / `Student@2026`"
        )


# --- MAIN APPLICATION WORKSPACE ---
if not st.session_state.authenticated:
    render_login()
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_fullname}")
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.user_fullname = ""
            st.rerun()

        st.markdown("---")
        st.markdown("## 🧭 NovaMentor")
        st.caption("AI-Driven Multi-Agent Framework for Academic Project Guidance")

        st.markdown("### API Configuration")
        user_key_input = st.text_input(
            "Gemini API key",
            value=st.session_state.gemini_api_key,
            type="password",
            help="Loaded automatically from secrets or paste your AI Studio key here.",
        )
        st.session_state.gemini_api_key = user_key_input.strip()

        if st.session_state.gemini_api_key:
            st.success("✅ Gemini API Key active")
        else:
            st.warning("⚠️ No key provided. Running in offline demo mode.")

        st.markdown("### Your Project")
        st.session_state.project_title = st.text_input(
            "Project title", value=st.session_state.project_title
        )
        st.session_state.project_context = st.text_area(
            "Project context (idea, domain, constraints, progress so far)",
            value=st.session_state.project_context,
            height=160,
            help="Shared with every agent so they give context-aware answers.",
        )

        st.markdown("### Agents")
        agent_names = list(AGENT_REGISTRY.keys())
        selected_agent_name = st.radio(
            "Choose an agent to talk to",
            agent_names,
            format_func=lambda n: n,
            label_visibility="collapsed",
        )

        raw_agent = AGENT_REGISTRY[selected_agent_name]
        role_desc = getattr(raw_agent, "role_description", "")
        if not role_desc and isinstance(raw_agent, type):
            role_desc = getattr(raw_agent(), "role_description", "")
        st.caption(role_desc)

        st.markdown("---")
        if st.button("🗑️ Clear this agent's chat", use_container_width=True):
            st.session_state.chat_histories[selected_agent_name] = []
            st.rerun()

    # Ensure message history exists for the selected agent
    if selected_agent_name not in st.session_state.chat_histories:
        st.session_state.chat_histories[selected_agent_name] = []

    # Safe agent initialization
    agent = raw_agent() if isinstance(raw_agent, type) else raw_agent

    try:
        agent.history = st.session_state.chat_histories[selected_agent_name]
    except (AttributeError, TypeError):
        pass

    st.title(f"{selected_agent_name}")
    st.caption(getattr(agent, "role_description", ""))

    # Render previous conversation history
    current_chat = st.session_state.chat_histories[selected_agent_name]
    for msg in current_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle chat input and generation
    user_input = st.chat_input(f"Ask the {selected_agent_name}...")
    if user_input:
        st.session_state.chat_histories[selected_agent_name].append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = agent.respond(
                        user_input,
                        context=st.session_state.project_context,
                        api_key=st.session_state.gemini_api_key,
                    )
                except TypeError:
                    reply = agent.respond(
                        user_input,
                        context=st.session_state.project_context,
                    )
                st.markdown(reply)

        st.session_state.chat_histories[selected_agent_name].append(
            {"role": "assistant", "content": reply}
        )
        st.rerun()

    # Export report module
    st.markdown("---")
    with st.expander("📄 Export project report (combines all agent conversations)"):
        report_md = build_markdown_report(
            st.session_state.project_title,
            st.session_state.project_context,
            st.session_state.chat_histories,
        )
        st.text_area("Preview", report_md, height=250)
        st.download_button(
            "Download as Markdown",
            data=report_md,
            file_name=f"{(st.session_state.project_title or 'novamentor_report').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
