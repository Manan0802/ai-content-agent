# AI Content Agent

Autonomous multi-agent system that turns a niche into a full video script (and, in later phases, voice + visuals + a finished video uploaded to YouTube/Instagram). Hinglish-first, multi-domain, free-first stack, no GPU required.

> **Status:** Phase 1 (text spine) complete — `niche → topic ideas → script → human approval`.

## Architecture (target)

```
LangGraph orchestrator
  idea_generator → [HITL topic] → script_writer → [HITL script]
    → voice (Kokoro) + visuals (fal two-tier) → HyperFrames render → upload
```

Phase 1 ships the brain: the orchestrator, state, agents, and a pluggable human-approval layer. Media/render/upload land in later phases.

Full design: `docs/superpowers/specs/2026-06-28-ai-content-agent-design.md`
Build plan: `docs/superpowers/plans/2026-06-28-phase1-text-spine.md`

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # then add your free GROQ_API_KEY
```

## Run

```bash
python -m orchestrator.runner
```

Generates topic ideas for the default niche, writes a script, and asks you to approve each step in the console. Needs a free [Groq](https://console.groq.com) API key in `.env`.

## Test

```bash
pytest -q
```

## Tech

LangGraph · langchain-groq · pydantic · pytest. Python 3.11+.

## Roadmap

- **Phase 1** ✅ Text spine (orchestrator, state, idea + script agents, HITL CLI)
- **Phase 2** Voice (Kokoro) + visuals (fal Instant Character + FLUX) + HyperFrames render + WhatsApp notifier (green-api)
- **Phase 3** YouTube/Instagram upload + thumbnails + analytics
- **Phase 4** Scheduler, retry/recovery, first real videos
- **Phase 5** VoxCPM2 cloud voice, Postiz multi-platform, analytics feedback loop
