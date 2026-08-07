"""
base_agent.py
Base class for all NovaMentor agents. Handles calls to the Anthropic API
and falls back to a offline template response when no API key is set,
so the app is fully demoable without credentials.
"""

import os
import streamlit as st

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

MODEL_NAME = "claude-sonnet-4-6"


class BaseAgent:
    """
    Parent class for every specialised agent (Requirement Analyzer,
    Research Assistant, Code Mentor, Documentation Generator, Viva Coach).

    Subclasses only need to set `name`, `role_description`, and
    `system_prompt`. Everything else (API call, offline fallback,
    chat history) is handled here.
    """

    name = "Base Agent"
    role_description = "Generic agent"
    system_prompt = "You are a helpful assistant."
    offline_fallback = (
        "This is demo/offline mode (no API key set in the sidebar). "
        "Add your Anthropic API key to get real responses from this agent."
    )

    def __init__(self):
        if "chat_histories" not in st.session_state:
            st.session_state.chat_histories = {}
        if self.name not in st.session_state.chat_histories:
            st.session_state.chat_histories[self.name] = []

    @property
    def history(self):
        return st.session_state.chat_histories[self.name]

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def reset(self):
        st.session_state.chat_histories[self.name] = []

    def _get_client(self):
        api_key = st.session_state.get("anthropic_api_key", "").strip()
        if not api_key or not ANTHROPIC_AVAILABLE:
            return None
        try:
            return anthropic.Anthropic(api_key=api_key)
        except Exception:
            return None

    def respond(self, user_input, context=""):
        """
        Sends user_input (plus any project context) to the model using
        this agent's system prompt, and returns the assistant's reply.
        Falls back to a canned response if no API key is configured.
        """
        self.add_message("user", user_input)

        client = self._get_client()
        if client is None:
            reply = self._offline_reply(user_input)
            self.add_message("assistant", reply)
            return reply

        full_system_prompt = self.system_prompt
        if context:
            full_system_prompt += f"\n\nProject context provided by the student:\n{context}"

        try:
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in self.history
                if m["role"] in ("user", "assistant")
            ]
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=1500,
                system=full_system_prompt,
                messages=api_messages,
            )
            reply = "".join(
                block.text for block in response.content if block.type == "text"
            )
        except Exception as e:
            reply = f"⚠️ API error: {e}\n\n{self._offline_reply(user_input)}"

        self.add_message("assistant", reply)
        return reply

    def _offline_reply(self, user_input):
        return (
            f"**[{self.name} — offline demo reply]**\n\n"
            f"{self.offline_fallback}\n\n"
            f"You asked: _{user_input}_"
        )
