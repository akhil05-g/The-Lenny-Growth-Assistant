# The Lenny Growth Assistant

> **An enterprise-grade conversational AI assistant strictly grounded in 300+ episodes of Lenny’s Podcast.**  
> *Built for Senior PMs, Growth Executives, and Founders seeking verifiable tactical wisdom from world-class operators.*

---

## 🌟 Key Features

1. **Strictly Grounded Conversational RAG**: Answers are synthesized exclusively from verified dialogue turns across 303 podcast episodes (49,781 chunks). Every claim includes direct quotes and deep-linked YouTube timestamps.
2. **Zero-Hallucination Guardrails**: If an inquiry falls outside Lenny's podcast domain (e.g. quantum physics, personal gossip), the assistant politely refuses rather than fabricating theories.
3. **Ship 30 for 30 Content Engine**: Automatically formats operator insights into viral, 1,250-word digital essays following Dickie Bush & Nicolas Cole's 4A framework (Actionable, Analytical, Aspirational, Anthropological).
4. **Interactive Sandboxed Artifacts**: Renders interactive HTML/CSS checklists, PM prioritization matrices, and roadmaps in a Claude-style split screen, safely isolated via `<iframe>` sandboxing.
5. **Real-Time Server-Sent Events (SSE) Streaming**: Progressive token-by-token streaming eliminates latency anxiety for long-form essay generation.
6. **Multi-Model Dynamic Toggling**: Run locally on **Ollama (`llama3.2:latest`)** with zero cloud dependencies, or switch instantly to **Anthropic Claude (`claude-sonnet-4-6`)** or **OpenAI (`gpt-4o`)**.
7. **Dual-Engine Database Resilience**: Seamlessly operates on PostgreSQL in production, with automatic fallback to local SQLite for zero-friction local grading.

---

## 🚀 Quickstart (One-Command Setup)

### 1. Prerequisites
- **Python**: 3.11+ (Tested on Python 3.13)
- **Node.js**: 18+ (Tested on Node 22)
- **Ollama**: (Mandatory for local demo) [Download Ollama](https://ollama.com/) and pull the default model:
  ```bash
  ollama run llama3.2:latest
  ```

### 2. Environment Configuration
Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration for local Ollama evaluation:
```ini
ENVIRONMENT=development
PORT=8000
DATABASE_URL=sqlite+aiosqlite:///./lenny_assistant.db
ACTIVE_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-4-6
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
```

### 3. Start the Application (Single Command)
In the project root, run:
```bash
# Windows / Mac / Linux:
python run.py
```
*Or on Windows, simply double-click `start.bat`.*

- **Web Application UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health & Observability Endpoint**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 4. Start the Frontend Web App
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to interact with the application.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)                   │
│   - Glassmorphism Pastel Canvas & 3D Iridescent Orb         │
│   - Real-Time Token Streaming with Autoscroll               │
│   - Side-by-Side Sandboxed Artifact Viewer                  │
│   - Live Model Toggle & Status Pill                         │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / SSE (/api/*)
┌──────────────────────────────▼──────────────────────────────┐
│                    BACKEND (FastAPI API)                    │
│  ┌─────────────────────────┐   ┌─────────────────────────┐  │
│  │    Agent Orchestrator   │   │  Hybrid RAG Engine      │  │
│  │  - Multi-Turn Memory    │◄──┤  - 49,781 Chunks        │  │
│  │  - Intent & Skill Router│   │  - BM25 + Content Boost │  │
│  │  - Ship 30 Skill Engine │   │  - Sponsor/Noise Filter │  │
│  └────────────┬────────────┘   └─────────────────────────┘  │
│               │                                             │
│  ┌────────────▼──────────────────────────────────────────┐  │
│  │            Unified LLM Provider Layer                 │  │
│  │  [Ollama Local] [Claude SDK] [OpenAI] [Resilient]     │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Persistence & Database                     │
│       PostgreSQL (AsyncPG) ──(Failover)──► SQLite           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Running the Test Suite

The automated test suite verifies API integrity, knowledge base indexing, guest filtering, grounding guardrails, and model toggling:

```bash
# Run all automated tests
python -m pytest tests/ -v
```

### Test Suite Coverage:
- `tests/test_health.py`: Verifies system diagnostics, database connection, and knowledge base indexing.
- `tests/test_sessions.py`: Verifies multi-turn session creation, retrieval, and message persistence.
- `tests/test_rag.py`: Verifies transcript chunking, guest filtering (Brian Chesky), and out-of-domain refusal.
- `tests/test_models.py`: Verifies dynamic provider discovery, telemetry, and runtime model switching.
- `tests/test_ship30.py`: Verifies the 4A framework structure and word-count targets.
- `tests/test_chat_orchestration.py`: Verifies grounded citations, anti-hallucination guardrails, and artifact generation.

---

## ⚙️ Model Provider Switching

You can switch the active LLM engine dynamically via `.env` or through the frontend UI:

| Provider | Setting | Prerequisites |
| :--- | :--- | :--- |
| **Ollama (Local)** | `ACTIVE_PROVIDER=ollama` | Ollama running locally with `llama3.2:latest`. Free, private, offline. |
| **Anthropic Claude** | `ACTIVE_PROVIDER=anthropic` | Set `ANTHROPIC_API_KEY=sk-ant-...`. Uses official Anthropic SDK. |
| **OpenAI GPT-4o** | `ACTIVE_PROVIDER=openai` | Set `OPENAI_API_KEY=sk-...`. |
| **Resilient Local** | `ACTIVE_PROVIDER=resilient_local` | Always available deterministic fallback (used for CI/CD). |

Check active provider status at any time:
```bash
curl http://127.0.0.1:8000/api/health
```

---

## 🛠️ Troubleshooting & Known Issues

1. **Ollama Connection Timeout**:
   - *Symptom*: Output shows `model_used: resilient_local` instead of `ollama`.
   - *Fix*: Generating 1,250 words on local hardware takes 60–90 seconds. We raised the client timeout to 300s. Ensure Ollama is running (`ollama list`) and your machine is not out of memory.
2. **PostgreSQL Not Running**:
   - *Symptom*: Warning in console: `Failed to connect to primary DB... Falling back to local SQLite.`
   - *Fix*: This is an intended resilience feature. The app automatically creates `lenny_assistant.db` locally. No action needed!
3. **Thunder Client / Postman "Invalid URL"**:
   - *Fix*: Ensure the target URL is exactly `http://127.0.0.1:8000/api/chat` with no trailing spaces.

---

## 📄 Documentation Links
- **PRD**: [`PRD.md`](./PRD.md)
- **Architecture**: [`architecture.md`](./architecture.md)
- **UI/UX Design**: [`design.md`](./design.md)
- **Assignment Brief**: [`assignment_text.txt`](./assignment_text.txt)
