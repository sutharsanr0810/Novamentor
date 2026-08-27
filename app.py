"""
NovaMentor — AI-Driven Multi-Agent Framework for Academic Project Guidance
"""

import hashlib
import os
import re
import streamlit as st
from agents.specialized_agents import AGENT_REGISTRY
from utils.export import build_markdown_report

st.set_page_config(
    page_title="NovaMentor",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number (0-9)."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        return (
            False,
            "Password must contain at least one special symbol (e.g., @, #, $, !).",
        )
    return True, "Password is valid."


# Pre-configured team logins
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

# Resolve default API key from Streamlit Secrets or Environment Variables
detected_secret_key = ""
try:
    detected_secret_key = (
        st.secrets.get("GEMINI_API_KEY", "")
        or st.secrets.get("GOOGLE_API_KEY", "")
        or os.environ.get("GEMINI_API_KEY", "")
        or os.environ.get("GOOGLE_API_KEY", "")
    )
except Exception:
    detected_secret_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")

# Initialize session state variables
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
    st.session_state.gemini_api_key = detected_secret_key
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}


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
            help="Loaded automatically from Streamlit Secrets if configured. Leave blank for offline demo mode.",
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

    # Instantiate the agent class safely if needed
    if isinstance(raw_agent, type):
        agent = raw_agent()
    else:
        agent = raw_agent

    # Safely inject session history if the agent supports dynamic history assignment
    try:
        setattr(agent, "history", st.session_state.chat_histories[selected_agent_name])
    except (AttributeError, TypeError):
        pass

    st.title(f"{selected_agent_name}")
    st.caption(getattr(agent, "role_description", ""))

    # Render persistent conversation messages
    current_chat = st.session_state.chat_histories[selected_agent_name]
    for msg in current_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input and agent response handling
    user_input = st.chat_input(f"Ask the {selected_agent_name}...")
    if user_input:
        # Render and append user prompt immediately
        st.session_state.chat_histories[selected_agent_name].append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate agent reply
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

        # Save assistant response to state
        st.session_state.chat_histories[selected_agent_name].append(
            {"role": "assistant", "content": reply}
        )
        st.rerun()

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
