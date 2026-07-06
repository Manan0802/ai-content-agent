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
| 3 | **Image / character** | **Cloud, two-tier.** fal.ai FLUX.2 [dev] (hero scenes, multi-reference conditioning, no LoRA) + FLUX.1 schnell (B-roll). *(Updated 2026-07-06 — see §6; originally Instant Character, swapped for ~8x cheaper cost at comparable no-fine-tune consistency.)* | No GPU → cloud only. Two-tier keeps cost < ₹15/video while preserving mascot identity. |
| 10 | **AI-content disclosure** | **Persistent on-screen label + one spoken disclosure line**, baked into every render starting Phase 2 — not bolted on at upload time. | India's 2026 IT Rules amendment mandates continuous visible AI-content labeling + embedded metadata + audible disclosure for AI-generated video; penalties up to ₹50 lakh + criminal liability (Section 66F-A). Found during 2026-07-06 research pass — see §6. |
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
| Hero character images (1–2) | fal FLUX.2 [dev] @ $0.012/MP | ₹1–3 |
| B-roll images (3–4) | FLUX.1 schnell @ ~$0.003/MP | ₹1–2 |
| Render | HyperFrames local (CPU) | ₹0 |
| Captions/BGM | HyperFrames built-in | ₹0 |
| Upload | YouTube API (free quota) | ₹0 |
| **Total** | | **≈ ₹3–6** *(updated 2026-07-06 — was ₹10–20 with Instant Character)* |

**Cost-control knobs:** cap hero scenes to 1–2/video. Benchmarked 2026-07-06 (Nano Banana 2 ~₹4–6/image, only marginally cheaper than Instant Character and a second vendor integration — skipped; FLUX.2 [dev] won on cost + no new vendor).

---

## 5. Phase Plan (revised)

- **Phase 0 — Setup:** accounts (YT/IG + brand name), API keys (Groq, fal, WhatsApp/Meta, NewsAPI, Reddit), character concept, HyperFrames smoke test.
- **Phase 1 — Text spine:** LangGraph skeleton + state + SQLite, idea_generator, script_writer (scene-HTML output), pluggable notifier (CLI fallback) HITL. Verify: topic → script → approval flow.
- **Phase 2 — Media:** Kokoro voice, fal two-tier visuals, HyperFrames render. Verify: full pipeline → playable MP4 (no upload).
- **Phase 3 — Publish:** YouTube upload, thumbnail, analytics pull. Verify: end-to-end unlisted upload.
- **Phase 4 — Automate:** APScheduler queue, retry/recovery, logging, first 10 real videos.
- **Phase 5 — Optimize:** VoxCPM2 cloud voice, character LoRA-free tuning, Postiz multi-platform, analytics feedback loop, cheaper-character migration.

---

## 6. Research Log

### 2026-07-06 deep research pass — done, findings applied above

Seven parallel research fronts covering every pipeline stage, run before starting Phase 2 build. Resolves all three "Mine" tasks from the original open-research list plus a wider sweep.

