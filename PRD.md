# Product Requirements Document
## The Lenny Growth Assistant
**Forward Deployed Engineer — Take-Home Engagement**

**Author:** Akhil  
**Date:** September 2026  
**Status:** Complete — backend and frontend built and verified  

---

## 1. Overview

The Lenny Growth Assistant is a grounded, conversational AI application built on top of the full transcript archive of *Lenny's Podcast* — a well-known product management and growth podcast. It lets a user ask questions about specific guests, frameworks, and stories from the show, and get answers that are backed by real quotes and timestamps rather than general AI knowledge.

Beyond Q&A, the assistant can also turn an answer into a long-form essay in the "Ship 30 for 30" writing style, and generate small interactive documents (checklists, summaries) that render safely inside the app.

This document explains who the product is for, what it needs to do, the decisions made while building it, and — since a real engineering process is never a straight line — the problems that came up along the way and how they were resolved.

---

## 2. Problem Statement & Users

**Who this is for:** Product managers, founders, and growth leads who want specific, credible insight from proven operators — without spending hours re-listening to old episodes to find the one relevant answer.

**The job to be done:** *"When I'm making a product or leadership decision, I want to pull a real, attributable lesson from someone who's actually done it — quickly, and without having to trust an AI that might just be making it sound plausible."*

**The core pain points this removes:**
- **Finding the needle in the haystack.** A single useful answer might be buried in a 2-hour interview.
- **Trusting the answer.** General-purpose LLMs will confidently invent detail if you let them. That's not acceptable when the output might inform a real business decision.
- **Turning insight into something usable.** Raw transcript quotes aren't the same as a structured, shareable write-up.

---

## 3. Success Metrics

| Metric | Target | How it's measured |
|---|---|---|
| Grounding accuracy | Answers should be traceable to a real transcript quote | Verified manually by checking that returned sources actually support the claim made |
| Out-of-domain refusal | The assistant should say "I don't know" rather than guess | Tested directly with questions outside the podcast's scope (see Section 7) |
| Setup friction | An evaluator should be able to run the app with one command | Verified via Docker Compose startup |
| Perceived responsiveness | The user shouldn't feel like the app has frozen during long generations | Addressed via streaming (Section 6) |

---

## 4. Scope Decisions & Assumptions

The brief for this assignment was intentionally open-ended. Here's what was assumed, and why certain things were built the way they were:

