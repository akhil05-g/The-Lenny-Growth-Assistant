# Design Document (design.md)
## Design System & UI/UX Architecture: The Lenny Growth Assistant

---

## 1. Design Vision & Guiding Philosophy

The Lenny Growth Assistant interface is inspired by high-end modern AI tools, blending **soft glassmorphism, ethereal pastel mesh gradients, and crisp typography** to create an executive-grade, distraction-free environment for founders and product leaders.

Rather than looking like a generic ChatGPT clone, the application adopts a tactile, human-centered aesthetic featuring:
- **Soft Dreamy Canvas**: Pastel gradient lighting (`#fed7e2`, `#e0e7ff`, `#fef08a`) that feels calm and creative rather than cold and clinical.
- **3D Iridescent Luminous Hero**: An interactive, multi-dimensional glass sphere with magenta and cyan light refractions and a soft mirror floor reflection, establishing immediate visual delight upon entry.
- **Floating Floating-Border Input Bar**: A floating pill input container encircled by a delicate rainbow-pastel gradient rim (`from-amber-200 via-pink-300 to-cyan-200`) with quick-action prompt chips above it.
- **Claude-Style Split-Screen Artifacts**: When documents, roadmaps, or interactive HTML checklists are generated, they slide gracefully into an isolated side panel rather than cluttering the conversational stream.

---

## 2. Information Architecture & Spatial Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FULL-SCREEN CANVAS                                   │
│  ┌──────────────┐  ┌──────────────────────────────────────────────┐  ┌────────────────┐  │
│  │ SLIM DOCK    │  │ TOP BAR: Logo + Active Model Pill (+ Status) │  │ ARTIFACT       │  │
│  │ - Logo       │  ├──────────────────────────────────────────────┤  │ VIEWER         │  │
│  │ - Assistant  │  │ CONVERSATION / HERO CANVAS                   │  │ - Live Preview │  │
│  │ - History    │  │                                              │  │ - Source Code  │  │
│  │ - Settings   │  │  [Empty State: 3D Iridescent Glass Orb]      │  │ - Copy / Export│  │
│  │ - New Chat   │  │  [Active State: Message Cards + Citations]   │  │ - Sandboxed    │  │
│  │              │  ├──────────────────────────────────────────────┤  │   <iframe>     │  │
│  │              │  │ FLOATING INPUT BAR                           │  │                │  │
│  │              │  │ - Quick Prompt Pills (Chesky, Elena, Ship30) │  │                │  │
│  │              │  │ - Textarea + Attach, DeepThink, Voice, Send  │  │                │  │
│  └──────────────┘  └──────────────────────────────────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 The 3-Zone Architecture
1. **The Left Navigation Dock**:
   - Slim vertical floating rail (`w-[68px]`, frosted white `rgba(255,255,255,0.9)`, full rounded borders).
   - Keeps the viewport clean while offering immediate access to the past session history drawer, settings, and new chat creation.
2. **The Central Conversational Stream**:
   - Dynamic stage: when empty, it displays the 3D iridescent orb and the gradient headline (*"AI Powers Grounded Growth And Voice Access"*).
   - When active, smoothly transitions to conversational turns with grounded podcast citation chips.
3. **The Slide-Out Artifact Workspace**:
   - A dedicated right-hand split-view (`w-[480px]`) that slides in smoothly when an artifact is generated.
   - Provides an isolated sandboxed preview and raw code inspector.

---

## 3. Color Palette & Typography Tokens

### 3.1 Color Palette
| Token | Hex Value | Role & Usage |
| :--- | :--- | :--- |
| **Canvas Mesh Primary** | `#fdf2f8` to `#f0fdf4` | Ambient pastel gradient background |
| **Glass Surface** | `rgba(255, 255, 255, 0.72)` | Blur cards, sidebars, and input containers |
| **Primary Accent** | `#f43f5e` to `#ec4899` | Rose-to-pink gradient for Send button, active icons, highlights |
| **Cyan Refraction** | `#06b6d4` | Secondary luminous reflection on the 3D orb |
| **Text Charcoal** | `#0f172a` (Slate-900) | Primary headlines, bold anchors, user bubbles |
| **Text Secondary** | `#475569` (Slate-600) | Body text, podcast quotes, explanation copy |
| **Text Tertiary** | `#94a3b8` (Slate-400) | Timestamps, metadata, inactive icons |
| **Success Emerald** | `#10b981` | Real-time connection pulse, verified status badges |

