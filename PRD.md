# Product Requirements Document (PRD)
## Project: The Lenny Growth Assistant (Forward Deployed Engineer Engagement)

---

### Executive Summary (The Non-Technical Brief)
Imagine having a top-tier Silicon Valley product advisor sitting beside you 24/7. When a founder or product manager asks, *"How should I structure my roadmap?"* or *"What did Brian Chesky actually say about micromanagement versus being in the details?"*, they don't want generic ChatGPT fluff. They want exact, battle-tested wisdom from world-class operators who built companies like Airbnb, Figma, Notion, and Stripe.

**The Lenny Growth Assistant** turns over 300 in-depth episodes (~500+ hours) of *Lenny’s Podcast* into an enterprise-grade AI advisor. It does three things exceptionally well:
1. **Answers truthfully**: Every single answer is strictly grounded in real quotes from real podcast episodes with verifiable YouTube timestamps. If Lenny's guests didn't talk about it, the system politely refuses rather than inventing falsehoods.
2. **Writes publication-ready essays**: Transforms rough conversational ideas into structured, 1,250-word digital essays following the proven **Ship 30 for 30** framework.
3. **Generates live interactive tools (Artifacts)**: Spits out interactive HTML checklists, PM prioritization matrices, and roadmaps that render natively inside the application rather than just dump raw code.

---

## 1. Forward Deployment Brief (Discovery & Scoping)

### 1.1 The Primary Persona & Job-To-Be-Done (JTBD)
- **Primary Persona**: Senior Product Managers, Group PMs, and Startup Founders facing high-stakes product decisions (pricing pivots, retention loops, founder-led leadership, zero-to-one product design).
- **Core Job-To-Be-Done**:
  > *"When I am formulating an executive memo or product strategy, I want to extract verified, tactical lessons from proven operators without manually listening to 500 hours of audio or reading scattered notes, so that I can make high-conviction decisions backed by real-world precedent."*
- **The Core Pain Points Removed**:
  1. **The Discovery Abyss**: Finding the 5 minutes of gold in a 2-hour interview requires agonizing keyword searches across YouTube show notes.
  2. **The Hallucination Risk**: Generic LLMs hallucinate plausible-sounding consultant jargon. Our client cannot afford to present ungrounded theories in executive meetings.
  3. **The Translation Friction**: Turning raw dialogue into an actionable format (a structured memo, a 4A essay, or a functioning checklist) normally takes 3–4 hours of manual drafting.

---

### 1.2 Measurable Success Metrics

| Metric | Target | Real-World Measurement |
| :--- | :--- | :--- |
| **Grounding Faithfulness Rate** | **> 95%** | Percentage of claims directly supported by retrieved podcast transcript citations. Automated checks verify that claims map to real timestamps. |
| **Zero-Hallucination Out-of-Domain Refusal** | **100%** | When asked about quantum physics or personal gossip, the system refuses to guess and cleanly states knowledge boundaries. |
| **Time-to-First-Token (Streaming UX)** | **< 2.0s** | Rather than freezing for 90s on long essays, tokens stream progressively via Server-Sent Events (SSE). |
| **Evaluator Time-to-First-Query (TTFQ)** | **< 3 minutes** | A fresh evaluator can clone the repo, run a single command, and successfully query the assistant with zero setup friction. |

---

### 1.3 Real Engineering Journey: Assumptions, Mistakes & Discoveries

A true Forward Deployed Engineer doesn't write hypothetical PRDs—they ground them in what happened when the system collided with reality. Here is the unvarnished engineering story:

#### A. The Early Scoping Call: Reusing the 300k+ CNN/DailyMail Dataset
*Initial Thought*: We had an existing academic summarization project trained on 300,000+ CNN/DailyMail articles. Could we adapt it?  
*The Decision*: **No.** CNN/DailyMail is generic news summarization, not conversational dialogue retrieval. It cannot attribute quotes to Brian Chesky or Elena Verna, and it does not support multi-turn conversational search. We chose to build a dedicated RAG pipeline tailored specifically to podcast dialogue transcripts with speaker timestamps.

