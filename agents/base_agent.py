"""
base_agent.py
Base class for all NovaMentor agents. Calls Google's Gemini API (free tier,
no credit card required) and falls back to an offline template response
when no API key is set, so the app is fully demoable without credentials.
"""

import streamlit as st

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

MODEL_NAME = "gemini-2.5-flash"


class BaseAgent:
    name = "Base Agent"
    role_description = "Generic agent"
    system_prompt = "You are a helpful assistant."
    offline_fallback = (
        "This is demo/offline mode (no API key set in the sidebar). "
        "Add a free Gemini API key to get real responses from this agent."
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

    def _get_model(self, system_prompt):
        api_key = st.session_state.get("gemini_api_key", "").strip()
        if not api_key or not GEMINI_AVAILABLE:
            return None
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(
                model_name=MODEL_NAME,
                system_instruction=system_prompt,
            )
        except Exception:
            return None

    def respond(self, user_input, context=""):
        self.add_message("user", user_input)

        full_system_prompt = self.system_prompt
        if context:
            full_system_prompt += "\n\nProject context provided by the student:\n" + context

        model = self._get_model(full_system_prompt)
        if model is None:
            reply = self._offline_reply(user_input)
            self.add_message("assistant", reply)
            return reply

        try:
            gemini_history = [
                {
                    "role": "user" if m["role"] == "user" else "model",
                    "parts": [m["content"]],
                }
                for m in self.history[:-1]
                if m["role"] in ("user", "assistant")
            ]
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(user_input)
            reply = response.text
        except Exception as e:
            reply = "API error: " + str(e) + "\n\n" + self._offline_reply(user_input)

        self.add_message("assistant", reply)
        return reply

    def _offline_reply(self, user_input):
        return (
            "**[" + self.name + " — offline demo reply]**\n\n"
            + self.offline_fallback + "\n\n"
            + "You asked: _" + user_input + "_"
        )