### 3.2 Typography
- **Primary Typeface**: `Plus Jakarta Sans` (Google Fonts) paired with system fallbacks (`-apple-system, BlinkMacSystemFont, Segoe UI`).
- **Hierarchy**:
  - Hero Title: `text-3xl / text-4xl`, weight `800` (extrabold) with gradient span.
  - Section Headers: `text-base / text-sm`, weight `700` (bold).
  - Body Text: `text-sm`, line height `1.65`, weight `400` (regular).
  - Code & Timestamps: `font-mono`, `text-xs / text-[11px]`.

---

## 4. Key Interaction States & Micro-Interactions

### 4.1 Empty / Discovery State (The Hero Orb)
- **Visual Centerpiece**: A multi-layered CSS iridescent bubble with radial gradients simulating 3-point studio lighting and caustic refractions.
- **Hover Micro-interaction**: The orb scales smoothly (`scale-104`) with an intensified ambient pink-cyan glow.
- **Click-to-Inspire**: Clicking the orb automatically populates a high-signal founder question (*"What does Brian Chesky believe about micromanagement vs being in the details?"*) into the input field.

### 4.2 Quick Prompt Pills
- A horizontal row of rounded glass pills above the input box:
  - `🎙️ Brian Chesky on Details`
  - `📈 Elena Verna Growth Loops`
  - `✍️ Ship 30 for 30 Essay`
  - `📋 Execution Checklist`
  - `⚡ Shreyas Doshi LNO`
- Clicking any pill immediately submits the grounded query, reducing cognitive load for evaluators.

### 4.3 Streaming Turn State (Zero Latency Perception)
- When the user sends a prompt:
  1. **T + 0.2s**: Optimistic user message appears.
  2. **T + 0.8s**: Grounded citation excerpts arrive via SSE `event: sources` and render at the top of the incoming assistant card.
  3. **T + 1.2s**: Words begin progressively typing onto the screen via SSE `event: token`.
  4. **T + Done**: Artifacts and final message state are persisted to SQLite/Postgres.

### 4.4 Verified Citation Chips
- Claims in the assistant's answer include clickable badge chips:
  - **Guest Name & Episode**: e.g., `Brian Chesky ("Brian Chesky's new playbook")`
  - **Timestamp Badge**: e.g., `(00:32:17)`
  - **YouTube Link**: Direct link with embedded timestamp parameter (`&t=1937s`) that opens the exact second of audio.
  - **Expandable Quote**: Click to view the exact transcript quote used as evidence.

---

## 5. Security & Isolation Model for Artifacts

### 5.1 The Zero-Trust Rendering Principle
User-generated or LLM-generated HTML/CSS must be treated as **untrusted input**. An assistant that outputs interactive widgets could be susceptible to XSS (Cross-Site Scripting), CSS exfiltration, or DOM hijacking if injected directly into the host page.

### 5.2 The <iframe> Sandbox Isolation
The Artifact Viewer encapsulates all HTML rendering within a sandboxed `<iframe>`:
```html
<iframe
  title="Artifact Preview"
  srcDoc="<!DOCTYPE html><html>...</html>"
  sandbox="allow-scripts"
  class="w-full h-full border-0"
/>
```
- **Why `sandbox="allow-scripts"`?**: Permits interactive JavaScript (such as checking boxes on a checklist, calculating scores on a PM matrix, or toggling tabs).
- **Why `allow-same-origin` is STRICTLY EXCLUDED**: Omitting `allow-same-origin` treats the iframe content as a unique, opaque origin. The artifact **cannot**:
  - Access parent cookies or session storage.
  - Manipulate the parent DOM or read chat history.
  - Issue requests using the user's host credentials.

---

## 6. Responsive Behavior & Accessibility (a11y)

### 6.1 Responsive Adaptations
- **Desktop (> 1024px)**: Full split-view with left dock, central chat, and right-hand artifact viewer visible simultaneously.
- **Tablet (768px - 1024px)**: Artifact viewer slides out as an overlay panel with backdrop blur.
- **Mobile (< 768px)**: Dock collapses into a bottom navigation bar; quick prompt pills become horizontally scrollable; artifact viewer acts as a full-screen modal with a prominent close button.

### 6.2 Accessibility Considerations
- **Color Contrast**: All text tokens exceed WCAG AA contrast ratio (4.5:1 for body text against frosted backgrounds).
- **Keyboard Navigation**: All interactive elements (pills, input, model toggle, citations) are keyboard navigable via `Tab` and `Enter`.
- **Screen Reader Hints**: ARIA labels on icon-only buttons (`aria-label="New Conversation"`, `aria-label="Toggle Artifact View"`).