#### B. Avoiding the "Overengineering Trap" Under a 48-Hour Deadline
*Initial Draft*: An initial AI-generated architecture proposed dual vector databases, complex Redis caching, hybrid BM25 + dense neural embeddings, and audio-synchronization web players.  
*The Pragmatic Pivot*: Given the tight September 15 deadline, building complex infrastructure that breaks during evaluation is a fatal consultant mistake. We made a conscious trade-off: **functional depth over infrastructure bloat**. We prioritized rock-solid lexical and topical RAG retrieval, native SSE streaming, and secure artifact sandboxing over brittle audio sync.

#### C. Bug 1: Silent Fallback Masking Long-Form Failures
*The Discovery*: During early manual testing, `/api/chat` worked fine with Ollama, but the Ship 30 essay endpoint returned `model_used: resilient_local`—it was falling back to the hardcoded stub without throwing an error.  
*Root Cause*:
1. Ollama's HTTP client had a 60-second read timeout. Generating an in-depth 1,250-word essay on local hardware takes 90–120 seconds. Exactly at 60 seconds, `httpx` threw a `ReadTimeout`.
2. Ollama's default context window is 2,048 tokens. Feeding 5 full transcript chunks overflowed the context buffer.
3. The fallback handler caught the error and silently redirected to the stub.  
*The Solution*: Raised the timeout to 300 seconds (5 minutes), explicitly set `num_ctx: 8192`, and added structured error logging.

#### D. Bug 2: The "Smarter Mock" Trap (Caught & Reverted)
*The Temptation*: When the stub returned a short 337-word essay with hardcoded guest names, the initial quick-fix impulse was to write code inside the stub to extract the guest name and repeat paragraphs to hit 1,250 words.  
*The Senior Engineering Call*: **Stop and revert immediately.** Padding a mock produces fake output that looks convincing on the surface but is completely ungrounded and fails the core evaluation criteria. We deleted the padded filler and focused on getting real Ollama inference working end-to-end.

#### E. Bug 3: Shallow Grounding & Podcast Banter
*The Discovery*: When testing `"Brian Chesky founder mode leadership"`, the retrieval engine returned Chesky's podcast intro chatter (*"Today my guest is Brian Chesky..."*, *"The rabbit hole goes deep"*) instead of his substantive leadership advice.  
*Root Cause*: Chunks were too short (15 words), and the BM25 index included the guest name in every chunk. Short banter chunks had artificially high keyword density for "Brian Chesky", drowning out 300-word paragraphs on micromanagement and roadmaps.  
*The Solution*: Raised the minimum chunk size to 40 words, added automated noise filters for sponsor reads and intros, and boosted body text matches on topical terms (`founder`, `leadership`, `details`, `micromanagement`) by 4.0x over generic name repetition.

#### F. Bug 4: The Word Count Deficit
*The Discovery*: Ollama naturally produced ~500 words when asked to write an essay, falling well short of the ~1,250-word requirement.  
*The Solution*: Encoded explicit section-by-section word budgets directly into the prompt: 100 words for the Hook, 100 for Credibility, 250–300 each for the 4As (Actionable, Analytical, Aspirational, Anthropological), and 100 for the Takeaway.

#### G. Bug 5: Latency & The Perceived Performance UX Risk
*The Discovery*: A user waiting 90 seconds in front of a frozen screen will assume the app crashed and close the tab.  
*The Solution*: Built **Server-Sent Events (SSE) streaming** across the entire stack (`/api/chat/stream` and `/api/skills/ship30/stream`). Citations appear within 1 second, and words stream onto the screen in real-time.

#### H. Intentional Scope Choice: Purpose-Built Corpus vs. Generic File Uploader
*The Architecture Decision*: We consciously scoped the application around Lenny's Podcast corpus (303 episodes, 49,781 dialogue chunks, 301 verified guests) pre-ingested and indexed at deployment time, rather than turning the app into a generic "upload any random podcast transcript" utility.  
*The Rationale*:
> *"The Lenny Growth Assistant is purpose-built around Lenny's Podcast corpus, pre-ingested at deployment time. It is not designed as a general-purpose podcast-analysis tool — this focused scope allows for deeper domain-specific retrieval tuning (guest-aware chunking, topic weighting) rather than a generic ingestion pipeline that would need to handle arbitrary transcript formats and quality levels."*
This intentional constraint allows an evaluator to clone the repository, run a single command, and immediately interrogate the knowledge base with zero manual file uploads. It also enables specialized BM25 scoring tailored to conversational podcast dialogues, speaker-turn timestamps, and YouTube deep-linking.

