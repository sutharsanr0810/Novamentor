"""
NovaMentor — AI-Driven Multi-Agent Framework for Academic Project
Guidance and Documentation.

Run locally with:
    streamlit run app.py
"""

import streamlit as st
from agents.specialized_agents import AGENT_REGISTRY
from utils.export import build_markdown_report

st.set_page_config(
    page_title="NovaMentor",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- session --
if "project_title" not in st.session_state:
    st.session_state.project_title = ""
if "project_context" not in st.session_state:
    st.session_state.project_context = ""
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

# ------------------------------------------------------------------ sidebar --
with st.sidebar:
    st.markdown("## 🧭 NovaMentor")
    st.caption("AI-Driven Multi-Agent Framework for Academic Project Guidance")

    st.markdown("### API Configuration")
    st.session_state.gemini_api_key = st.text_input(
        "Gemini API key",
        value=st.session_state.gemini_api_key,
        type="password",
        help=(
            "Free key from https://aistudio.google.com/apikey — leave blank "
            "to use offline demo mode with canned responses."
        ),
    )
    if not st.session_state.gemini_api_key:
        st.info("Running in offline demo mode. Add a free Gemini key above for live AI responses.")

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
    st.caption(AGENT_REGISTRY[selected_agent_name].role_description)

    st.markdown("---")
    if st.button("🗑️ Clear this agent's chat", use_container_width=True):
        st.session_state.chat_histories[selected_agent_name] = []
        st.rerun()

# -------------------------------------------------------------------- main --
agent = AGENT_REGISTRY[selected_agent_name]()

st.title(f"{selected_agent_name}")
st.caption(agent.role_description)

# Render existing chat
for msg in agent.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input(f"Ask the {selected_agent_name}...")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = agent.respond(user_input, context=st.session_state.project_context)
        st.markdown(reply)

# ------------------------------------------------------------- report tab --
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