| # | Question | Verdict | Applied? |
|---|---|---|---|
| 1 | Cheaper/better hero-image options (was: benchmark Instant Character vs Nano Banana 2 vs FLUX.2) | **FLUX.2 [dev] wins** — same fal.ai account, ~8x cheaper ($0.012/MP vs $0.10/MP), comparable no-fine-tune multi-reference consistency. Nano Banana 2 only marginally cheaper and a new vendor — skipped. Local MLX/ComfyUI on the Mac — real setup effort, ties output to the secondary machine — skipped. | ✅ §2 row 3, §4 cost table |
| 2 | Best free-first Hinglish TTS (was: confirm Kokoro is still right) | Kokoro stays as Phase 2 default (free, zero setup, already wired via HyperFrames CLI). **Sarvam AI (Bulbul V3) flagged as a strong near-free upgrade** — explicit Hinglish code-switching support, ₹1,000 free credits then ~₹1–3/video — but needs a custom wrapper (not in HyperFrames' provider chain). Not pulled into Phase 2; tracked as a fast-follow. VoxCPM2/Coqui correctly stay Phase 5-only (real GPU deployment). HeyGen's Starfish engine is CJK-optimized, not a Hindi upgrade. | 🕓 Fast-follow, not built yet |
| 3 | Is HyperFrames still the right render choice vs Remotion-direct / MoneyPrinterTurbo / JSON2Video / Lambda | **No change — HyperFrames confirmed.** Raw Remotion would mean rebuilding its lint/validate/inspect + media pipeline by hand. JSON2Video/Creatomate would replace a free render step with a $20–50/mo subscription. Local render (not Lambda) is correct at this scale (one machine, not always-on, <60s clips). | ✅ No change needed |
| 4 | `cloudflare/agents` HITL pause/resume patterns for orchestrator robustness | Confirmed pattern: LangGraph's `interrupt()` + `Command(resume=...)` + a durable checkpointer (`SqliteSaver`) lets a *different process* resume a paused job by `thread_id` — exactly what's needed once WhatsApp HITL lands (a webhook handler ≠ the process that started the job). **Deliberately not wired in yet** — no payoff while the notifier is still CLI-only and blocking. | 🕓 Wire in when the WhatsApp notifier is built (Phase 5, or sooner if jobs need to survive a reboot) |
| 5 | Full scan of `anil-matcha/open-generative-ai` for missed tools | Repo is built around MuAPI, a paid model aggregator — cuts against free-first. One genuine find: **sd.cpp**, a local Stable Diffusion runner using Metal GPU acceleration — free B-roll option, but only usable on the Mac (secondary machine); not a Windows-path replacement. Nothing else beats the locked stack. | 🕓 Optional Mac-only fallback, not built |
| 6 | Upload/scheduling landscape check for Phase 3/4 | YouTube default quota ≈ 6 uploads/day (apply for an audit early — weeks of lead time); Shorts need `#Shorts` in title/description, reject custom thumbnails. Instagram needs a Business account + new permission names (`instagram_business_*`, old ones deprecated Jan 2025) + 2–4 week Meta review — manual fallback still warranted. Postiz's native YouTube support unconfirmed — re-verify at Phase 5 (alternatives: Bulkit.dev, Mixpost). **India's 2026 IT Rules require AI-content disclosure** — see §2 row 10, this is the one finding that changes Phase 2 itself. | ✅ §2 row 10 (disclosure); 🕓 rest is Phase 3/4 prep |
| 7 | Famous open-source reference projects beyond MoneyPrinterTurbo/ShortGPT | ShortGPT's modular step-chain confirms this project's own LangGraph node design is the right shape — nothing new to take architecturally. **VideoGraphAI's pattern of grounding script generation in real search results (not just topic discovery) is a concrete, actionable idea** for accuracy-sensitive niches (finance/tech/mythology) — worth adding as a fact-grounding step before `script_writer` later. SadTalker (open, local, free lip-sync) noted for if a talking-head format is ever wanted. Dead ends: AI-Youtube-Shorts-Generator (repurposes existing long-form video, wrong shape), OpenMontage (redundant with the already-installed HyperFrames skill family). | 🕓 Fact-grounding idea tracked, not built |

**Follow-ups tracked for later (not blocking Phase 2):**
1. Sarvam AI TTS wrapper as an optional Kokoro upgrade for genuine Hinglish voice quality.
2. `sd.cpp` local Metal image-gen as a free B-roll fallback specifically when working from the Mac.
3. LangGraph `SqliteSaver` + `interrupt()`/`Command(resume=...)` — replace the in-memory checkpointer and blocking `Notifier.ask_approval()` once the WhatsApp adapter is built.
4. Fact-grounding step (real search results fed into `script_writer`'s prompt) for accuracy-sensitive niches — VideoGraphAI-inspired.
5. Re-verify Postiz's YouTube coverage right before Phase 5; Bulkit.dev/Mixpost as backups.
6. SadTalker (open-source lip-sync) if a talking-head format is ever wanted alongside the current B-roll/hero-cutaway style.
7. **Script prompt refinements from the 2026-07-06 Hinglish channel study** (real analogs: Khooni Monday, Kahanikaar Sudhanshu Rai, Paisa Samjho): explicit hook-type constraint (question/bold claim/mid-action drop, never scene-setting), fixed 6–10 segments of 5–8s each, niche-conditional Hinglish register, caption-ready short clauses in `voiceover_text` (it's burned on screen verbatim), and a cliffhanger-style `outro_cta`. Apply to `prompts/script_prompts.py` when next touching Phase 1's script writer — not done yet.
8. **Web dashboard for the AI Content Agent itself** (requested 2026-07-06, not scoped yet) — a real UI showing job status, script/video previews, and approve/reject controls in the browser, as an alternative/addition to the CLI `Notifier`. Deliberately kept out of Phase 2 to keep that build focused; needs its own small plan doc when picked up (likely after Phase 2 ships a working render, so there's an actual pipeline to visualize).
9. **Monetization strategy** (2026-07-06 research) — Shorts-only ad revenue is weak (~10% of long-form RPM in India, months before YouTube Tier-2 monetization even activates). Long-form video (already implied by the spec's "later long-form" framing) is the real revenue path; Shorts should be treated as a discovery funnel, not the earner. Revisit when scoping Phase 4/5 — don't just automate more Shorts.

**Manan's (unchanged, still open):**
1. Create YouTube + Instagram accounts; decide brand/channel name.
2. Obtain API keys: Groq, fal.ai, WhatsApp Cloud API (Meta Business + number; CLI works without it), NewsAPI, Reddit app.
3. Draft character concept (gender, anime style, hair/eyes/outfit, palette) — even a Canva sketch.
4. Run HyperFrames `faceless-explainer` on a sample topic to judge output quality before locking render core.
5. Study 2–3 top Hinglish faceless channels (hook, pace, caption style) to tune script prompts.
6. **New (2026-07-06): apply for the YouTube Data API quota audit early** — default quota only allows ~6 uploads/day, and Google's review takes weeks. Start this well before Phase 3 needs it, even though it's a Phase 3 concern.

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