#### I. Bug 6: Eliminating Hallucinated Metadata Placeholders ("(Episode X, Timestamp Y)")
*The Discovery*: When asked open-ended questions like *"Which episodes of Andy Raskin should I explore?"*, local compact LLMs (Llama 3.2 3B) defaulted to templated placeholders like `* "The power of strategic narrative" (Episode X, Timestamp Y)`.  
*Root Cause*: The model attempted to satisfy the citation format instructed in the prompt without referencing the exact metadata fields provided in the RAG context block.  
*The Solution*: Implemented strict negative prompting: `"NO PLACEHOLDERS: NEVER output placeholder tokens like (Episode X, Timestamp Y) or (Episode #, Time). If citing an episode, use the EXACT episode title and timestamp provided in the GROUNDED PODCAST TRANSCRIPTS section. If exact timestamps are unavailable, discuss the guest and insight directly without placeholder parentheses."`

---

## 2. Technical Architecture & Component Specification

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                         │
│  ┌───────────────────────┐  ┌────────────────────────────────────────┐  │
│  │   Chat Conversation   │  │       Side-by-Side Artifact Viewer     │  │
│  │  - Progressive Stream │  │  - Sandboxed <iframe> (allow-scripts)  │  │
│  │  - Source Citation    │  │  - Live Preview / Raw Source Toggle    │  │
│  │  - Model Switcher     │  │  - One-Click Copy & Export             │  │
│  └───────────────────────┘  └────────────────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / SSE Stream
┌───────────────────────────────────▼────────────────────────────────────┐
│                       BACKEND (FastAPI API Layer)                      │
│                                                                        │
│  ┌─────────────────────────┐         ┌──────────────────────────────┐  │
│  │    Agent Orchestration  │         │   Hybrid RAG Retrieval       │  │
│  │  - Intent Classifier    │◄────────┤   - 49,781 Chunks (303 Eps)  │  │
│  │  - Multi-Turn Session   │         │   - BM25 + Content Weighting │  │
│  │  - Ship 30 Skill Engine │         │   - Noise & Sponsor Filter   │  │
│  └────────────┬────────────┘         └──────────────────────────────┘  │
│               │                                                        │
│  ┌────────────▼─────────────────────────────────────────────────────┐  │
│  │                    Unified LLM Provider Layer                    │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │  │
│  │  │ Ollama Local │ │ Claude (SDK) │ │  OpenAI GPT  │ │ Resilient│ │  │
│  │  │ (Mandatory)  │ │(Real Key Ok) │ │  (API Key)   │ │ Fallback │ │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    Persistence & Storage (Async SQL)                   │
│         Primary: PostgreSQL  ──(Failover)──► Local SQLite             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Product Functional Requirements

### 3.1 Grounded Conversational RAG
- **Session Memory**: Maintains multi-turn context (last 6 dialogue turns) within isolated session UUIDs.
- **Source Citation Cards**: Every grounded claim renders an interactive badge featuring:
  - Guest Name (e.g. *Brian Chesky*)
  - Episode Title (e.g. *Brian Chesky’s new playbook*)
  - Exact Timestamp (e.g. `(00:32:17)`)
  - Direct Quote
  - Deep-linked YouTube URL with timestamp parameter (`&t=1937s`).
- **Strict Anti-Hallucination Refusal**: If RAG retrieves no relevant transcripts, returns the standardized refusal:
  > *"I could not find information on this in Lenny's podcast transcripts. The Lenny Growth Assistant strictly answers using verified insights from Lenny Rachitsky's podcast episodes..."*

### 3.2 Ship 30 for 30 Content Skill
- Transforms retrieved transcript evidence into a viral digital essay following Dickie Bush & Nicolas Cole's framework:
  1. **Magnetic Hook**: 3–4 short, punchy sentences confronting an industry myth.
  2. **Authority Statement**: Positioned as synthesized playbooks from Lenny's guests.
  3. **The 4A Framework**:
     - **Actionable**: Tactical operating systems and workflows.
     - **Analytical**: Metrics, cadence of review, and unit economics.
     - **Aspirational**: Founder-led vision and category creation.
     - **Anthropological**: Organizational debt, team resistance, and why consensus fails.
  4. **One High-Impact Takeaway**: A non-obvious, decisive action item for the reader.
  5. **Length**: 1,100 to 1,300 words.

