# AI Content Agent

Autonomous multi-agent system that turns a niche into a full video script (and, in later phases, voice + visuals + a finished video uploaded to YouTube/Instagram). Hinglish-first, multi-domain, free-first stack, no GPU required.

> **Status:** Phases 1–4 complete — from a topic (or a whole multi-part story) to rendered, captioned, uploadable vertical videos. All human-gated.

## Architecture (target)

```
single video:  idea_generator → [HITL topic] → script_writer → [HITL script]
                 → visuals → voice/music → composition → render → [HITL] → upload

series:        series_writer (one story → N parts, locked style + characters)
                 → per part: the pipeline above, chained by cliffhangers
```

Built on LangGraph. Every external call (Groq, image gen, HyperFrames CLI, YouTube) sits behind a
mockable wrapper, so the whole test suite runs with no network and no subprocess.

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
- **Phase 3 (publish) — optional:** to auto-upload to YouTube (unlisted), set up OAuth (see **Publishing** below). If unconfigured, the pipeline still finishes at `media_complete` — the video just isn't uploaded.

## Run

```bash
python -m orchestrator.runner
```

Generates topic ideas for the default niche, writes a script, generates voice + visuals, renders a video, and (if YouTube is configured) uploads it — asking you to approve at each gate (topic, script, render, publish) in the console. Produces `outputs/<job_id>/render/final.mp4`.

## Series mode (Phase 4)

Turn one story into a multi-part serial — the format the reference accounts grow on (later parts
outperform Part 1 because the audience gets invested):

```bash
python -m orchestrator.series_runner "एक डिलीवरी वाला रात को सुनसान फ्लैट पर पहुँचता है" 3
```

Every part shares one locked art style and the same characters, ends on a cliffhanger written
into the dialogue, and carries a "Part N" badge. Output lands in `outputs/<series_id>/part_<n>/`.

**Format profiles** (`modules/formats.py`, durations measured from real reels):

| Profile | Length | Audio | Use for |
|---|---|---|---|
| `joke_10s` | ~11s | 2 voices | one setup, one punchline |
| `montage_35s` | ~34s | music | nostalgia, emotional |
| `drama_50s` | ~50s | 3-5 voices | characters arguing, explainer |
| `serial_75s` | ~75s | music | thriller / crime / story serial |

Music-mode formats render **silent by default** (`BGM_MODE=silent`) so you can add trending audio
in the Instagram / YouTube app — trending sounds can't be attached through the API. Set
`BGM_MODE=baked` to mix in a track from `assets/music/` instead.

Languages: `hindi`, `hinglish`, `haryanvi`, `punjabi` — written in dialect, not transliterated.

## Publishing to YouTube (Phase 3)

Uploads the rendered video as **unlisted** (review it on YouTube, then make it public yourself). One-time setup:

1. In [Google Cloud Console](https://console.cloud.google.com), create a project and enable **YouTube Data API v3**.
2. Create an **OAuth 2.0 Client ID** (type: *Desktop app*). Put the id/secret in `.env` as `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET`.
3. Run the one-time consent once — it opens a browser and writes your refresh token to `.env`:
   ```bash
   python -m scripts.youtube_auth
   ```
4. Apply for a **quota audit early** — the default quota allows only ~6 uploads/day and Google's review takes weeks.

Notes: Shorts are auto-tagged with `#Shorts` in the description; custom thumbnails are intentionally skipped (YouTube rejects them for Shorts); Instagram publishing is a later phase (needs a Business account + Meta review).

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
- **Phase 3** ✅ YouTube unlisted upload (HITL-gated, #Shorts, OAuth) — Instagram + analytics deferred
- **Phase 4** ✅ Series & format engine — multi-part serials, 4 format profiles, multi-voice dialogue, music mode, Hindi/Haryanvi/Punjabi, engagement captions
- **Phase 5** Scheduler, retry/recovery, first real videos
- **Phase 6** VoxCPM2 / Sarvam cloud voice, Postiz multi-platform, WhatsApp notifier (green-api), analytics feedback loop