- **The assistant is pre-loaded with Lenny's Podcast, not a general file-upload tool.** A user should never need to upload a transcript — the corpus is ingested once, ahead of time. This was a deliberate choice: it allows retrieval to be tuned specifically for this dataset (guest names, speaker turns, podcast intros as noise) instead of building a generic ingestion pipeline that has to handle arbitrary transcript quality.
- **Local model support (Ollama) is treated as a hard requirement, not an optional extra**, per the brief — the app needs to run and demo without requiring anyone's personal API key.
- **A cloud provider option exists mainly to prove the system is configurable**, not because it's expected to be the primary way the app is evaluated.
- **Given the short timeline, some infrastructure ideas were reconsidered along the way.** An early draft plan proposed a more complex hybrid search setup (BM25 plus dense embeddings) up front; this was simplified to a tuned lexical/topical retrieval approach so time could go toward making grounding genuinely reliable rather than technically elaborate. Database resilience (automatic fallback to local SQLite when PostgreSQL isn't configured) was kept, since it directly serves the "zero-friction evaluation" goal and required little extra effort once the async database layer was in place.

### On reusing prior work
There was an earlier personal project — a summarization model trained on 300k+ CNN/DailyMail news articles. It was considered and explicitly ruled out as the core engine here: it's a different task (fixed-length summarization vs. multi-turn grounded retrieval) on a completely different and unrelated dataset. It has no ability to cite a specific guest or episode. It's mentioned here only for transparency, not because it contributed to this system.

---

## 5. Functional Requirements

### 5.1 Grounded conversational assistant
- Retrieves relevant transcript passages for a user's question and answers strictly from that retrieved content.
- Every answer that makes a claim is attached to a real source: guest name, episode title, timestamp, and a direct link to that point in the YouTube video.
- If nothing relevant is found in the transcripts, the assistant says so plainly rather than answering anyway.
- Follow-up questions within the same conversation are understood in context.

### 5.2 Ship 30 for 30 essay generation
- Converts a topic into a long-form essay (target: roughly 1,100–1,300 words) following a defined structure: a hook, a credibility statement, four themed sections, and one closing takeaway.
- Every claim in the essay should trace back to something actually said in the retrieved transcript material — not filled in from general knowledge.

### 5.3 Artifact generation
- Can produce a small interactive document (e.g. a checklist) as a self-contained piece of HTML, shown in a separate panel from the chat.
- Because this HTML is AI-generated, it's rendered inside a sandboxed iframe that cannot access the rest of the page, cookies, or local storage — a defensive measure against any unexpected or malicious content.

### 5.4 Configurable model provider
- The active LLM — Groq (cloud, recommended for evaluators since it's free and requires no local setup), Ollama (local, required for the offline demo), Anthropic Claude, or OpenAI — is set via a single `.env` value, with no code changes needed.
- Providers can also be switched at runtime through a dedicated endpoint (`/api/models/switch`), without restarting the server.
- The system reports honestly which provider is active and whether it's currently reachable, via `/api/health`.

### 5.5 Persistence
- Conversations, sessions, and generated artifacts are saved so that a user can leave and return to a conversation without losing it.
- Sessions are isolated from one another.

### 5.6 Frontend / User Interface
Built in React. The interface includes:
- A visually distinct landing/chat surface using a glassmorphism-style canvas with a 3D animated hero element.
- A chat window that renders streamed responses progressively, rather than waiting for the full answer before showing anything, with autoscroll.
- Inline display of source citations (guest, episode, timestamp) alongside grounded answers.
- A side-by-side artifact viewer panel for generated documents/checklists, separate from the main chat.
- A live, pill-shaped indicator showing the active model/provider, with the ability to switch it directly from the UI.
- A session sidebar showing past conversations, so a user can return to an earlier chat.

---

## 6. System Architecture (Summary)

```
Browser (React frontend — chat UI + artifact viewer + session sidebar)
        │
        ▼
FastAPI backend
   ├── Agent orchestration (decides: plain answer / essay / artifact)
   ├── Retrieval layer (searches indexed transcript chunks)
   ├── LLM provider layer (Groq / Ollama / Claude / OpenAI, runtime-switchable)
   └── Persistence layer (PostgreSQL, with automatic SQLite fallback for local evaluation)
        │
        ▼
Ollama (runs natively on the host machine, outside Docker)
```

Long-running generations (chat responses and essays) are streamed back to the client token-by-token using Server-Sent Events, rather than making the user wait for the entire response before seeing anything.

A full breakdown of endpoints, database schema, and security decisions lives in `architecture.md`.

---

## 7. What Actually Happened While Building This

A take-home like this isn't just "did the code run once" — it's whether the thing holds up when you actually poke at it. Here's what came up during backend development and testing, because the process itself is part of what's being evaluated:

**Silent failures on long generations.** Early on, the Ship 30 essay endpoint was quietly falling back to a lightweight offline stub instead of using the real local model, with no visible error. The cause turned out to be two things stacking together: the timeout on requests to the local model was shorter than a full essay actually takes to generate, and the local model's default context window was too small for the amount of transcript text being passed in. Once found, both were fixed, and the failure handling was changed to log clearly instead of failing silently.

**A shortcut that was rejected.** At one point, rather than fixing the actual generation, the more tempting option was to make that offline stub "smarter" — pull out a real guest name and pad the text to hit the word count. That was reverted on purpose. It would have produced output that looked right without actually being generated or grounded — which defeats the entire point of what's being evaluated here.

**Weak retrieval quality.** A question like "Brian Chesky on founder mode leadership" was initially returning podcast intro small-talk instead of anything substantive, because very short transcript snippets were scoring artificially well just for repeating a guest's name. This was fixed by requiring longer, more substantial chunks, filtering out intros and sponsor reads, and weighting topical relevance above simple name repetition.

**Essay length falling short.** The model would default to a much shorter essay than required unless explicitly told how much to write per section. Fixed by giving it an explicit word budget for each part of the structure.

**Latency as a real usability risk, not just a caveat.** A local model can take well over a minute to write a full essay. Rather than just noting this as an accepted limitation, streaming was built so the user sees the response forming in real time instead of watching a blank screen.

**Citation placeholders.** On some open-ended questions, the model would occasionally output a generic placeholder like "(Episode X, Timestamp Y)" instead of a real citation. This was fixed with an explicit instruction to only cite exact metadata that was actually retrieved, or to skip the citation format entirely rather than fabricate one.

Each of these was caught through direct manual testing, not assumed to be fine.

---

## 8. Risks & Trade-offs

| Risk | Mitigation / Current State |
|---|---|
| Local model responses are slow (60s+ for a full essay) | Addressed with streaming so the experience doesn't feel frozen; Groq is offered as a fast, free cloud alternative for evaluators who don't want to wait on local inference, while Ollama remains the required path for the offline demo |
| Retrieval could still surface tangential quotes on some queries | Chunking and scoring were tuned to reduce this, but it isn't perfect on every query |
| Multiple cloud providers add surface area to maintain | Groq and Anthropic were both verified with real API keys; OpenAI is wired to the same interface but tested less extensively |
| A generic offline fallback exists for reliability | Used only to keep automated tests stable without external dependencies — never used for real user-facing answers |

---

## 9. Testing & Verification

**Automated:** A pytest suite covers health checks, session persistence, retrieval behavior (including out-of-domain refusal), provider/model listing, and Ship 30 essay structure.

**Manual (API level):** Verified directly via Thunder Client and Postman, including the health endpoint, session creation, grounded chat responses, out-of-domain refusal, the streaming Ship 30 endpoint, and behavior when Ollama is intentionally taken offline. Screenshots of key verification runs are included in the repository.

**Manual (UI level):** Documented separately in the manual test checklist (`tests.md`).

---

## 10. Deployment

- **Local (required by the assignment):** Docker Compose brings up the backend, frontend, and database with a single command. Ollama runs natively on the host machine and is reached from inside the container via `host.docker.internal`.
- **Hosted demo:** A live version is also deployed, using Groq's hosted inference as the cloud LLM option and PostgreSQL for persistence.
- **Repository:** https://github.com/akhil05-g/The-Lenny-Growth-Assistant
- **Live demo:** https://the-lenny-growth-assistant-jq4i.onrender.com

---

## 11. Deliverables Status

| Deliverable | Status |
|---|---|
| GitHub repository | Complete |
| README.md | Complete |
| PRD (this document) | Complete |
| design.md | Complete |
| architecture.md | Complete |
| Agent development transcripts | Complete |
| Automated tests + manual test plan | Complete |
| Demo video | Pending |