### 3.3 Sandboxed Artifact Generation
- Detects artifact generation requests and outputs clean, structured markdown:
  ```markdown
  :::artifact title="Product Execution Checklist" type="html"
  <div style="...">...</div>
  :::
  ```
- **Security Sandboxing**: Rendered inside an `<iframe>` configured strictly with:
  ```html
  <iframe sandbox="allow-scripts" srcdoc="..."></iframe>
  ```
  `allow-same-origin` is explicitly forbidden, ensuring the generated artifact can never access parent DOM, local storage, or cookies.

---

## 4. Operational Handover & Deployment Specification

### 4.1 Zero-Setup Evaluation Strategy
- Evaluators should never fail due to missing dependencies.
- Dual-database failover:
  - Attempts PostgreSQL connection via `DATABASE_URL`.
  - If PostgreSQL is unconfigured or unreachable, silently and reliably initializes `lenny_assistant.db` via SQLite.
- Multi-Model Toggle:
  - Controlled by a single line in `.env`: `ACTIVE_PROVIDER=ollama` (or `anthropic`, `openai`, `resilient_local`).
  - Evaluated honestly via `GET /api/health`.

### 4.2 Observability & Diagnostics
- Every LLM request logs provider name, execution latency (ms), token stream health, and status codes.
- `/api/health` reports status for Database, Knowledge Base (total chunks, guests, topics indexed), and active LLM availability.

---

## 5. Verification & Test Log (Manual & Automated Evidence)

### 5.1 Automated Test Suite
- Comprehensive tests in `tests/`:
  - `test_health.py`: Health check and system discovery endpoints.
  - `test_sessions.py`: Multi-session CRUD and persistence.
  - `test_rag.py`: Knowledge base initialization, guest filtering, and out-of-domain refusal.
  - `test_models.py`: Provider discovery, model listing, and switching telemetry.
  - `test_ship30.py`: Essay generation structure and word count validation.
  - `test_chat_orchestration.py`: Multi-turn conversational grounding, anti-hallucination refusal, and artifact extraction.

### 5.2 Manual API Verification Screenshots
The following manual test runs have been executed and verified in Postman / Thunder Client with screenshot evidence:

1. **`Screenshot 2026-09-13 140759.png`**:
   - Verification of `/api/health` reporting honest model availability and database health.
2. **`Screenshot 2026-09-13 151147.png`**:
   - Verification of `/api/skills/ship30` running under local Ollama, returning genuine generated content and verified transcript citations.

---

## 6. Deployment

- **Live URL**: [https://the-lenny-growth-assistant-jq4i.onrender.com](https://the-lenny-growth-assistant-jq4i.onrender.com)
- **GitHub Repo**: [https://github.com/akhil05-g/The-Lenny-Growth-Assistant](https://github.com/akhil05-g/The-Lenny-Growth-Assistant)
- **Cloud LLM**: Groq (`llama-3.1-70b-versatile`) — free tier, ultra-fast inference
- **Local LLM**: Ollama (`llama3.2:latest`) — fully offline, no API key needed
- **Database**: PostgreSQL (Docker/production) with automatic SQLite fallback (local evaluation)

---

## 7. Deliverable Readiness Checklist

| Deliverable | Description | Status |
| :--- | :--- | :--- |
| **1. Public GitHub Repo** | Clean code, sensible structure, no committed secrets. | 🟢 **Complete** |
| **2. README.md** | Architecture overview, prerequisites, setup, env vars, tests, troubleshooting. | 🟢 **Complete** |
| **3. PRD.md** | User, problem, success metrics, flows, risks, real engineering journey. | 🟢 **Complete** |
| **4. design.md** | UI/UX principles, information architecture, interaction states, accessibility. | 🟢 **Complete** |
| **5. architecture.md** | DB schema, API endpoints, RAG pipeline, agent routing, security, deployment. | 🟢 **Complete** |
| **6. Agent Transcripts** | Coding agent logs with failed attempts, debugging, and corrections. | 🟢 **Complete** |
| **7. Tests** | Automated pytest suite (7 modules) + manual UI test plan. | 🟢 **Complete** |
| **8. Demo Video** | 2–3 minute walk-through (YouTube). | 🟡 To be recorded |
