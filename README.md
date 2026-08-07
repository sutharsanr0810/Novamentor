# NovaMentor

**AI-Driven Multi-Agent Framework for Academic Project Guidance and Documentation**

NovaMentor is a Streamlit application that guides a student through a college
project using five specialised AI agents:

| Agent | Helps you with |
|---|---|
| 🧩 Requirement Analyzer | Turning a rough idea into a scoped problem statement, objectives, and milestones |
| 📚 Research Assistant | Framing your literature review and articulating novelty |
| 💻 Code Mentor | Architecture, tech stack choices, and implementation approach |
| 📝 Documentation Generator | Drafting abstracts, chapters, and report sections |
| 🎤 Viva & Presentation Coach | Anticipating viva questions and structuring your presentation |

Each agent shares the same project context (entered once in the sidebar) so
answers stay consistent across agents, and every conversation can be exported
as a single Markdown report at the end.

## Features

- Multi-agent chat UI built with Streamlit's native `st.chat_message`
- Shared project context injected into every agent's system prompt
- Works fully **offline in demo mode** (no API key needed) with canned
  responses, or with **live responses** from the Anthropic API when you add
  your own key
- One-click export of the full session as a Markdown report

## Getting started

### 1. Clone and install

```cmd
git clone https://github.com/<your-username>/novamentor.git
cd novamentor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run

```cmd
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### 3. (Optional) Add an API key

Paste an [Anthropic API key](https://console.anthropic.com/) into the sidebar
to get live AI responses instead of offline demo replies. The key is only
kept in your browser session — it is never written to disk or committed.

## Project structure

```
novamentor/
├── app.py                        # Streamlit entry point / UI
├── agents/
│   ├── base_agent.py             # Shared agent logic (API calls, offline fallback)
│   └── specialized_agents.py     # The 5 NovaMentor agents
├── utils/
│   └── export.py                 # Markdown report builder
├── .streamlit/
│   └── config.toml               # Theme
├── requirements.txt
└── README.md
```

## Deploying

The app is ready to deploy on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this repo to GitHub (see below).
2. On share.streamlit.io, click **New app**, pick this repo and `app.py`.
3. Add `ANTHROPIC_API_KEY` under app **Secrets** if you want it pre-filled
   (or just let users paste their own key in the sidebar).

## License

MIT
