# AI Content Agent

Autonomous multi-agent system that turns a niche into a full video script (and, in later phases, voice + visuals + a finished video uploaded to YouTube/Instagram). Hinglish-first, multi-domain, free-first stack, no GPU required.

> **Status:** Phase 2 (media pipeline) complete — `niche → topic ideas → script → voice + visuals → HyperFrames render → playable MP4`, all human-gated. Upload lands in Phase 3.

## Architecture (target)

```
LangGraph orchestrator
  idea_generator → [HITL topic] → script_writer → [HITL script]
    → voice (Kokoro) + visuals (fal two-tier) → HyperFrames render → upload
```

Phases 1–2 ship the brain and the body: orchestrator, state, agents, a pluggable human-approval layer, two-tier AI visuals, Kokoro voiceover, and an HTML→MP4 render. Upload lands in Phase 3.

Full design: `docs/superpowers/specs/2026-06-28-ai-content-agent-design.md`
Build plans: `docs/superpowers/plans/`

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # then add your API keys (see below)
```

### Requirements

- **Phase 1 (text):** a free [Groq](https://console.groq.com) API key (`GROQ_API_KEY`).
- **Phase 2 (media):** image generation, plus **Node.js ≥ 22** and **FFmpeg** on your PATH — the render step runs through the HyperFrames CLI (`npx hyperframes`). Voice (Kokoro) runs locally through that same CLI, no key needed.
  - **Free (default):** `IMAGE_PROVIDER=pollinations` — [pollinations.ai](https://pollinations.ai), no key, zero cost. With this, the *entire* pipeline runs on just the free Groq key.
  - **Paid (better character consistency):** `IMAGE_PROVIDER=fal` + a [fal.ai](https://fal.ai) key (`FAL_KEY`).
- **Optional:** `CHARACTER_REF_IMAGE_URL` — a reference image for the recurring character. If unset, hero scenes fall back to plain B-roll generation, so the pipeline still runs end-to-end.

## Run

```bash
python -m orchestrator.runner
```

Generates topic ideas for the default niche, writes a script, generates voice + visuals, renders a video, and asks you to approve at each gate (topic, script, render) in the console. Produces `outputs/<job_id>/render/final.mp4`.

## Dashboard

A local web dashboard to see every job the agent has run — status, niche, topic, full script, and a playable preview of the rendered video.

```bash
uvicorn dashboard.app:create_app --factory --port 8000
```

Then open `http://localhost:8000`. It reads jobs from `outputs/` and auto-refreshes, so a finished run appears on its own. It's read-only monitoring for now — browser-based approve/reject arrives with the async human-in-the-loop refactor (Phase 5). Until you've run a job (needs a `GROQ_API_KEY`), it shows an empty state with the run command.

## Test

```bash
pytest -q
```

Unit tests never hit the network or subprocess — all external calls (Groq, fal.ai, the HyperFrames CLI) go through mockable wrappers.

## Tech

LangGraph · langchain-groq · fal-client · HyperFrames (Kokoro TTS + HTML→video) · pydantic · pytest. Python 3.12.

## Roadmap

- **Phase 1** ✅ Text spine (orchestrator, state, idea + script agents, HITL CLI)
- **Phase 2** ✅ Voice (Kokoro) + visuals (fal FLUX.2 hero + FLUX.1 schnell B-roll) + HyperFrames render + AI-content disclosure
- **Phase 3** YouTube/Instagram upload + thumbnails + analytics
- **Phase 4** Scheduler, retry/recovery, first real videos
- **Phase 5** VoxCPM2 / Sarvam cloud voice, Postiz multi-platform, WhatsApp notifier (green-api), analytics feedback loop
