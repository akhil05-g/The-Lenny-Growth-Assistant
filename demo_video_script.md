# 2.5-Minute Demo Video Script & Recording Guide
## The Lenny Growth Assistant (Forward Deployed Engineer Take-Home)

> **Video Target Duration**: 2 minutes 30 seconds  
> **Camera**: Enabled (picture-in-picture in top corner)  
> **Screen**: Browser on `http://localhost:3000` + Terminal showing Ollama  

---

### Segment 1: The Problem & The Mission (0:00 – 0:35)
- **Face on Camera / Screen showing App Canvas**:
> *"Hi everyone, I'm Akhil. This is The Lenny Growth Assistant, a full-stack AI knowledge application built for product managers and founders. 
> Lenny’s Podcast contains over 300 episodes with the world's top operators—from Brian Chesky to Elena Verna. But finding tactical advice normally means digging through hundreds of hours of audio, and generic AI tools like standard ChatGPT hallucinate generic advice without citing real sources.
> The goal of this project was to build a system that grounds every single answer in Lenny's verified transcripts, writes publication-grade Ship 30 for 30 essays, and renders live interactive artifacts right in the browser."*

---

### Segment 2: Live Product Demonstration with Local Ollama (0:35 – 1:30)
- **Action**: Show browser on `http://localhost:3000`. Point to the top-right model pill: `Ollama (Llama 3.2)`.
> *"Notice here in the top-right corner: our active LLM is running completely locally using Ollama and Llama 3.2. There are zero cloud dependencies for this query.*
> *Let's click this quick prompt: 'What does Brian Chesky believe about micromanagement vs being in the details?'"*
- **Action**: Click the pill or hit Send. Show the streaming response typing in real-time.
> *"Watch the response stream in via Server-Sent Events. Within 1 second, we see verified podcast citations appear. When we open a citation, we see the exact timestamp—32 minutes in—where Chesky explains why being in the details is not micromanagement. There’s even a deep link directly to that exact second on YouTube.*
> *If we ask something out-of-domain, like 'How do quantum computers solve protein folding?', the assistant politely refuses, proving our strict anti-hallucination guardrail."*

---

### Segment 3: Artifact Viewer & Ship 30 Engine (1:30 – 2:05)
- **Action**: Ask for an artifact: *"Generate an interactive HTML checklist for product execution."*
> *"Now let's look at the Artifact Viewer. Notice how instead of dumping raw code in the chat, a Claude-style split-screen opens on the right. 
> This is an interactive, sandboxed HTML widget. We can check off items, toggle to inspect the raw code, or copy it with one click. For security, this is rendered inside an iframe without same-origin privileges, so it cannot access cookies or the host page."*

---

### Segment 4: The Key Technical Trade-Off (2:05 – 2:30)
- **Face on Camera / Terminal view**:
> *"One major technical trade-off we faced was Latency vs. Offline Generation. 
> Generating a full 1,250-word Ship 30 essay on local Ollama takes 60 to 90 seconds. Initially, the client timed out at 60 seconds and silently fell back. We had to resist the temptation of padding a mock stub—which would be fake engineering. Instead, we re-architected the pipeline with a 300-second context window and real-time SSE streaming. Now, the user sees citations immediately and tokens progressively, turning a 90-second wait into an engaging, responsive experience.
> Thank you for your time, and I look forward to your feedback!"*
