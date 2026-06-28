# AI Content Agent — Design Spec

**Version:** 1.0 (research-locked)
**Author:** Manan + Claude
**Date:** 2026-06-28
**Status:** Approved design → ready for implementation plan
**Supersedes the open decisions in:** `AI_Content_Creation_PRD.md` §14

---

## 1. Vision

A multi-agent system that autonomously generates, produces, and publishes short-form
(and later long-form) video to YouTube and Instagram. Hinglish-primary, multi-domain
(horror, tech, finance, motivation, mythology, comedy, trending). Free-first stack,
flexible human-in-the-loop, built for personal passive income first and freelance/SaaS later.

Full product context lives in `AI_Content_Creation_PRD.md`. This spec records the
**decisions and architecture** settled during the research phase and overrides the PRD
where they differ.

---

## 2. Locked Decisions (research outcomes)

| # | Decision | Outcome | Why |
|---|---|---|---|
| 1 | **Hardware / GPU** | No usable GPU (Intel Iris Xe, i7-1255U, 15.7 GB RAM). | Kills local SD/ComfyUI/LoRA. Forces cloud image gen. CPU is fine for orchestration, Kokoro TTS, Whisper-base, HTML render. |
| 2 | **Build strategy** | **Hybrid** — build the brain, steal proven components, adopt cloud services for GPU-bound work. | Max control over differentiators; absorb months of work elsewhere. |
| 3 | **Image / character** | **Cloud, two-tier.** fal.ai Instant Character (hero scenes, ref image, no LoRA) + FLUX schnell (B-roll). | No GPU → cloud only. Two-tier keeps cost < ₹15/video while preserving mascot identity. |
| 4 | **Render + caption core** | **HyperFrames** (HTML→video, installed locally as skills). | Replaces brittle FFmpeg/MoviePy Ken Burns + ASS captions. CapCut-grade animated captions, kinetic motion, Kokoro TTS + BGM + Whisper built in, AWS Lambda batch render. |
| 5 | **Voice (TTS)** | Phase 1 **Kokoro** (82M, CPU, free, best open Hindi). Phase 2 **VoxCPM2** (Apache-2.0, 30 langs, voice cloning) on cloud GPU for premium cloned character voice. Sarvam optional paid. | Kokoro runs locally now. VoxCPM2 is 2B — needs cloud GPU. |
| 6 | **Upload / scheduling** | Phase 1 **custom YouTube Data API** + APScheduler (SQLite jobstore, survives restart). Instagram Graph API with manual fallback. Postiz deferred to Phase 2 (multi-account scaling). | Laptop is not a 24/7 server. Official APIs only — never anti-detect automation for posting (ToS/ban risk). |
| 7 | **Orchestration** | **LangGraph** StateGraph + SQLite checkpointer. PRD `ContentState` kept. | Resumable jobs, parallel nodes, HITL pause/resume. |
| 8 | **HITL** | **WhatsApp** (Meta Cloud API) via a **pluggable notifier interface** with a **CLI/console fallback** that works day one. Per-checkpoint toggle. | User prefers WhatsApp. WhatsApp Cloud API has setup friction (Meta Business + number + template approval), so the notifier is abstracted — CLI works immediately, WhatsApp adapter slots in when keys ready. Core pipeline never blocks on it. |
| 9 | **Niche** | **Multi-domain, niche-agnostic build.** Style + script-prompt config per niche. Character placement is per-niche config. | Max reach; one render → YT Shorts + IG Reels. |

---

## 3. Architecture

### Pipeline (revised render half)

```
ORCHESTRATOR (LangGraph StateGraph, SQLite checkpoint)
  └─ idea_generator      (pytrends + praw + newsapi + Groq scoring)
       → [HITL topic?]
  └─ script_writer       (Groq Llama 3.3; emits scene HTML spec + character_visible per scene)
       → [HITL script?]
  └─ PARALLEL:
       ├─ voiceover       (Kokoro TTS → per-segment audio)  [Phase 2: VoxCPM2 cloud]
       └─ visuals (two-tier):
            character_visible=true  → fal Instant Character (ref image)
            character_visible=false → fal FLUX schnell (B-roll)
  └─ render              (HyperFrames: scenes HTML + images + audio → motion + captions + BGM → MP4)
       → [HITL final?]
  └─ uploader            (YouTube Data API; IG Graph API w/ manual fallback)
  └─ analytics_tracker   (YouTube Analytics API → feedback to idea_generator)
```

### Component sourcing

