# The Lenny Growth Assistant

> **An enterprise-grade conversational AI assistant strictly grounded in 300+ episodes of Lenny's Podcast.**  
> *Built for Senior PMs, Growth Executives, and Founders seeking verifiable tactical wisdom from world-class operators.*

🚀 **Live Deployment**: [https://the-lenny-growth-assistant-jq4i.onrender.com](https://the-lenny-growth-assistant-jq4i.onrender.com)  
📂 **Repository**: [https://github.com/akhil05-g/The-Lenny-Growth-Assistant](https://github.com/akhil05-g/The-Lenny-Growth-Assistant)

---

## 🌟 Key Features

1. **Strictly Grounded Conversational RAG**: Answers synthesized exclusively from 303 podcast episodes (49,781 chunks). Every claim includes direct quotes and deep-linked YouTube timestamps.
2. **Zero-Hallucination Guardrails**: Out-of-domain queries (quantum physics, personal gossip) return a polite refusal — never fabricated content.
3. **Ship 30 for 30 Content Engine**: Transforms operator insights into viral ~1,250-word digital essays following Dickie Bush & Nicolas Cole's 4A framework.
4. **Interactive Sandboxed Artifacts**: Renders interactive HTML/CSS checklists and PM matrices in a Claude-style split screen, safely isolated via `<iframe>` sandboxing.
5. **Real-Time SSE Streaming**: Progressive token-by-token streaming — citations appear in under 1 second.
6. **Multi-Model Dynamic Toggling**: Switch between **Groq** (cloud, free), **Ollama** (local, offline), **Anthropic Claude**, or **OpenAI** via a single `.env` line.
7. **Dual-Engine Database Resilience**: PostgreSQL in production; automatic SQLite fallback for zero-friction local evaluation.
8. **Persistent Chat History**: All sessions, messages, and artifacts are saved to the database and survive browser refresh.

---

## 🚀 Quickstart (One-Command Setup)

### 1. Prerequisites

| Tool | Version | Purpose |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend (only needed to rebuild UI) |
| **Ollama** *(optional)* | Latest | Local offline inference |

To use **local Ollama** inference, install [Ollama](https://ollama.com/) and pull the model:
```bash
ollama run llama3.2:latest
```

### 2. Environment Configuration

Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env   # Mac/Linux
copy .env.example .env  # Windows
```

Edit `.env` and set your preferred provider:

```ini
# ── Provider Selection ──────────────────────────────────────────
# Options: groq | ollama | anthropic | openai | resilient_local
ACTIVE_PROVIDER=groq

# ── Groq (Recommended for evaluators — free, fast, no GPU needed)
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# ── Ollama (Local, fully offline)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# ── Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6

# ── OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# ── Database (SQLite default, PostgreSQL for production)
DATABASE_URL=sqlite+aiosqlite:///./lenny_assistant.db
```

> **Get a free Groq key** (takes 60 seconds): [console.groq.com](https://console.groq.com) → API Keys → Create

### 3. Start the Application (Single Command)

```bash
python run.py
```

*Windows users: double-click `start.bat`*

| Endpoint | URL |
| :--- | :--- |
| **Web App** | http://127.0.0.1:8000 |
| **Swagger API Docs** | http://127.0.0.1:8000/docs |
| **Health Check** | http://127.0.0.1:8000/api/health |

The React frontend is pre-compiled in `frontend/dist/` and served automatically by FastAPI — **no separate `npm start` needed**.

### 4. Docker (Optional — Full Stack with PostgreSQL)

```bash
# Copy env and add your Groq key
cp .env.example .env
# Edit .env: set GROQ_API_KEY=gsk_...

# Build and launch (PostgreSQL + Backend + Frontend)
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)                   │
│   - Glassmorphism Canvas & 3D Iridescent Hero Orb           │
│   - Real-Time Token Streaming via SSE (autoscroll)          │
│   - Side-by-Side Sandboxed Artifact Viewer                  │
│   - Live Model Toggle Pill & Chat History Sidebar           │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / SSE (/api/*)
┌──────────────────────────────▼──────────────────────────────┐
│                    BACKEND (FastAPI API)                     │
│  ┌─────────────────────────┐   ┌─────────────────────────┐  │
│  │    Agent Orchestrator   │   │  Hybrid RAG Engine      │  │
│  │  - Multi-Turn Memory    │◄──┤  - 49,781 Chunks        │  │
│  │  - Intent & Skill Router│   │  - BM25 + Content Boost │  │
│  │  - Ship 30 Skill Engine │   │  - Sponsor/Noise Filter │  │
│  └────────────┬────────────┘   └─────────────────────────┘  │
│               │                                             │
│  ┌────────────▼──────────────────────────────────────────┐  │
│  │            Unified LLM Provider Layer                 │  │
│  │  [Groq Cloud] [Ollama Local] [Claude] [OpenAI]        │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Persistence & Database                     │
│       PostgreSQL (AsyncPG) ──(Failover)──► SQLite           │
│   Sessions | Messages | Artifacts (survives browser refresh)│
└─────────────────────────────────────────────────────────────┘
```

See [`architecture.md`](./architecture.md) for the full database schema, API endpoints, RAG pipeline, and deployment topology.

---

## ⚙️ Model Provider Switching

Switch the active LLM engine via `.env` or the live `/api/models` endpoint:

| Provider | `ACTIVE_PROVIDER` | Notes |
| :--- | :--- | :--- |
| **Groq** *(Recommended)* | `groq` | Free tier at [console.groq.com](https://console.groq.com). Uses `llama-3.1-70b-versatile`. Fast. |
| **Ollama (Local)** | `ollama` | Fully offline. Requires `ollama run llama3.2:latest`. |
| **Anthropic Claude** | `anthropic` | Set `ANTHROPIC_API_KEY=sk-ant-...` |
| **OpenAI GPT-4o** | `openai` | Set `OPENAI_API_KEY=sk-...` |
| **Resilient Fallback** | `resilient_local` | Always-on deterministic engine. Used in CI/CD. |

Check live provider status:
```bash
curl http://127.0.0.1:8000/api/health
# → {"provider": "groq", "is_available": true, "latency_ms": 312}
```

Switch provider at runtime (no restart needed):
```bash
curl -X POST http://127.0.0.1:8000/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "ollama"}'
```

---

## 🧪 Running the Test Suite

```bash
# Install test dependencies
pip install -r backend/requirements.txt

# Run all 7 test modules
python -m pytest tests/ -v
```

| Test File | Coverage |
| :--- | :--- |
| `test_health.py` | System diagnostics, DB connection, knowledge base indexing |
| `test_sessions.py` | Multi-turn session CRUD, message persistence across refresh |
| `test_rag.py` | Transcript chunking, guest filtering, out-of-domain refusal |
| `test_models.py` | Provider discovery, telemetry, runtime model switching |
| `test_ship30.py` | 4A framework structure, ~1,250 word count targets |
| `test_chat_orchestration.py` | Grounded citations, anti-hallucination guardrails, artifact generation |
| `conftest.py` | Shared async fixtures and test database setup |

### Manual UI Test Plan

| Test | Steps | Expected Result |
| :--- | :--- | :--- |
| **RAG grounding** | Ask "What does Brian Chesky say about being in the details?" | Answer with citation cards + YouTube timestamps |
| **Out-of-domain refusal** | Ask "Explain quantum entanglement" | Polite refusal, no hallucination |
| **Ship 30 essay** | Ask "Write a Ship 30 essay about Elena Verna and growth loops" | ~1,250-word essay with 4A structure |
| **Artifact rendering** | Ask "Generate a product execution checklist" | Interactive HTML checklist in side panel |
| **Chat persistence** | Chat, refresh browser, reopen session | Full message history restored |
| **Provider toggle** | Change `ACTIVE_PROVIDER` in `.env`, restart | Health badge shows new provider |

---

## 📂 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── config.py          # Settings (providers, DB, ports)
│   │   ├── database.py        # Async SQLAlchemy (PG + SQLite)
│   │   ├── main.py            # FastAPI app + static frontend serving
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── routers/           # API route handlers
│   │   └── services/
│   │       ├── agent_service.py    # Orchestrator + intent router
│   │       ├── llm_provider.py     # Groq, Ollama, Claude, OpenAI, Fallback
│   │       ├── rag_service.py      # BM25 hybrid retrieval engine
│   │       ├── artifact_service.py # Artifact parsing & sanitization
│   │       └── ship30_skill.py     # Essay generation skill
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/                   # React source (components, hooks, context)
│   └── dist/                  # Pre-compiled bundle (served by FastAPI)
├── data/
│   └── episodes/              # 303 Lenny transcript .txt files
├── tests/                     # Automated pytest test suite
├── agent_transcripts/         # Coding agent logs & debug sessions
├── run.py                     # Single-command launcher
├── start.bat                  # Windows one-click launcher
├── docker-compose.yml         # Full-stack Docker (PG + Backend + Frontend)
├── .env.example               # Environment template (no secrets)
├── README.md
├── PRD.md
├── design.md
└── architecture.md
```

---

## 🛠️ Troubleshooting

| Issue | Symptom | Fix |
| :--- | :--- | :--- |
| **Groq key invalid** | Health shows `is_available: false` | Get a free key at [console.groq.com](https://console.groq.com) |
| **Ollama timeout** | `model_used: resilient_local` instead of `ollama` | Essay generation takes 90–120s on CPU. Timeout is set to 300s. Ensure Ollama is running: `ollama list` |
| **PostgreSQL not running** | Console: `Falling back to local SQLite` | Intended! App auto-creates `lenny_assistant.db`. No action needed. |
| **Frontend not loading** | Browser shows JSON at `localhost:8000` | The pre-built `frontend/dist/` is missing. Run `cd frontend && npm install && npm run build` |
| **Render cold start** | First request takes ~30s | Free tier spins down after 15min inactivity. Normal behavior. |

---

## 📄 Documentation

| Document | Contents |
| :--- | :--- |
| [`PRD.md`](./PRD.md) | Product requirements, user personas, success metrics, real engineering journey |
| [`architecture.md`](./architecture.md) | DB schema, API endpoints, RAG pipeline, agent routing, security model |
| [`design.md`](./design.md) | UI/UX principles, information architecture, interaction states, accessibility |
| [`agent_transcripts/`](./agent_transcripts/) | AI coding session logs including failed attempts and corrections |