| Layer | Source | Item |
|---|---|---|
| Orchestrator + state + HITL | **BUILD** | LangGraph, pluggable notifier (CLI now → WhatsApp adapter), niche/style config |
| Script + idea prompts | **BUILD** | Hinglish, niche-aware, scene-HTML-emitting |
| Two-tier character system | **BUILD on service** | fal.ai Instant Character + FLUX schnell |
| TTS | **ADOPT** | Kokoro (P1) → VoxCPM2 cloud (P2) |
| Render + captions + BGM + motion | **ADOPT** | HyperFrames |
| Trending research | **STEAL/USE** | pytrends, praw, newsapi |
| Transcription (if needed outside HyperFrames) | **STEAL/USE** | faster-whisper / whisperX |
| Upload | **BUILD (P1) → ADOPT Postiz (P2)** | YouTube Data API, IG Graph API |
| Pipeline pattern reference | **READ** | MoneyPrinterTurbo, ShortGPT |

### Parked / rejected
- **agentic-inbox** — email HITL not needed (WhatsApp + CLI is HITL). Revisit Phase 3 for sponsor-email triage.
- **camoufox** — anti-detect browser. **Never on the upload path** (ToS/ban risk). Optional read-only trend scraping only.
- Books / LMS / podcast / newsletter tools (Ghost, Frappe, Podcastfy, etc.) — separate sub-projects, out of this spec's scope.

---

## 4. Cost Model (per short, target < ₹15)

| Item | Tool | Approx cost |
|---|---|---|
| Script + ideas | Groq (free tier) | ₹0 |
| Voice | Kokoro (local) | ₹0 |
| Hero character images (1–2) | fal Instant Character @ $0.10/MP | ₹8–17 |
| B-roll images (3–4) | FLUX schnell @ ~$0.003/MP | ₹1–2 |
| Render | HyperFrames local (CPU) | ₹0 |
| Captions/BGM | HyperFrames built-in | ₹0 |
| Upload | YouTube API (free quota) | ₹0 |
| **Total** | | **≈ ₹10–20** |

**Cost-control knobs:** cap hero scenes to 1–2/video; benchmark cheaper character options
(Nano Banana 2, FLUX.2 w/ reference) to push hero cost down — open research task.

---

## 5. Phase Plan (revised)

- **Phase 0 — Setup:** accounts (YT/IG + brand name), API keys (Groq, fal, WhatsApp/Meta, NewsAPI, Reddit), character concept, HyperFrames smoke test.
- **Phase 1 — Text spine:** LangGraph skeleton + state + SQLite, idea_generator, script_writer (scene-HTML output), pluggable notifier (CLI fallback) HITL. Verify: topic → script → approval flow.
- **Phase 2 — Media:** Kokoro voice, fal two-tier visuals, HyperFrames render. Verify: full pipeline → playable MP4 (no upload).
- **Phase 3 — Publish:** YouTube upload, thumbnail, analytics pull. Verify: end-to-end unlisted upload.
- **Phase 4 — Automate:** APScheduler queue, retry/recovery, logging, first 10 real videos.
- **Phase 5 — Optimize:** VoxCPM2 cloud voice, character LoRA-free tuning, Postiz multi-platform, analytics feedback loop, cheaper-character migration.

---

## 6. Open Research Tasks

**Mine (next sessions):**
1. Full scan of `anil-matcha/open-generative-ai` for missed tools (fetch was rate-limited).
2. Benchmark fal character options (Instant Character vs Nano Banana 2 vs FLUX.2 ref) for cost/consistency.
3. Read `cloudflare/agents` HITL pause/resume patterns for orchestrator robustness.

**Manan's:**
1. Create YouTube + Instagram accounts; decide brand/channel name.
2. Obtain API keys: Groq, fal.ai, WhatsApp Cloud API (Meta Business + number; CLI works without it), NewsAPI, Reddit app.
3. Draft character concept (gender, anime style, hair/eyes/outfit, palette) — even a Canva sketch.
4. Run HyperFrames `faceless-explainer` on a sample topic to judge output quality before locking render core.
5. Study 2–3 top Hinglish faceless channels (hook, pace, caption style) to tune script prompts.

---

## 7. Success Criteria (system)

| Metric | Target |
|---|---|
| Idea → uploaded video | < 30 min (full auto) |
| Cost per video | < ₹15 |
| Human time per video | < 5 min (review only) |
| Pipeline success rate | > 90% |
| Capacity | 7–14 videos/week |

---

*Next step: invoke writing-plans skill to produce the implementation plan for Phase 0 + Phase 1.*
