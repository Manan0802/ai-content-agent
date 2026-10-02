# aica — The Complete Project Guide

> **Who this is for:** anyone joining the project, from a total beginner to a senior engineer.
> **Written:** 2026-10-02, from the code, the git history and the project's own notes
> (Obsidian vault, `Projects/aica/*`). Facts were re-checked while writing: the test suite was run
> (289 passed), every finished video was probed with `ffprobe`, and the machine's tools were checked.
> **The last real work session was 2026-09-05.** Nothing has changed in the project since then.
>
> **How to read it:**
> - **5 minutes:** read §0 and §1.
> - **Before you touch anything:** read §0–§6, §9 (logins), §10 (how the work is done) and §21
>   (current status).
> - **Before you write code or make a video:** read everything once. Each section stands on its own,
>   so you can come back to any of them later.

---

## Table of contents

0. [The shortest version (Hinglish)](#0-the-shortest-version-hinglish)
1. [The project in one paragraph](#1-the-project-in-one-paragraph)
2. [Glossary: every word you'll see](#2-glossary-every-word-youll-see)
3. [Why this exists: the goal, the audience, the money](#3-why-this-exists-the-goal-the-audience-the-money)
4. [The owner's standing rules](#4-the-owners-standing-rules)
5. [How the project evolved: the timeline](#5-how-the-project-evolved-the-timeline)
6. [The big picture: two pipelines](#6-the-big-picture-two-pipelines)
7. [A tour of every folder and file](#7-a-tour-of-every-folder-and-file)
8. [The finished videos](#8-the-finished-videos)
9. [Logins and access: every account, in depth](#9-logins-and-access-every-account-in-depth)
10. [How the AI assistant works on this project (operating manual)](#10-how-the-ai-assistant-works-on-this-project-operating-manual)
11. [Runbook: how to make a new video today](#11-runbook-how-to-make-a-new-video-today)
12. [Google Flow: everything you need to know](#12-google-flow-everything-you-need-to-know)
13. [Writing prompts for Veo, and the character locks](#13-writing-prompts-for-veo-and-the-character-locks)
14. [Assembly: how clips become one video](#14-assembly-how-clips-become-one-video)
15. [Quality gates: how we know a video is "ready"](#15-quality-gates-how-we-know-a-video-is-ready)
16. [Content strategy: what we make and why](#16-content-strategy-what-we-make-and-why)
17. [Format and caption rules built into the code](#17-format-and-caption-rules-built-into-the-code)
18. [Environment, setup and keys](#18-environment-setup-and-keys)
19. [Tests](#19-tests)
20. [Known traps, condensed](#20-known-traps-condensed)
21. [Current status as of 2026-10-02](#21-current-status-as-of-2026-10-02)
22. [Where to read more](#22-where-to-read-more)
23. [FAQ for newcomers](#23-faq-for-newcomers)

---

## 0. The shortest version (Hinglish)

- Yeh project ek **AI video factory** hai. Yeh Instagram Reels aur YouTube Shorts ke liye
  **faceless short videos** banata hai — **Hindi aur Haryanvi** mein, Indian audience ke liye.
  Goal hai **asli income**, demo nahi.
- Video ka asli engine **Google Flow (Veo)** hai. Jio × Google AI Pro subscription ki wajah se yeh
  **free** hai. Flow ek baar mein ek **10 second ka clip** banata hai, jisme character **khud bolta
  hai, lip-sync ke saath**, Haryanvi mein bhi.
- Hamara code chaar kaam karta hai:
  1. Chrome browser ko chala ke Flow se clip banwata hai aur download karta hai.
  2. Har clip ko **Whisper** se sun ke check karta hai ki sahi line boli gayi ya nahi.
  3. Clips ko jodta hai, khaali hissa kaat deta hai, PART badge aur end card lagata hai, aur
     **upload-ready video** banata hai.
  4. Instagram aur YouTube ke liye caption likhta hai.
- `library/` folder mein abhi **10 finished videos** hain: **8 upload-ready**, 2 pehle hi post ho
  chuke hain. Upload abhi **haath se** hota hai.
- Ek purana, poora automatic pipeline bhi code mein hai (LangGraph: idea → script → images → awaaz
  → render → YouTube). Woh tested hai, par abhi use nahi hota — Groq key band ho gayi hai, aur still
  images waale videos kamzor lagte the.
- **Teen sabse zaroori rules:**
  - "Ready" sirf tab bolo jab video sach mein upload-ready ho.
  - Flow credits kabhi waste mat karo.
  - Flow ki screen pe bharosa mat karo. Sirf disk pe aayi file ko sach maano.
- **Login kaise hota hai** (poora §9 mein):
  - Script kabhi password nahi daalti.
  - Flow ke paanch Google accounts ek alag Chrome folder `~/.aica-chrome` mein signed-in hain.
    Yeh normal Chrome ki session files copy karke banaya gaya hai.
  - Wahi Chrome debug port 9222 pe khulta hai, aur `agent-browser` usse chalata hai.
  - **Dhyan do:** Chrome profiles 8 Aug ke baad badal gaye hain. Purani notes mein "Profile 1 copy
    karo" likha tha, jo ab galat hai (notes 2026-10-02 ko theek kar diye gaye). Paanchon accounts
    ab sirf `~/.aica-chrome` mein saath hain, isliye use kabhi delete mat karna.
- **AI assistant kaam kaise karta hai** (poora §10 mein):
  - Session ki shuruaat notes padh ke aur health check karke.
  - Pehle ek "canary" clip, phir baaki clips background mein.
  - Har line Whisper se check, aur sirf poori verification ke baad "ready".
  - Session ke end mein notes update.

---

## 1. The project in one paragraph

**aica** ("AI Content Agent") makes short vertical videos (9:16, 30–40 seconds) for Instagram
Reels and YouTube Shorts, in Hindi and Haryanvi, without anyone appearing on camera. The current
production method has five steps:

1. A story is written as a few one-line shots.
2. Each shot is sent to **Google Flow**, Google's AI video tool. Its Veo model returns a 10-second
   clip of the character speaking that exact line, with real lip sync.
3. A local copy of the **Whisper** speech-recognition model listens to every clip, to confirm the
   right words were actually spoken.
4. The clips are trimmed to where the speech ends, joined, branded and captioned with **ffmpeg**
   and **Pillow**.
5. The result goes into `library/<genre>/<series>/part_NN/`, ready for the owner to upload by hand.

An earlier, fully automated pipeline is still in the code and still tested. It is built on
**LangGraph** and runs idea → script → AI still images → text-to-speech → HTML/GSAP render →
YouTube upload. It is not used for new videos right now (§6.3 explains why).

---

## 2. Glossary: every word you'll see

| Term | Plain meaning |
|---|---|
| **Reel / Short** | A vertical short video on Instagram or YouTube. Ours are 1080×1920 pixels, 30 frames per second, about 30–40 seconds long. |
| **Faceless channel** | A channel where no real person appears on camera. Everything is AI-generated. |
| **aica** | This project's name: "AI Content Agent". The GitHub repo is `Manan0802/ai-content-agent`. |
| **Google Flow** | Google's web app for making AI video (`flow.google.com`). It is our video engine. |
| **Veo / Veo 3.1 / Omni Flash** | Google's video-generation models inside Flow. Omni Flash makes a 10-second clip that includes speech. |
| **Credits** | Flow's internal currency. One 10-second Omni Flash clip costs **15 credits** when "outputs" is set to x1. |
| **Jio × Google AI Pro** | A telecom bundle that gives Google AI Pro free for 18 months. This is why Flow costs us nothing. |
| **authuser** | Google's way of choosing between accounts signed into one browser: `?authuser=0`, `?authuser=1`, and so on. |
| **CDP / debug Chrome** | Chrome DevTools Protocol. Chrome is started with `--remote-debugging-port=9222` so scripts can control it. |
| **agent-browser** | The command-line tool (`npm i -g agent-browser`, version 0.26.0) that our scripts use to control Chrome over CDP. |
| **Lip sync** | Mouth movement that matches the spoken words. Veo puts it straight into the video it generates. |
| **Clip / shot** | One 10-second Flow generation. In our videos one clip is one line spoken by one character. |
| **Part / series / standalone** | A series is one story split into parts (Part 1, Part 2…). A standalone is a complete story in one video, with no parts. |
| **Character lock** | A fixed English description of a character, pasted **word for word** into every prompt so the character looks the same in every clip. |
| **Set lock** | The same idea for the location: a fixed description of the place, the light and the lens. |
| **End card** | The last ~2.6 seconds of a video. The final frame is frozen and darkened, with a question or "PART 2 — कल रात" written over it. |
| **PART badge / AI-Generated label** | The small red "PART N" tag in the top-left corner and the "AI-Generated" tag in the top-right corner. |
| **Dead air / trimming** | Flow always returns 10 seconds even if the line takes 4. Trimming cuts the silent tail off each clip. |
| **Whisper / mlx-whisper** | OpenAI's speech-to-text model. `mlx-whisper` runs the large-v3 version locally on the Mac's GPU, with no key and no limit. |
| **Round-trip check** | Turning our own audio back into text with Whisper, then comparing that text with the line we wrote. |
| **Contact sheet** | One image made of a still frame from every shot, side by side, so a person can check every picture against its line. |
| **ffmpeg / ffprobe** | Command-line tools that cut, join, encode and measure video and audio. |
| **Pillow / libraqm** | Pillow is the Python image library we use to draw badges and end cards. libraqm is the add-on it needs to draw Hindi (Devanagari) text correctly. |
| **Matra** | A Devanagari vowel sign. `ि` must be drawn *before* its consonant (`कि`). Without libraqm Pillow gets this wrong without any error. |
| **LangGraph** | A Python library for building a pipeline out of "nodes". The old automated pipeline is built with it. |
| **ContentState** | The single dictionary that carries a job's data from node to node in the old pipeline (`orchestrator/state.py`). |
| **HITL** | "Human in the loop": the pipeline stops and asks a person to approve before it continues. |
| **Groq** | A hosted LLM service. It was used for writing scripts and for Whisper. **Its key is dead as of Sept 2026.** |
| **TTS** | Text-to-speech. The old pipeline uses `edge-tts` (free Microsoft voices). In the Flow pipeline Veo does the voice itself. |
| **HyperFrames / GSAP** | HyperFrames is a CLI (`npx hyperframes`) that renders an HTML page with GSAP animations into an MP4. The old pipeline uses it. |
| **Pollinations / fal.ai / Gemini image** | Image generators the old pipeline can use. Pollinations is free; fal.ai is paid; Gemini needs a valid key. |
| **Narrated vs music mode** | The two ways a format carries its sound. In narrated mode characters speak. In music mode there is no voice: just music (or silence) and on-screen text. |
| **`BGM_MODE=silent`** | The default. Music-mode videos are rendered with **no audio at all**, so a trending sound can be added inside the Instagram app. |
| **Format profile** | One of `joke_10s`, `montage_35s`, `drama_50s`, `serial_75s` (`modules/formats.py`). Each sets the length, scene count and audio mode. |
| **library/ vs outputs/** | `library/` holds finished, upload-ready videos. `outputs/` is the scratch space for experiments and intermediate files. |
| **Review gallery vs dashboard** | The gallery (`web/`) is a static web page for approving or rejecting finished videos; it is **not deployed** yet. The dashboard (`dashboard/`) is a local page that shows the old pipeline's jobs. |
| **Haryanvi** | A dialect from Haryana, written here in Devanagari: `मन्नै`, `सै`, `कोन्या`, `गाड्डी`. It is a big content opportunity (§16). |
| **Trending audio** | A popular sound on Instagram. Using one helps a reel get shown to more people, but it can only be added inside the Instagram app. |

---

## 3. Why this exists: the goal, the audience, the money

- **The goal is real income**, not a demo or a portfolio project.
- **Audience:** Indian viewers, in Hindi, Haryanvi and Punjabi. Punjabi is supported in the old
  pipeline's prompts but has not been used in a finished video yet.
- **Platform order:** **Instagram first, YouTube second.** The same operator's content did
  85–340 views on YouTube Shorts and **10.1M** on Instagram. YouTube is still where ads pay
  (Shorts RPM in India is roughly ₹5–30 per 1,000 views), so it is the place the money comes from
  later.
- **Instagram page name chosen:** **सन्नाटा** ("silence"). It is for dark content only (horror,
  crime, drama). Light topics such as nostalgia or facts would need a second page.
- **Uploading is manual for now.** YouTube upload code exists and works (§6.1), but it is
  deliberately turned off: `.env` has no YouTube credentials, so the upload step quietly skips.
- **Monetisation reality** (from `docs/GO_LIVE_CHECKLIST.md`):
  - YouTube pays only after 1,000 subscribers plus either 4,000 watch-hours or 10M Shorts views in
    90 days.
  - The accounts we studied reached 80K–107K followers on only **26–40 posts**. Consistency and
    format matter more than volume.
  - The first month is for learning what works, not for earning.
- **Cost today: ₹0 per video.** Flow is covered by the subscription, Whisper runs locally, and
  ffmpeg and Pillow are free.

---

## 4. The owner's standing rules

The project owner is **Manan** (GitHub `Manan0802`). Manan is **non-technical** and writes in
**Hinglish**. Reply in Hinglish, and act like a full team (project manager, developer, tester,
researcher), not like an assistant that asks again about things already decided. These rules
override everything else in this document:

1. **Only say "ready" or "done" when the video is genuinely upload-ready.** A half-finished
   Part 1 was rejected once, rightly. If something is unverified, say so plainly.
2. **Never waste Flow credits.** Every failure path must stop *before* a spend is approved.
3. **Content boundaries:**
   - **In:** bold, mature themes such as infidelity, suspicion, betrayal, revenge and crime.
   - **Out:** nudity, sexual depiction, and any crime involving minors.
   - **Female characters:** write them as glamorous, elegant and confident, in modern or western
     clothes. Describe them through **wardrobe and presence, never body parts**.
4. **Don't stop a series at 3 parts.** One reference account's Part 4 got 8× more comments than
   its Part 1.
5. **Beat the reference accounts, don't copy them.**
6. **Bhakti and mythology content is in.** Manan asked for it back after it had been dropped.
7. **Don't take over Manan's browser tab** while Manan is using it. A background script once closed
   a tab Manan was working in and ruined a test.
8. **Git routing:** projects inside the `manan` folder push with the **Manan0802** GitHub account.
   Never commit the `.claude` or `.mcp.json` symlinks or `.DS_Store`; they point at shared config
   that can contain tokens.
9. **AI disclosure:** keep the small on-screen "AI-Generated" badge. Manan has explicitly waved off
   the stricter legal thresholds (a label over 10% of the screen, a spoken disclosure). Don't raise
   it again unless the channel grows a lot.

---

## 5. How the project evolved: the timeline

You need this to understand why the code contains **two different ways** of making a video.

| Date (2026) | What happened | Why it matters |
|---|---|---|
| **Jun 28** | Design spec and Phase 1 plan written (`docs/superpowers/specs/2026-06-28-ai-content-agent-design.md`). | The original vision: a fully automatic, multi-genre, free-first pipeline. The spec assumed a Windows laptop with **no GPU**. |
| Jun–Jul | **Phase 1, "text spine":** LangGraph orchestrator, idea and script agents (Groq Llama 3.3), approvals in the terminal. | `orchestrator/`, `agents/idea_generator.py`, `agents/script_writer.py`, `prompts/` |
| **Jul 5** | **Phase 2, "media pipeline":** AI images (fal.ai or Pollinations), Kokoro TTS, HTML composition, HyperFrames render, AI-disclosure card. | `agents/visuals.py`, `voiceover.py`, `composition_writer.py`, `render.py` |
| Jul 7 | Local dashboard. | `dashboard/` |
| **Jul 12** | **Phase 3:** YouTube upload (unlisted, with an approval gate, OAuth). | `agents/uploader.py`, `integrations/youtube_client.py`, `scripts/youtube_auth.py` |
| **Jul 20–21** | Studied real reels (views, audio, formats), then **Phase 4, "series and format engine":** multi-part serials, 4 format profiles, a voice per character, music mode, regional languages, engagement captions. | `modules/formats.py`, `voices.py`, `music.py`, `caption.py`, `agents/series_writer.py`, `orchestrator/series_runner.py` |
| Jul 22 | Edge TTS became the default voice (free, real Hindi voices). Gemini image and TTS clients added. Go-live checklist written. | `integrations/edge_tts_client.py`, `docs/GO_LIVE_CHECKLIST.md` |
| Jul 22–29 | Quality fixes: scene timing from real audio, English-only image prompts, a locked look per genre, the `torch`→`flashlight` fix, a different camera move per scene, the review gallery. | `modules/style.py`, `prompt_terms.py`, `camera.py`, `timing.py`, `gallery.py`, `web/` |
| **Jul 28–29** | **आख़री कॉल** crime serial, Parts 1–3, built with the old still-image pipeline in silent music mode. **Parts 1 and 2 were posted.** | `library/crime/aakhri-call/` |
| **Jul 29–31** | Tools research. Frame-by-frame study showed the best reference account uses real video, not stills. **Google Flow (Veo) found to be free through the Jio subscription → the big pivot.** First Flow driver and the `assemble` module written. | `tools/flow_clip.sh`, `modules/assemble.py` |
| **Aug 1** | **Batch 1:** दोस्ती का हिसाब Part 1 and तीसरा हाथ (standalone), both verified. | Commit `748d659` |
| Aug 8 | Caption fix: a finale or standalone must not promise a next part. Copying the signed-in Chrome profile verified. **Last git commit (`61e00e8`).** | |
| **Sep 5** | **Flow was rebuilt by Google and the old driver silently stopped working.** `flow_clip_v2.sh` written. The Groq key died, so Whisper moved to local `mlx-whisper`. **Batch 2: five new videos** (27 clips, 405 credits). | `tools/flow_clip_v2.sh`, `tools/verify_*.py`, `tools/assemble_batch2.py`, `content/batch2/`. Committed to git on 2026-10-02, together with this guide. |
| Oct 2 | This guide written. | |

> The Obsidian notes contain one more machine fact: the project is worked on from two machines.
> One is a **Windows laptop with no GPU** (what the original spec was written for). The other is a
> **MacBook Pro M3 Pro** (18 GB, real GPU). **All the Flow-era work happened on the Mac**, and
> several tools are now Mac-specific: `mlx-whisper`, the Devanagari font path, `stat -f%z`, and the
> Chrome profile paths.

---

## 6. The big picture: two pipelines

### 6.1 Pipeline A: the automated "stills" pipeline (LangGraph). Built and tested, currently idle.

```
python -m orchestrator.runner                       (one video)
python -m orchestrator.series_runner "<story>" 3    (a 3-part series)

 ┌──────────────────┐   ┌───────────┐   ┌───────────────┐   ┌────────────┐
 │ idea_generator   │──▶│ hitl_topic│──▶│ script_writer │──▶│ hitl_script│
 │ (Groq: 3 ideas,  │   │ (approve?)│   │ (Groq: JSON   │   │ (approve?) │
 │  viral_score)    │   └───────────┘   │  script)      │   └─────┬──────┘
 └──────────────────┘                   └───────────────┘         │
                                                                   ▼
 ┌──────────┐   ┌───────────────────┐   ┌──────────────┐   ┌──────────────┐
 │ uploader │◀──│ render            │◀──│ composition_ │◀──│ voiceover    │◀── visuals
 │ (YouTube,│   │ (hyperframes check│   │ writer (HTML │   │ (edge-tts per│   (AI image
 │ unlisted)│   │  → approve? →     │   │ + GSAP)      │   │  character,  │    per scene)
 └──────────┘   │  render MP4)      │   └──────────────┘   │  or silent)  │
                └───────────────────┘                      └──────────────┘
Output: outputs/<job_id>/render/final.mp4  +  outputs/<job_id>/state.json
```

**How it works:**

- One `ContentState` dictionary flows through the nodes. Each node reads it, adds its own results,
  and passes it on. Errors are added to `state["errors"]` instead of crashing the run.
- **Approval gates:** topic, script, render and publish. `CLINotifier` asks in the terminal
  (`[a]pprove / [r]eject`). `auto=True` approves everything automatically.
- **Series mode:** `series_writer` plans the whole story once. It fixes one art style
  (`style_prompt`) and each character's appearance, then runs every part through the pipeline,
  starting at `script_writer`. Each part opens by paying off the previous part's cliffhanger.
- **Sound:** narrated formats get one edge-tts voice per character. Music formats get no voice;
  they are silent by default, or use a track from `assets/music/` if `BGM_MODE=baked`.
- **Pictures:** still images, each with a slow pan or zoom ("Ken Burns" effect), crossfades
  between scenes, and the dialogue as on-screen text in music mode.

**Why it's idle:**

1. **The Groq key is dead** (`Access denied` on every endpoint), so the idea and script nodes can't
   run.
2. **Still images look weak** next to real video. The best reference account generates real video
   per scene.
3. **Free image generators can't keep a character's face the same** from one scene to the next.

It still works end to end with mocked services: all of its tests pass. It is also the path that
made the आख़री कॉल crime serial.

### 6.2 Pipeline B: the Flow pipeline. This is how videos are made now.

```
 content/batch2/videos.py      ← the video written as DATA: cast locks, set, 5–6 shots, outro, caption
          │
          ▼  tools/run_batch2.sh  (runs everything below, video by video)
 tools/batch_generate.sh <key> <authuser>
          │   for each shot: build the prompt → call flow_clip_v2.sh
          │   (skips clips already on disk, so it is safe to resume;
          │    retries only if the failure happened BEFORE credits were spent)
          ▼
 tools/flow_clip_v2.sh <authuser> "<prompt>" <out.mp4>
          │   drives Chrome (port 9222) → flow.google.com → new project → type prompt →
          │   send → wait for the "Approve (15 credits)" box → approve → wait for the clip →
          │   download it with curl
          ▼
 /tmp/aica_clips/<key>/c1.mp4 … c6.mp4         (raw 10-second clips, 720×1280)
          │
          ▼
 tools/assemble_batch2.py <key>
          │  1. Whisper round-trip on every clip  → REFUSES to assemble if a word looks wrong
          │  2. picks a trim point per clip (Whisper's end, or measured from the audio)
          │  3. modules/assemble.build_part: normalise → trim → join → badges → end card
          │  4. modules/caption.build_caption: Instagram and YouTube captions
          │  5. modules/library.publish → library/<niche>/<slug>/part_NN/
          ▼
 tools/verify_final.py <key>
             format · decode errors · audio vs video length · slice at every cut and
             transcribe it (is the right line in the right place?) · contact sheet
          ▼
 A person watches it → uploads it by hand with caption.txt
```

What makes this pipeline better:

- **Real video with real lip sync**, and Veo speaks **genuine Haryanvi**. We proved it by
  transcribing our own output: "एक चा मिलेगी के".
- **Animal-headed characters** (a lion head on a human body in a black kurta) stay **the same
  across clips**, where human faces drift. A whole genre of successful reference accounts already
  uses this look.
- It costs **₹0**.

### 6.3 Which one to use when

| Situation | Use |
|---|---|
| Any new dialogue video (drama, crime, comedy, horror, bhakti) | **Pipeline B (Flow)** |
| A silent, text-on-screen serial with music added in the app (like आख़री कॉल) | Pipeline A in music mode can do this, but it needs a working script LLM key, and its stills are the weak point |
| Testing pipeline logic without spending anything | Pipeline A with mocks (the test suite) |
| Auto-uploading to YouTube | Pipeline A's uploader, after the one-time OAuth setup (§9.4) |

---

## 7. A tour of every folder and file

```
aica/
├── PROJECT_GUIDE.md          ← this file
├── README.md                 Phase 1–4 overview (the old pipeline). Partly out of date: setup is Windows-flavoured, no Flow.
├── AGENTS.md                 Instructions for the Codex AI tool (points at Manan's tool catalogue). Not used by the code.
├── AI_Content_Creation_PRD.md The original product requirements (big vision: 11 modules, money model). Historical.
├── config.py                 All settings in one frozen dataclass (SETTINGS), read from .env.
├── requirements.txt          Python dependencies. ⚠ incomplete for the Flow path (see §18).
├── .env  → ../claude-transfer/.env   Secrets (symlink, git-ignored). Never print or commit.
├── .env.example              The variable names, with no values.
├── .gitignore                Ignores .venv, .env, outputs/, library/, web/public/, .claude, .mcp.json …
├── p2.json                   A leftover file holding a web-scraper "rate limit" error. Nothing uses it.
├── .claude → ../claude-transfer/.claude   Shared Claude Code config (symlink). Never commit.
├── .mcp.json → ../claude-transfer/.mcp.json  Shared MCP config (symlink). Never commit.
├── .agents/  .codex/          Codex tool configuration (Manan's tool arsenal). Not part of the app.
├── .venv/                    The Python 3.12 virtualenv.
│
├── orchestrator/   Pipeline A's brain (LangGraph)
├── agents/         Pipeline A's steps (one file per node)
├── prompts/        The LLM instructions used by the agents
├── integrations/   Thin wrappers around outside services (Groq, images, TTS, HyperFrames, YouTube)
├── modules/        Shared building blocks, used by BOTH pipelines (assemble, caption, library…)
├── tools/          Pipeline B: Flow driver, batch runners, verifiers, assembler
├── content/        Stories and shot lists (for Pipeline B), as Markdown and as Python data
├── library/        ★ The finished, upload-ready videos (git-ignored: they exist ONLY on this Mac)
├── outputs/        Scratch space: every job, experiment and intermediate render (git-ignored)
├── assets/         Music beds and reference images
├── dashboard/      Local web page listing Pipeline A's jobs
├── web/            The review gallery (static site for Cloudflare Pages). Not deployed.
├── scripts/        One-off helpers (YouTube OAuth, build the gallery)
├── tests/          289 tests (pytest). Never touch the network.
├── docs/           Design spec, phase plans, research, go-live checklist
└── logs/           Logs from MCP servers on the dev machine. Not project data.
```

### 7.1 `orchestrator/`: Pipeline A's brain

| File | What it is for |
|---|---|
| `state.py` | Defines `ContentState`, the dictionary every node reads and writes: job_id, status, niche, language, format_profile, topic, script, visual and audio assets, paths, YouTube id, series info. `new_state()` creates an empty one. Status moves through `idle → running → media_complete → published` (or `failed`). |
| `graph.py` | `build_graph()` wires the 9 nodes into a LangGraph `StateGraph`, including the two approval gates and the "stop here if rejected" routes. Everything outside the graph (the LLM, image and TTS clients, the CLI, YouTube) is passed in, so tests can swap in fakes. |
| `runner.py` | `run_job()` runs one video. It picks the image client (`IMAGE_PROVIDER`) and the TTS client (`TTS_PROVIDER`), runs the graph, and saves `state.json`. Entry point: `python -m orchestrator.runner`. |
| `series_runner.py` | `run_series()` plans N parts once, then runs each part through the same graph, starting at `script_writer`, passing the previous part's cliffhanger along. Entry point: `python -m orchestrator.series_runner "<story idea>" 3`. |

### 7.2 `agents/`: one file per pipeline step (Pipeline A)

| File | What it does |
|---|---|
| `idea_generator.py` | Asks the LLM for 3 video ideas in a genre, scored by `viral_score`. The "trends" are a fixed seed list per genre (`SeedTrendsProvider`); there is no live trend source yet. |
| `script_writer.py` | Asks the LLM for a full JSON script: title, hook, characters, segments (speaker, dialogue, visual_direction, emotion), cliffhanger, hashtags. |
| `series_writer.py` | Turns one story idea into N parts. Each part has a beat and a cliffhanger. It also fixes one `style_prompt` and each character's `appearance` for the whole series. |
| `visuals.py` | Builds each scene's image prompt (locked style + scene + character look), generates the image, and downloads it to a **short** local filename. Long Hindi URLs once broke filenames with an `ENAMETOOLONG` error. |
| `voiceover.py` | Narrated mode: one TTS voice per character, then measures the **real** audio length and re-times each scene from it. Music mode: no TTS; each card is timed by reading speed, and a music track is picked only if `BGM_MODE=baked`. |
| `composition_writer.py` | Writes `index.html`: one `<section>` per scene, GSAP animations (a different camera move per scene, crossfades), dialogue text in music mode, the PART badge, the AI label, the disclosure card and the end card. |
| `render.py` | Runs `hyperframes check` (lint, layout, motion and contrast in one pass), asks for approval, renders `render/final.mp4`, and confirms the file exists and isn't empty. |
| `uploader.py` | Builds the title, description and tags, asks "Publish?", and uploads to YouTube as **unlisted**. If YouTube isn't configured it skips quietly, so the video is never lost. |

### 7.3 `prompts/`: what we tell the LLM

| File | Content |
|---|---|
| `idea_prompts.py` | "Propose the 3 best video ideas, as JSON." |
| `script_prompts.py` | The rules learned from the reference reels: hook = a question, a bold claim, or starting mid-action (never scene-setting); short lines; dialect written as real dialect; music mode has no narration; the cliffhanger is spoken inside the dialogue; `visual_direction` in **English only**, describing the shot rather than the feeling. |
| `series_prompts.py` | The "show-runner" prompt: N parts, every part ends on a cliffhanger, each part pays off the previous one, plus a locked `style_prompt` and character `appearance`s. |

### 7.4 `integrations/`: wrappers around outside services

Every external call goes through one of these small classes, so tests can replace them with fakes.

| File | Service | State today |
|---|---|---|
| `groq_client.py` | Groq LLM (`llama-3.3-70b-versatile`), JSON mode | **Key dead** (`Access denied`) |
| `pollinations_client.py` | Pollinations.ai images: free, no key, warms the URL and retries on 429 errors | Works; can't keep characters consistent |
| `fal_client.py` | fal.ai FLUX.2 (with a reference image) and FLUX schnell. Paid. | No key set |
| `gemini_client.py` | Gemini image model with reference-image character lock | The key in `.env` starts with `AQ.`, which is **not a valid AI Studio key** (those start with `AIza`) |
| `edge_tts_client.py` | Microsoft Edge TTS: `hi-IN-MadhurNeural` (male), `hi-IN-SwaraNeural` (female). Free, unlimited. **Default.** | Works. Gives 8 character voices from 2 base voices by changing rate and pitch. |
| `gemini_tts.py` | Gemini TTS (real Hindi voice) | Free quota tiny; key invalid anyway |
| `hyperframes_tts.py` | Kokoro TTS through the HyperFrames CLI (English model, offline) | Works; wrong accent for Hindi |
| `hyperframes_cli.py` | `npx hyperframes check` / `render` | Works (needs Node.js 22+) |
| `youtube_client.py` | YouTube Data API v3 upload. Sets `containsSyntheticMedia: true`, not made for kids, privacy from `.env`. | Not configured (no OAuth credentials) |

### 7.5 `modules/`: shared building blocks

| File | What it is for | Used by |
|---|---|---|
| `assemble.py` | **The heart of Pipeline B.** `speech_end()` finds where the speech stops; `concat()` normalises and joins clips; `add_furniture()` adds the badges and end card; `build_part()` runs all three. §14 has the details. | B |
| `caption.py` | `build_caption()` writes the hook line, the asks (follow, share with 3 friends, comment a keyword), "Part N-1 is on the profile", and up to 5 hashtags on Instagram (plus `#Shorts` on YouTube only). A finale or standalone never promises a next part. | A + B |
| `library.py` | `slugify()`, `part_dir()`, `publish()` copy a finished video into `library/<niche>/<series>/part_NN/` with `caption.txt` and `meta.json`. | A + B |
| `formats.py` | The 4 format profiles, with lengths taken from real measured reels. | A |
| `style.py` | A locked "look" per genre (grade, lens, grain). **Never a location**: a look is pasted into every prompt, so naming a place forces every scene there. | A |
| `prompt_terms.py` | Swaps Indian or British words that image models misread: `torch`→`flashlight`, `lift`→`elevator`, `lorry`→`truck`. | A |
| `voices.py` | Gives each character id its own stable voice (no repeats within one script). | A |
| `music.py` | Maps a genre to a mood folder and picks a track deterministically per series, so all parts share one track. | A |
| `timing.py` | How long a text card stays on screen: `0.8s + words/2.6`, kept between 2.2s and 4.5s. | A |
| `camera.py` | 6 camera moves (push in, pull back, drift left/right, rise, sink), cycled per scene. | A |
| `job_store.py` | Saves and lists `outputs/<job_id>/state.json` (the dashboard reads these). | A |
| `notifier.py` | `CLINotifier` (asks in the terminal) and `AutoApproveNotifier`. | A |
| `gallery.py` | Scans `library/` and builds the static review site into `web/public/`. | gallery |
| `preview.py` | Makes a small 720p copy of a video (about 1.7 MB) for the gallery. Cloudflare Pages refuses files over 25 MiB. | gallery |

### 7.6 `tools/`: Pipeline B (Flow)

| File | What it does | Status |
|---|---|---|
| `flow_clip_v2.sh` | **Generates ONE Flow clip and downloads it.** `bash tools/flow_clip_v2.sh <authuser> "<prompt>" <out.mp4> [existing_project_url]`. Takes about 2 minutes. Every failure before approval prints "0 credits spent". | **Current.** |
| `flow_clip.sh` | The old driver, for Flow before the September rebuild. It still runs and exits 0, but **produces nothing** on the new Flow. A warning header at the top says so. | **Do not use.** Kept for reference. |
| `batch_generate.sh` | All clips of one video into `/tmp/aica_clips/<key>/`. Skips clips already on disk. Retries only failures that happened **before** approval. | Current |
| `batch_all.sh` | Runs `batch_generate.sh` for v1…v5 in order. | Current |
| `run_batch2.sh` | The full batch: generate, then verify, assemble and publish each video, then print a summary. | Current |
| `verify_lines.py` | Whisper round-trip for one clip. Compares words by their **consonant skeleton**, so dialect spelling differences pass while real word swaps get caught. | Current. Covered by `tests/test_line_verification.py` (19 tests). |
| `assemble_batch2.py` | Verifies every clip, chooses trim points, builds the part, writes captions and `meta.json`, publishes to `library/`. **Refuses to assemble** if a word looks misread, unless you set `ALLOW_MISREAD=1` after reading each pair. | Current |
| `verify_final.py` | The final gate on the finished file (§15.3). Prints `VERIFIED — upload ready` or `NOT READY`. | Current |

### 7.7 `content/`: the stories

| Path | What it is |
|---|---|
| `content/teesra_haath.md` | Script and reasoning for the तीसरा हाथ horror standalone (batch 1). |
| `content/batch2/PLAN.md` | Why these five videos were chosen. Every pick is tied to measured evidence. |
| `content/batch2/v1_…v5_*.md` | One readable script per video: cast lock, set, shot table, end card. |
| `content/batch2/videos.py` | **The same five videos as Python data.** This is what the tools actually read. `build(shot, video)` turns one shot into the exact Flow prompt (§13). |

### 7.8 `library/`: the finished videos

```
library/<niche>/<series-slug>/part_NN/
    final.mp4     the file you upload (1080×1920, 30fps)
    caption.txt   the Instagram caption (≤5 hashtags)
    meta.json     YouTube caption, every line, length, and the verification report per clip
```

⚠ `library/` is **git-ignored**, so these videos exist **only on this Mac**. There is no backup.
The full list is in §8.

### 7.9 `outputs/`: scratch space (about 340 MB, git-ignored)

- ~200 folders named with 8 hex characters (e.g. `0ca211eb/`) are Pipeline A job runs. Each holds
  `state.json`, `index.html`, `images/`, `assets/audio/` and `render/final.mp4`.
- Named folders are experiments and intermediate builds: `aakhri_call_p2/`, `aakhri_call_p3/`,
  `crime_p1/`, `dosti_ka_hisaab_p1/`, `dosti_p1_hybrid/`, `dosti_veo_p1/`, `batch2_v1…v5/`
  (where `assemble_batch2.py` builds before copying to the library), and `job/`.
- Nothing in here is precious once a video is in `library/`.

### 7.10 `assets/`

| Path | What it is |
|---|---|
| `assets/music/{dark,emotional,comedy,devotional}/` | Music beds, used only when `BGM_MODE=baked`. Only two tracks exist so far (`dark/tension_drone.mp3`, `emotional/warm_pad.mp3`). `README.md` explains how to fill them. |
| `assets/reference/style/` | Early art-direction tests per genre (health organs in Pixar style, bhakti, night horror…), made free with Pollinations. |
| `assets/reference/character/` | Early heroine and couple character studies. `README.md` keeps the exact prompts; the prompts are the reusable asset. |

### 7.11 `dashboard/`: local job viewer (Pipeline A)

- `uvicorn dashboard.app:create_app --factory --port 8000` → open `http://localhost:8000`.
- Lists every job in `outputs/` with its status, genre, topic and script, and plays its video.
  Read-only.
- It does **not** show `library/` or the Flow videos. That is the gallery's job.

### 7.12 `web/`: the review gallery (built, not deployed)

| File | What it is |
|---|---|
| `index.html` | One page: a video card per library item, with Approve / Reject. Saves to D1 when deployed, otherwise to `localStorage`. |
| `functions/api/status.js` | A Cloudflare Pages Function: reads and writes review status in a D1 database (input is validated). |
| `schema.sql` | One `review` table (id, status, updated_at). |
| `wrangler.toml` | Cloudflare config. `database_id = "PASTE_AFTER_d1_create"` is the blocker. |
| `public/` | Build output (git-ignored). It currently holds only one preview, from an early test. |

- Build it with `python -m scripts.build_gallery`.
- Deploy it with `cd web && npx wrangler pages deploy public`, after creating the D1 database
  (§21).
- **Why Cloudflare and not Vercel:** Vercel's free plan forbids commercial use, and this channel is
  meant to earn.

### 7.13 `scripts/`

- `youtube_auth.py`: one-time Google sign-in that writes `YOUTUBE_REFRESH_TOKEN` into `.env`.
- `build_gallery.py`: builds `web/public/`.

### 7.14 `docs/`

| Path | What it is |
|---|---|
| `docs/superpowers/specs/2026-06-28-ai-content-agent-design.md` | The locked design decisions and their reasons (some are outdated now, e.g. "no GPU", "fal.ai", "HyperFrames for everything"). |
| `docs/superpowers/plans/*` | Step-by-step build plans for Phases 1–4 and the dashboard. |
| `docs/superpowers/specs/2026-07-2*-*analysis.md` | Reels research: views, formats, audio transcripts. |
| `docs/research/transcripts/*.txt` | Placeholder transcript files for 15 reference reels. **All of them are empty (0 bytes).** The real findings are in the analysis specs above. |
| `docs/GO_LIVE_CHECKLIST.md` | As of Jul 22: what was working, what only Manan can do. **Partly out of date:** it says Groq works and recommends paying for fal.ai, both of which predate Flow. |

### 7.15 `tests/`

48 test files, 289 tests. See §19.

---

## 8. The finished videos

All of these were checked on 2026-10-02 with `ffprobe` (length, audio stream). "Ready" means the
whole verification process in §15 was run, but **nobody has yet watched any of them from start to
finish in a normal video player.** Do that before posting (§21).

| # | Video | Genre | Path (`library/…`) | Length | Audio | State |
|---|---|---|---|---|---|---|
| 1 | **आख़री कॉल — Part 1** | crime | `crime/aakhri-call/part_01/` | 38.6s | **none** (silent on purpose) | **Already posted** |
| 2 | **आख़री कॉल — Part 2** | crime | `crime/aakhri-call/part_02/` | 35.6s | **none** | **Already posted** |
| 3 | **आख़री कॉल — Part 3** (finale) | crime | `crime/aakhri-call/part_03/` | 36.0s | **none**: add a trending sound in the Instagram app | Ready |
| 4 | **दोस्ती का हिसाब — Part 1** | drama | `drama/dosti-ka-hisaab/part_01/` | 37.1s | Veo dialogue: **add NO music** | Ready |
| 5 | **दोस्ती का हिसाब — Part 2** | drama | `drama/dosti-ka-hisaab/part_02/` | 38.3s | Veo dialogue: **add NO music** | Ready |
| 6 | **खून का सौदा — Part 1** | crime | `crime/khoon-ka-sauda/part_01/` | 29.3s | Veo dialogue: **add NO music** | Ready |
| 7 | **सासु का WiFi** (standalone) | comedy | `comedy/sasu-ka-wifi/part_01/` | 31.8s | Veo dialogue: **add NO music** | Ready |
| 8 | **तेरा हिसाब** (standalone) | bhakti-horror | `mythology/tera-hisaab/part_01/` | 36.5s | Veo dialogue: **add NO music** | Ready |
| 9 | **घर का वो कोना** (standalone) | horror / vastu | `horror/ghar-ka-wo-kona/part_01/` | 35.0s | Veo dialogue: **add NO music** | Ready |
| 10 | **तीसरा हाथ** (standalone) | horror | `horror/teesra-haath/part_01/` | 30.7s | Veo dialogue: **add NO music** | Ready |

> **The audio rule matters.** Music added on top of Veo dialogue drowns the voices. The silent crime
> videos are the opposite case: trending audio helps a reel get seen and can only be attached
> inside the Instagram app, so the pipeline hands over a silent video on purpose. **Do not "fix"
> either one.**
>
> Standalones live in a `part_01/` folder only because of how folders are named. Their `meta.json`
> says `standalone: true`, they carry no PART badge, and their captions promise nothing.

### What each story is

- **आख़री कॉल** (crime serial, 3 parts, Pipeline A): a still-image thriller with burned-in dialogue
  text and no voice. Part 1 was built before the `torch`→`flashlight` fix; rebuilding it is an open
  item.
- **दोस्ती का हिसाब** (Haryanvi drama, a lion and a dog at a roadside dhaba):
  - *Part 1:* शेरू (lion, once rich, now broke) meets his old friend काळू (dog, the dhaba waiter).
    End card: `शेरू की गाड्डी किसनै खरीदी थी?`
  - *Part 2:* the answer: काळू bought शेरू's car by selling his own land. End card:
    `के शेरू वा चाबी लेगा?` / `PART 3 — कल रात`.
  - Lines of Part 2:
    `यो हॉर्न... मेरी गाड्डी का सै।` · `तू अंदर चाल जा। मैं देख लूँ सूं।` · `यो तो मेरी ए गाड्डी सै।` ·
    `मन्नै खरीदी। अपणी जमीन बेच के।` · `क्यूँ काळू? क्यूँ?` ·
    `तेरी गाड्डी किसे और कै हाथ मैं ना जाणी चाहिए थी।`
- **खून का सौदा** (Haryanvi crime, planned for 4 parts): a goat-headed father (बिरजू) facing a
  buffalo-headed moneylender in dark glasses (कालिया). "Two lakh, tonight. In return: one name, and
  one night's work." This is the first test of a combination nobody else was found doing: a
  photoreal animal protagonist in a crime serial. End card: `कालिया नै कौण सा नाम लिया?` /
  `PART 2 — कल रात`.
- **सासु का WiFi** (Haryanvi comedy): a cat-headed mother-in-law changes the WiFi password; the
  rabbit-headed daughter-in-law finds the hint is the mother-in-law's own name. This one tests the
  biggest gap we measured: huge Haryanvi demand, almost no AI supply.
- **तेरा हिसाब** (bhakti-horror): an owl-headed चित्रगुप्त reads out "you threw away four thousand
  rotis in this life", and a buffalo-headed यमराज sentences you: "next life, hunger, not bread".
  It passes a **verdict on the viewer's own life** and is **never numbered**; both rules came from
  the research (§16).
- **घर का वो कोना** (vastu fear): "Don't sleep in the south-west corner. The people who lived here
  before slept there too." It is shot at night so human faces don't drift between clips.
- **तीसरा हाथ** (Haryanvi horror): two friends on a motorbike at night. "Why is your hand on my
  shoulder?" / "Both my hands are behind me, brother." / "Then whose third hand is this?" → the
  mirror reveal → "Don't stop the bike."

---

## 9. Logins and access: every account, in depth

**No script in this project ever types a password.** Every login is one of three things, set up once
by a person:

- a saved browser session
- a token file
- an API key

This section covers each one: what it is, where it lives, how to check it, and how to fix it.

### 9.1 All logins at a glance

| Login | Used for | How it's logged in | Where the login lives | Set up by | State on 2026-10-02 |
|---|---|---|---|---|---|
| **Google Flow** (5 AI Pro accounts) | Making every video clip | A copied Chrome session, controlled through debug port 9222 | `~/.aica-chrome/`, a separate Chrome data folder | Manan signs in; the assistant copies the session files | The folder holds **all five accounts** (last used 2026-09-05). **Only `authuser=0` gets past Flow's first-run onboarding.** |
| **Jio 5G plan** | Keeps Google AI Pro free | Manan's phone plan, ₹349 or more | Jio account | Manan | Must stay active, or Flow stops being free |
| **GitHub** (git push) | Saving code | HTTPS token, chosen automatically for every repo inside `~/Desktop/manan/` | `~/.gitconfig` → `~/.gitconfig-manan` → `~/.git-credentials-manan` | Already done | Pushes as **Manan0802** |
| `gh` CLI | GitHub from the terminal (PRs, issues) | Keyring login | macOS Keychain | – | Logged in as a **different** GitHub account. Don't use `gh` for this repo without switching (§9.3). |
| **YouTube API** | Auto-upload (optional) | OAuth refresh token | `.env` (`YOUTUBE_*`) | Manan, once | Not set up |
| **Instagram** | Posting | The Instagram phone app, by hand | Manan's phone | Manan | Manual; no API |
| **Cloudflare** | Hosting the review gallery | `npx wrangler login` | wrangler's local config | Manan, once | Not done |
| **Groq** | Pipeline A's script writer | API key | `.env` | – | **Dead** |
| **Gemini API** | Optional images and TTS | API key | `.env` | – | **Invalid** key |
| **mlx-whisper** | Checking speech | No login; runs on the Mac | Model cached in `~/.cache/huggingface/hub/models--mlx-community--whisper-large-v3-mlx` | – | Works |

### 9.2 Google Flow login, in depth

**The problem, in three facts:**

1. A script can control Chrome only if Chrome was started with `--remote-debugging-port`.
   **Chrome 136 and later refuses that flag on your normal Chrome folder.** It allows it only
   together with a separate `--user-data-dir`.
2. A separate folder starts **empty: nobody is signed in.**
3. You can't sign in from it either. **Google blocks sign-in from a browser under automation**
   ("This browser or app may not be secure").

**The solution:** copy the *session files* of a normal, signed-in Chrome profile into a separate
folder (`~/.aica-chrome`), and start Chrome on that folder with debugging turned on. The copied
cookies carry the Google sign-in of every account in that profile, so Flow opens signed in, with
the PRO plan.

> **Why the copy works only on this Mac:** on macOS, Chrome encrypts cookies with a key stored in
> the user's login Keychain (the "Chrome Safe Storage" item). A second Chrome on the same Mac user
> can read that key, so the copied cookies decrypt. Copied to another computer, the same files are
> useless.

**What gets copied:**

- `Local State` (from Chrome's top folder)
- From the profile folder:
  - `Cookies`: the sign-in itself
  - `Login Data`
  - `Preferences`: also records which Google accounts the profile holds
  - `Web Data`
  - `Secure Preferences`

#### ⚠ The Chrome profile map changed after 2026-08-08

This was checked on 2026-10-02 from Chrome's own `Local State` and each profile's `Preferences`.

| Chrome folder | In the August notes | Now (2026-10-02) |
|---|---|---|
| `Default` | the bachatt work account | the **personal Gmail** profile; lists 3 Google accounts |
| `Profile 1` | personal Gmail, holding all five AI Pro accounts | the **bachatt work account**; lists 2 accounts |
| `Profile 2` | another person's account | no longer exists |
| `~/.aica-chrome` (the debug copy) | – | lists **all five AI Pro accounts**; last used 2026-09-05 |

What this means:

- **The old instruction "copy `Profile 1`" now copies the wrong account.** Flow would open signed
  out, or on the work account.
- **No normal Chrome profile lists all five AI Pro accounts any more.** The existing debug copy is
  the only place all five are together. **Treat `~/.aica-chrome` as precious: don't delete it or
  copy over it unless it has actually signed out.**
- One caveat: the list in `Preferences` is what Chrome records about its accounts. It is a strong
  signal, but the real test is always the account check below.

**To see which profile holds which accounts** (this prints email addresses on your own screen only;
never paste them into git):

```bash
python3 - <<'EOF'
import json, os, glob
base = os.path.expanduser('~/Library/Application Support/Google/Chrome')
for p in [base + '/Default'] + sorted(glob.glob(base + '/Profile *')) + [os.path.expanduser('~/.aica-chrome/Default')]:
    try:
        accts = json.load(open(p + '/Preferences')).get('account_info', [])
        print(p, '->', [a.get('email') for a in accts])
    except Exception as e:
        print(p, '-> unreadable:', e)
EOF
```

#### Daily start: reuse the debug folder, don't copy

```bash
if lsof -nP -iTCP:9222 -sTCP:LISTEN >/dev/null; then
  echo "debug Chrome already running"
else
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --user-data-dir="$HOME/.aica-chrome" --remote-debugging-port=9222 --no-first-run >/dev/null 2>&1 &
fi
```

This opens a **separate, visible Chrome window**. Manan's normal Chrome keeps running beside it,
untouched, because the two use different folders.

#### Check every account before spending anything

```bash
for U in 0 1 2 3 4; do
  agent-browser --cdp 9222 goto "https://flow.google.com/?authuser=$U" >/dev/null 2>&1; sleep 20
  echo "authuser=$U $(agent-browser --cdp 9222 eval "(()=>{const t=document.body.innerText;return JSON.stringify({signedOut:/Create with Google Flow/i.test(t),newProject:/New project/i.test(t),overlay:document.querySelectorAll('.cdk-overlay-backdrop').length});})()" | tail -1)"
done
```

| You see | Meaning | Fix |
|---|---|---|
| `signedOut:true`, or no `newProject` (a marketing page) | Session expired, or the wrong profile was copied | Re-copy (below) |
| `newProject:true` with `overlay` above 0 | This account never finished Flow's first-run onboarding | Manan clicks through it by hand (below) |
| `newProject:true`, `overlay:0` | Ready to generate | – |
| You landed on `labs.google/...` | The old address redirects and **drops `?authuser`** | Always use `flow.google.com` |

> The older notes check for a "PRO" badge. That check was written for the pre-September Flow. On
> today's Flow the dependable sign is the project list with a working "New project" button, which
> is exactly what `flow_clip_v2.sh` waits for before it does anything.

#### Unlocking accounts 1–4 (Manan, about 30 seconds each)

Automation could not finish Flow's first-run dialog: its "Continue" stays disabled even after the
policy is scrolled to the bottom. A person can do it:

1. In the **debug Chrome window** (an ordinary visible window; just click in it normally), open
   `https://flow.google.com/?authuser=1`.
2. On "Experience and shape AI tools for creativity", leave the marketing and research checkboxes
   **unchecked**, then click **Next**.
3. On "Review our privacy policy", scroll to the bottom, click **Continue**, then
   **Start Creating**.
4. Open **Agent settings** and set:
   - number of outputs to **x1** (otherwise a clip costs 30 credits instead of 15)
   - **Confirm before generating = Always**. This is our spend gate.
   - Never choose "Always approve". The 9:16 setting is ignored anyway; the prompt states the
     orientation.
5. Repeat for `authuser=2`, `3` and `4`, then run the check loop above.

Google stores the onboarding per account, so this should be a one-time job. The check loop
confirms it.

**Which `authuser` number is which account?** The number is the order in which accounts were added
to that browser's Google session; nobody chose it. To find out, open
`https://myaccount.google.com/?authuser=N` in the debug window and read the email it shows. All of
batch 2 ran on `authuser=0`.

#### Re-copying (only when the session has really expired)

1. Run the profile snippet above to find which normal Chrome profile holds the AI Pro accounts.
   - If **no** profile holds all five, Manan opens the best one in normal Chrome and uses the
     profile menu's **"Add another account"** for each missing one. **Manan types the passwords;
     a script never does.**
2. **Quit every Chrome window, normal and debug.** Copying a `Cookies` database while Chrome is
   writing to it gives a half-written file.
3. Copy, keeping the old folder as a backup until the new one is proven:

   ```bash
   SRC_PROFILE="Default"       # ← whichever profile step 1 showed holds the accounts
   SRC="$HOME/Library/Application Support/Google/Chrome"
   DST="$HOME/.aica-chrome"
   pkill -f 'user-data-dir=.*aica-chrome'
   mv "$DST" "$DST.bak-$(date +%Y%m%d)"
   mkdir -p "$DST/Default"
   cp "$SRC/Local State" "$DST/"
   for f in Cookies "Login Data" Preferences "Web Data" "Secure Preferences"; do
     cp "$SRC/$SRC_PROFILE/$f" "$DST/Default/"
   done
   ```

4. Start it ("Daily start" above) and run the check loop. Delete the `.bak-…` folder only after
   every account checks out.

**Never** keep the profile in `/tmp`: it is wiped on reboot, which is how the first debug profile
disappeared.

### 9.3 GitHub: how pushes go out as Manan0802

The login is picked automatically by folder:

- `~/.gitconfig` contains:

  ```
  [includeIf "gitdir:/Users/beastathome/Desktop/manan/"]
      path = /Users/beastathome/.gitconfig-manan
  ```

- `~/.gitconfig-manan` sets `user.name = Manan0802` and
  `credential.helper = store --file ~/.git-credentials-manan`. That file holds a token for
  Manan0802, so it is a **secret: never print it**.
- Result: inside any repo under `~/Desktop/manan/`, a plain `git push` goes out as Manan0802.
  Outside that folder, the default account is used.

To check:

```bash
git config --show-origin user.name     # expect: file:/Users/beastathome/.gitconfig-manan  Manan0802
git remote -v                          # https://github.com/Manan0802/ai-content-agent
```

Two more things to know:

- **The `gh` CLI is logged into a different GitHub account.** `gh pr create` from here would act
  as that account. Either push with plain `git` and open PRs in the browser as Manan0802, or ask
  Manan before switching `gh` accounts.
- **If a push is refused or goes out under the wrong name,** it's almost always an account mix-up,
  so don't retry blindly. One possible cause: macOS also has a system-wide Keychain credential
  helper, which is asked first and may hold a different GitHub login.

### 9.4 YouTube upload: one-time OAuth (not set up yet)

1. In [Google Cloud Console](https://console.cloud.google.com), create a project, enable
   **YouTube Data API v3**, and create an **OAuth client ID** of type **Desktop app**.
2. Put the ID and secret into `.env` as `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET`.
3. Run `python -m scripts.youtube_auth`. A browser opens and Manan approves for the channel. The
   script appends `YOUTUBE_REFRESH_TOKEN=…` to `.env`.

How it behaves afterwards:

- **Scope is `youtube.upload` only.** The token cannot read or delete anything.
- Uploads go out **unlisted** (`YOUTUBE_PRIVACY`), are marked as synthetic media and not made for
  kids, and get `#Shorts`.
- **Known Google behaviour:** while the OAuth consent screen's publishing status is "Testing",
  refresh tokens **expire after 7 days**. Either publish the consent screen, or expect to re-run
  `youtube_auth` weekly.
- The default quota allows about **6 uploads a day**. Apply for the quota audit early; Google's
  review takes weeks.

### 9.5 Cloudflare: the review gallery (not done yet)

Free plan; no card needed, because there is no R2 storage.

```bash
cd ~/Desktop/manan/aica/web
npx wrangler login                                   # browser opens; Manan approves
npx wrangler d1 create aica-review                   # prints a database_id
#   → paste that id into web/wrangler.toml (replace PASTE_AFTER_d1_create)
npx wrangler d1 execute aica-review --remote --file schema.sql
cd .. && python -m scripts.build_gallery             # makes 720p previews into web/public/
cd web && npx wrangler pages deploy public
```

### 9.6 API keys (`.env`)

- **`.env` is a symlink to `../claude-transfer/.env`**, shared with Manan's other projects.
  Editing it changes it for all of them.
- Key names and states are in §18.3.
- **Groq:** a new key comes from console.groq.com → API Keys. Test it without printing it:
  ```bash
  set -a && . ./.env && set +a
  curl -s https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY" | head -c 200
  ```
  A list of models means it works. `Access denied` is the current dead state.
- **Gemini:** a real key comes from **aistudio.google.com → Get API key** and starts with `AIza`.
  The current value starts with `AQ.` and is not a usable key. Even a valid key gives **no free
  video**.

### 9.7 Instagram

- Posting is done by hand from the Instagram app, on the page **सन्नाटा**.
- Trending audio can be attached **only** in the app.
- API posting would need a Business account, a linked Facebook Page and Meta app review (2–4
  weeks). None of that has been started.

---

## 10. How the AI assistant works on this project (operating manual)

Most of the hands-on work is done by an AI coding assistant (Claude Code, run from inside this
folder): planning, writing the stories as data, driving Flow, verifying, assembling, and keeping the
notes. Manan decides and approves. This section is the assistant's working method, written so that
a human helper, or a fresh AI session, can do the same job the same way.

### 10.1 Who does what

| Manan | The assistant |
|---|---|
| Chooses what to make (using the research), approves plans and credit spends | Researches, proposes the batch with evidence, writes stories and shot lists |
| Signs in to accounts and unlocks Flow onboarding; keeps the Jio plan active | Starts the debug browser, checks every account, drives Flow, downloads clips |
| Watches the finished videos and uploads them; picks trending audio for silent videos | Verifies every line, assembles, writes captions, reports honestly what is and isn't verified |
| Has the final word | Keeps the code, the tests, the Obsidian notes and this guide up to date |

### 10.2 Start of every session

1. **Read the notes, in this order.** Read them straight from disk: the Obsidian MCP connection
   isn't always running, but the notes are plain Markdown files.
   1. `~/Desktop/manan/manan-memory/Projects/aica.md`: index and headline status
   2. `…/Projects/aica/session-state.md`: where the last session stopped
   3. `…/Projects/aica/aica-gotchas.md`: especially the September 2026 section
   4. `…/Projects/aica/aica-handoff.md`: the full background. Its Flow-driving section is
      **pre-September** (§12 here replaces it). Its Chrome profile instructions were corrected on
      2026-10-02; §9.2 here has the full version.
   5. This guide

   The assistant also loads four short memory notes automatically, from
   `~/.claude/projects/-Users-beastathome-Desktop-manan-aica/memory/`: the two machines, the
   AI-disclosure decision, git account routing, and a pointer to the handoff.
2. **Health check** (about one minute):
   ```bash
   cd ~/Desktop/manan/aica && source .venv/bin/activate && set -a && . ./.env && set +a
   python3 -m pytest tests/ -q | tail -1                                         # 289 passed
   python3 -c "from PIL import features; print('raqm', features.check('raqm'))"  # raqm True
   git status --short                                                            # what's uncommitted
   lsof -nP -iTCP:9222 -sTCP:LISTEN                                              # debug Chrome running?
   ```
   If clips are going to be generated, also run the account check loop from §9.2.
3. **Ask Manan only what is genuinely open.** Decisions already recorded in §4 or in the notes are
   not re-asked. Reply in Hinglish, in plain words.

### 10.3 Planning a batch

- Tie every pick to evidence (§16), and write it up like `content/batch2/PLAN.md`.
- For each video, write a readable `.md` script and a data entry the tools can read (the
  `content/batch2/videos.py` shape).
- A continuing series reuses its character locks **word for word** (§13.2).
- **Budget:** clips × 15 credits. Batch 2 was 27 clips = 405 credits. Check the balance in Flow
  before starting.
- Show Manan the plan before spending anything: titles, every line, end cards, and the credit
  total.

### 10.4 Spending credits: the protocol

1. **Make one canary clip first.** Before queueing a whole video, generate one clip and check:
   - it is portrait (720×1280)
   - it shows the right character
   - Whisper hears the right line

   This is how the "9:16 setting is ignored" problem cost one clip instead of a whole batch.
2. **Run the rest in the background.** The assistant's shell stops any single command after 10
   minutes, and one video takes longer than that. Run
   `bash tools/batch_generate.sh <key> 0 > /tmp/<key>.log 2>&1` as a background job. Track
   progress by counting files in `/tmp/aica_clips/<key>/` and reading the log. Don't use a `tail`
   pipe; it shows nothing until the job ends.
3. **Never retry after `approved`.** A failure after approval means the credits are spent and the
   clip may exist in Flow. Open that project in the debug window and download it by hand (§12.4,
   step 9) instead of paying again.
4. **Run one video at a time, for now.** Every run drives the same browser tab. Even after accounts
   1–4 are unlocked, true parallel generation still needs to be built: separate tabs per run, or a
   second debug Chrome on another port with its own profile copy.

### 10.5 Driving the browser: how it's done

- **The tool:** `agent-browser --cdp 9222 <command>`. The commands used are `goto <url>`,
  `eval "<javascript>"`, `keyboard inserttext "<text>"`, `press Backspace`/`Escape`, and
  `screenshot <path>`.
- **Find elements with JavaScript in the page**: by `aria-label`, by visible text, or by position
  on screen. Never reuse the numbered references from `snapshot`; they are renumbered every time.
- **Click with `element.click()`** from `eval`; on today's Angular Flow that is the only method
  that works everywhere. **Type with `keyboard inserttext`**, after focusing the box with
  JavaScript and a selection range.
- **Prove every step by a change in state:** the box emptied, the approval count rose, a URL
  changed, a file appeared (§12.5). "✓ Done" proves nothing.
- **When confused, take a screenshot and look at it:**
  `agent-browser --cdp 9222 screenshot /tmp/flow.png`, then open the image. One screenshot has
  settled questions that hours of JavaScript probing couldn't.
- **Respect Manan's browser.**
  - Never automate Manan's normal Chrome.
  - Never close or switch tabs in the debug window while Manan is using it.
  - No background poller that switches tabs. One once closed a tab Manan was working in.
- Put browser command sequences in a `.sh` file and run it with `bash`. zsh doesn't split unquoted
  variables, so `$AB goto …` breaks when typed directly.

### 10.6 When Flow changes again (expect it)

**Symptoms:**

- The driver fails at the same step every time with "0 credits spent".
- The driver exits 0 but produces no file.
- Clicks report "✓ Done" and nothing happens.

**Procedure** (this is how `flow_clip_v2.sh` was worked out in September 2026):

1. **Stop spending.** Take a screenshot of the page.
2. **Find the new controls in the page**: the prompt box, the send button (by `aria-label`), the
   approval text, the "New project" button, and the video tile. Note which framework the app uses.
   Class names like `mat-*` and `cdk-overlay-*` mean Angular; React apps look different and need
   real input events.
3. **Try click methods in this order**, and judge each one only by a change in state:
   1. `element.click()`
   2. tag the element, then `agent-browser click "#id"`
   3. real mouse input (`agent-browser mouse move/down/up`)
   4. focus, then Enter
4. **Test on one clip.** Confirm the file on disk and its dimensions.
5. **Write a new driver** (`flow_clip_v3.sh`) instead of editing v2 in place. Give the old one a
   "superseded" header, as was done for v1. Point `batch_generate.sh` at the new one, and record
   what changed in `aica-gotchas.md` and in §12.6 here.

### 10.7 Saying "ready", and reporting to Manan

- **"Ready"** means gates 1–3 passed (§15), the contact sheet was read frame by frame, and ideally
  someone watched it. Use precise words: "verified by the tools" is not the same as "watched end to
  end".
- **Report in Hinglish:**
  - what's done, with paths and lengths
  - how many credits were spent
  - what failed, and why
  - exactly what is needed from Manan
- Never hide a failure. Never call something ready on a command's word. Three past status reports
  were wrong because a screen signal was trusted, and **Manan caught all three**.

### 10.8 End of every session

1. Update `session-state.md` with the date, what's ready, what's blocked, and what's next.
2. For any new bug, add **symptom → root cause → fix** to `aica-gotchas.md`.
3. Update the status table in `aica.md` and §21 of this guide.
4. Commit code **by specific paths** and push (it goes out as Manan0802 automatically). Never
   commit videos, `.env` or the symlinks.
5. Raw clips in `/tmp/aica_clips/` disappear on reboot. Make sure everything needed is assembled,
   or copy the clips somewhere permanent.

### 10.9 The assistant's own setup in this folder

- **`.claude`** is a symlink to `~/Desktop/manan/claude-transfer/.claude`, shared by all of Manan's
  projects. It holds the project `CLAUDE.md`, hooks, a tool "router", rules, skills and settings.
- **On every prompt, a hook runs the router** and adds a "TOOL-FIRST PROTOCOL" block listing skills
  and tools that might fit the task. Treat them as suggestions, not orders.
- **Global coding rules** live in `~/.claude/CLAUDE.md`:
  - think before coding
  - choose the simplest solution
  - change only what's needed
  - verify against a clear goal
  - after any change, explain it in plain language: what changed, which files, what broke, and a
    one-line summary
- **Auto-memory:** `~/.claude/projects/-Users-beastathome-Desktop-manan-aica/memory/` (index:
  `MEMORY.md`).
- **Notes vault:** `~/Desktop/manan/manan-memory/` (Obsidian). Plain Markdown, so it can be read
  and edited directly.
- **For OpenAI Codex**, if it's used here: `AGENTS.md`, `.codex/config.toml`, and
  `.agents/skills/manan-arsenal` (a symlink to Manan's shared tool catalogue).
- **Shell limits:** a command stops after 10 minutes, so long jobs run in the background.

### 10.10 The "never" list

- Never type or store a password. Manan signs in.
- Never click "Always approve" in Flow.
- Never retry a generation after it was approved.
- Never send two prompts in one Flow project.
- Never trust Flow's screen over a file on disk.
- Never add music to a Veo-dialogue video. Never "fix" a silent music-mode video.
- Never call a video ready without the gates in §15.
- Never automate Manan's normal Chrome or switch tabs while Manan is using the debug window.
- Never `git add -A`. Never commit `.env`, `.claude`, `.mcp.json`, `.DS_Store` or videos.
- Never print secrets (`.env`, `~/.git-credentials-manan`) into a log, a note, or this guide.
- Never delete `~/.aica-chrome`: it is currently the only place all five accounts are together.

---

## 11. Runbook: how to make a new video today

This is Pipeline B, from nothing to an uploaded video. It assumes the Mac.

### Step 0: environment (every new terminal)

```bash
cd ~/Desktop/manan/aica
source .venv/bin/activate          # background commands lose this; chain it every time
set -a && . ./.env && set +a       # zsh needs ./.env, and set -a so Python sees the variables
python3 -m pytest tests/ -q        # expect 289 passed (~40s)
```

### Step 1: start the controllable Chrome and check the accounts

All of this is covered in depth in **§9.2**. The short version:

1. **Reuse the existing debug folder `~/.aica-chrome`. Do not re-copy a Chrome profile.** Chrome's
   profiles were rearranged after 2026-08-08, so the old "copy `Profile 1`" instruction now
   copies the work account. The debug folder is currently the only place all five AI Pro accounts
   are together.

   ```bash
   if lsof -nP -iTCP:9222 -sTCP:LISTEN >/dev/null; then echo "already running"; else
     "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
       --user-data-dir="$HOME/.aica-chrome" --remote-debugging-port=9222 --no-first-run >/dev/null 2>&1 &
   fi
   ```

2. **Run the account check loop** from §9.2. You want `newProject:true` and `overlay:0` for the
   account you'll use. Today that is `authuser=0`; 1–4 are still behind onboarding.
3. Signed out? Follow "Re-copying" in §9.2. **Never type a password from a script.** Manan signs in
   by hand.

### Step 2: write the video as data

Add a new entry to `content/batch2/videos.py`, or copy that file for a new batch. Copy the shape of
an existing entry:

- `title`, `emoji` (the hook emoji must fit the genre: 😱 suits horror and would undercut a drama),
  `hook`, `hashtags` (5 at most), `niche`, `slug`
- `part` and `total_parts` (use `0, 0` for a standalone), `lang` (`"Haryanvi"` / `"Hindi"`)
- `set`: the location lock, in English
- `cast`: one **verbatim** character lock per character id. **Copy existing locks exactly**; a
  reworded lock is how a cast starts to drift.
- `outro`: `(top line, bottom line)` for the end card. The bottom line is `""` for standalones.
- `shots`: one per line, each with `lock`, `line` (the dialogue in Devanagari dialect), `action`
  (English body language, usually ending in `NOT smiling` unless smiling is the point), and
  optionally `pronoun` (`"She"`).

Also write a readable `.md` next to it, like `v1_dosti_part2.md`. Follow the prompt rules in §13.

### Step 3: generate the clips

```bash
bash tools/batch_generate.sh <key> 0        # e.g. v6 on authuser 0 → /tmp/aica_clips/v6/c1.mp4 …
# or one clip by hand:
bash tools/flow_clip_v2.sh 0 "<full prompt>" /tmp/aica_clips/v6/c1.mp4
```

- About 2 minutes and **15 credits** per clip.
- What the output lines mean:
  - `sent`: the prompt left the box.
  - `cost: 15 credits`: Flow asked for approval.
  - `approved`: credits are now spent.
  - `clip ready`, then `saved … (720x1280)`: the clip is on disk.
- **`WARNING: … is not portrait`** means the clip came back landscape. The orientation line in the
  prompt was ignored. Stop and check before generating the rest.
- **`FAIL … 0 credits spent`** is safe to retry.
- A failure **after** `approved` means credits are already gone and the clip may exist inside Flow.
  Don't regenerate blindly; look in Flow first.

⚠ `/tmp/aica_clips/` is **wiped on reboot**. Assemble before you restart, or copy the clips
somewhere permanent. (The raw clips of batch 2 are already gone; only the finished videos remain.)

### Step 4: verify, assemble and publish

```bash
python3 tools/assemble_batch2.py <key>
```

For every clip it prints what was **written** and what was **heard**. If any word looks
substituted, it prints `REFUSING TO ASSEMBLE` and stops.

- **Read each pair yourself.**
  - If the difference is only Whisper's spelling of dialect (गाड्डी→गाड़ी, सै→है), re-run with
    `ALLOW_MISREAD=1`.
  - If Veo actually said a different word (पाछै→"अच्छे"), **rewrite the line and regenerate that
    one clip**.
- On success the video is in `library/<niche>/<slug>/part_NN/`.

### Step 5: verify the finished file

```bash
python3 tools/verify_final.py <key>
```

It must end with `VERIFIED — upload ready`. Then **open the contact sheet**
(`/tmp/<key>_sheet.jpg`) and read every frame against its line: right character, right emotion,
right setting.

### Step 6: watch it yourself

Play `final.mp4` from start to finish, with sound, on a phone if possible. No automated check
replaces this, and it is the gap still open on every current video.

### Step 7: upload (manual)

- **Instagram:**
  - Upload `final.mp4` with the text of `caption.txt`.
  - For a **silent** video, choose a trending sound in the app. For crime and thriller, the genre's
    signature devotional track ("कर्म की कोख ही जनम का द्वार है…") is worth searching for.
  - For a **dialogue** video, add **no** music.
- **YouTube Shorts:** use `youtube_caption` from `meta.json` (it adds `#Shorts`). Auto-upload works
  only after the OAuth setup:
  1. In Google Cloud, create an OAuth **Desktop** client with YouTube Data API v3 enabled.
  2. Put its id and secret into `.env`.
  3. Run `python -m scripts.youtube_auth`.

  Apply for a quota audit early: the default quota allows about 6 uploads a day. Full details,
  including the 7-day token expiry trap, are in §9.4.
- **Post parts in order.** The caption on Part N points at Part N-1, which must already be on the
  profile.
- Flow's small sparkle watermark (bottom-right) is **left in on purpose**. It shows where the video
  came from, and covering it isn't ours to do.

### Step 8: commit the code (never the videos)

- `git add` **specific paths** only. A broad `git add -A` once deleted the reference images.
- Push with the **Manan0802** account.
- `library/` and `outputs/` are ignored on purpose (they're large).

---

## 12. Google Flow: everything you need to know

### 12.1 Why it's free: the subscription and the accounts

- **Jio × Google AI Pro**: worth ₹35,100, **free for 18 months**, as long as an active Jio 5G plan
  of **₹349 or more** is kept the whole time. If that plan lapses, the free video goes away.
- **Five Google accounts**, all on AI Pro, all together in the debug Chrome folder `~/.aica-chrome`
  (§9.2 explains how that login works). Switch between them with `?authuser=0..4`; the new Flow
  turns this into `/u/N/`.
- **Only `authuser=0` can be used today.** Accounts 1–4 are stuck behind Flow's first-run
  onboarding screens (§12.6). Manan needs about 30 seconds per account, clicking by hand in the
  debug Chrome window. The steps are in §9.2.

### 12.2 Credits (measured inside the app, not guessed)

| Item | Value |
|---|---|
| Monthly allowance | **1,000 credits per account** |
| Daily bonus | **+50 per day**. The wording said "until Aug 31", so it may have ended. Check in the app. |
| Omni Flash, 10s, x1 output | **15 credits.** Google's documentation says 30 because it assumes 2 outputs. Keep the setting at **x1**. |
| Veo 3.1 Lite, 8s | 10 credits |
| Extend (Lite only, 8s clips only) | 10 credits. The cheapest way to longer shots; not used yet. |
| Batch 2 actual spend | 27 clips = **405 credits** |

The chat now states the price itself ("…costing 15 credits?"), and the driver prints it.

### 12.3 Other Google video pools (separate credits, mostly untested)

- **Google Vids** (`docs.google.com/videos`): has Veo 3.1 and 60-second AI avatars. It uses a
  **separate pool**: a test generation there didn't touch Flow's balance. It starts in landscape,
  so switch it to portrait. One test failed with "Something went wrong". **Not properly tested.**
- **Gemini app** "Videos" mode: also a separate pool, with no published limit. **Untested.**
- **AI Studio / Gemini API: zero free video.** It needs billing.

### 12.4 How `flow_clip_v2.sh` works, step by step

1. Opens `flow.google.com/?authuser=N` (or a project URL, if given as the 4th argument) and waits
   until the project list has loaded.
2. Closes any overlays ("Get started", "Got it", leftover dark backdrops). A leftover backdrop
   **silently swallows every click**, which is the most common way a run dies.
3. Checks that "New project" isn't covered by anything (if it is, that account's onboarding was
   never finished), clicks it, and waits for the URL to contain `project`.
4. Focuses the prompt box with JavaScript (`focus()` plus a selection range), clears it with a
   real Backspace, and types with `agent-browser keyboard inserttext`.
5. **Before spending anything**, confirms two things: the box holds at least 80 characters, and the
   send arrow (`aria-label="Start generation"`) is enabled. If either fails, it exits with
   "0 credits spent".
6. Clicks send, then confirms the box **emptied**. That is the proof the message was sent.
7. Waits up to 300 seconds for the number of "Approve" boxes to **increase**, prints the price, and
   clicks the **last** Approve. Older approvals stay on screen and must never be clicked.
8. Waits up to about 20 minutes for the clip (it usually lands in 1–2). It hovers over the grid tile (that is what makes the
   tile load a real `<video>` with a source), reads the dimensions, and warns if they aren't
   portrait.
9. Downloads it: a JavaScript `<a download>` click follows the redirects to a signed
   `googlevideo.com` URL. Then `curl` fetches it, and **it must send a browser User-Agent, a
   Referer and a `Range` header**, or it saves 0 bytes.
10. Confirms the file isn't empty.

**One clip per project, always.** Queueing several prompts in one project *looks* as if it works,
but only the first one ever produces a video. A fresh project replies in about 10 seconds.

### 12.5 The rule that matters most: Flow's screen is not the truth

Flow re-renders inconsistently, hides older clips, and shows chat thumbnails for work that never
finished. "✓ Done" from a click command means the command ran, not that the click landed. Status
reports built on those signals have been wrong more than once, and **Manan caught every one of
them**. Trust only:

- the prompt box **going empty**: the message was sent
- the number of approval boxes **going up**: a spend request exists
- a **file on disk**: a clip exists

When confused, **take a screenshot and look at it.** One screenshot once answered three questions
that hours of JavaScript probing hadn't.

### 12.6 What changed in the September 2026 Flow rebuild

| | Before (Jul–Aug) | Now (Sept 2026) |
|---|---|---|
| Address | `labs.google/fx/tools/flow` | **`flow.google.com`**. The old address redirects but **drops `?authuser`**. |
| App framework | React: `element.click()` did nothing; real mouse input through CDP was needed | **Angular: plain `element.click()` is the ONLY method that works everywhere.** Real mouse input, focus+Enter and coordinate clicks all fail **silently**. |
| Send button | a button containing "Create" | `aria-label="Start generation"` (icon `arrow_forward`) |
| Approval | `checkApprove` text | unchanged: strip spaces, take the last one |
| Aspect ratio | – | The 9:16 setting in Agent settings **is ignored**. You must write `Vertical 9:16 portrait video, tall vertical frame.` in the prompt. |
| Settings to keep | – | Outputs **x1**; "Confirm before generating" = **Always** (that is our spend gate). **Never click "Always approve".** |
| Clip download | `<video>` on the page | the grid tile has no source until you hover over it; signed `googlevideo.com` URL; curl needs UA + Referer + Range |
| Onboarding | – | **Accounts 1–4 blocked:** a two-step dialog whose "Continue" stays disabled even after scrolling to the bottom. Needs a person. |

"New project" once *looked* rate-limited after a few uses. It wasn't; the click method was wrong.
After switching to `element.click()` it has worked every time.

---

## 13. Writing prompts for Veo, and the character locks

### 13.1 Rules (each one was proven in the product)

1. **One speaker per clip.** With two faces in frame, Veo puts the dialogue on the wrong one.
2. **The scene description is in English; only the spoken line is in Hindi or Haryanvi.** A Hindi
   scene description once produced a **puppy** for a horror scene.
3. **Start with** `Vertical 9:16 portrait video, tall vertical frame. Static camera, medium shot.`
   Veo's own motion is enough; asking for camera moves isn't needed.
4. **End with** `Do not include closed captioning or auto-generated speech subtitles.` Otherwise
   Veo burns its own captions into the picture.
5. **Paste the character lock word for word, every time.** This is what keeps the cast identical.
6. **Name the emotion and rule out the wrong one:** `NOT smiling`, `no teeth showing`. A shocked
   line once rendered as a grinning dog.
7. **Force time jumps out loud:** `BRIGHT OVERCAST DAYLIGHT, midday, no night, no darkness`.
   Otherwise the scene's dark look wins.
8. **Avoid words that have already gone wrong:**
   - `पहचाण` was spoken as "पैर पैन". Use `पहचान`.
   - `पाछै` was spoken as "अच्छे", which destroyed a horror twist. Use `पीछे`.
   - A **sentence-initial `चाय`** is read by edge-tts as "चाहे". Put any word before it.
   - The image models read British/Indian `torch`, `lift` and `lorry` differently. Write
     `flashlight`, `elevator`, `truck`.
9. **Use animal heads for recurring daylight characters.** A lion head plus a fixed outfit
   reproduces reliably; a human face drifts. Human faces are fine at **night or in fog**, where the
   drift is hidden.

The prompt that `content/batch2/videos.py → build()` actually produces:

```
Vertical 9:16 portrait video, tall vertical frame. Static camera, medium shot. <SET>. <CAST LOCK>,
<ACTION>. He is the only person in frame. He says in Haryanvi: "<LINE>" Do not include closed
captioning or auto-generated speech subtitles.
```

### 13.2 Character locks in use (copy them exactly)

| Series | Character | Lock |
|---|---|---|
| दोस्ती का हिसाब | शेरू (sheru) | `A male lion head with a full golden mane on a human body, wearing a black kurta and a thick gold chain` |
| | काळू (kaalu) | `A brown and white street dog head on a lean human body, wearing a faded blue shirt and a dhaba apron` |
| | *set* | `Inside a roadside Indian dhaba with wooden benches and Hindi signboards, warm golden afternoon light, 50mm lens` |
| खून का सौदा | कालिया (kaalia) | `A black buffalo head with thick curved horns on a heavy human body, wearing a white kurta and dark sunglasses` |
| | बिरजू (birju) | `A grey goat head with a short beard on a lean human body, wearing a torn brown shirt` |
| | *set* | `Inside a dim village room at night, a single bare bulb hanging overhead, cracked plaster walls, cold hard shadows, 35mm lens` |
| सासु का WiFi | सासु (sasu) | `An elderly grey cat head with sharp green eyes on a stout human body, wearing a maroon saree and large gold earrings` |
| | बहू (bahu) | `A young brown rabbit head with long upright ears on a slim human body, wearing a bright yellow salwar kameez` |
| तेरा हिसाब | चित्रगुप्त | `An owl head with large amber eyes on a human body, wearing deep blue robes and holding a thick open ledger` |
| | यमराज | `A black water buffalo head with enormous curved horns on a towering human body, wearing dark red robes and a heavy gold crown` |
| तीसरा हाथ | राजू | `a lean young Haryanvi man in his early twenties with very short cropped hair, clean shaven, wearing a grey hoodie` |
| | सोनू | `a stocky young Haryanvi man with a full black beard, wearing a black jacket` |
| | *set* | `on an empty village road at night, thick fog, a single motorcycle headlight, cold blue moonlight, 35mm lens` |

The sets for सासु का WiFi, तेरा हिसाब and घर का वो कोना, and the cast of घर का वो कोना, are in
`content/batch2/videos.py`. The तीसरा हाथ locks above are the final ones, from the Obsidian
handoff. The early draft in `content/teesra_haath.md` words them slightly differently.

---

## 14. Assembly: how clips become one video

Everything is in `modules/assemble.py → build_part(clips, out_dir, part, outro_top, outro_bottom, trim=True, ends=None)`.

1. **Trim point per clip.** Flow always returns a full 10 seconds, so each clip carries about 4
   seconds of nobody speaking. That dead air was the "sluggish" feel Manan kept pointing at.
   - `assemble_batch2.py` uses **Whisper's segment end + 0.45s**, but only when that end is clearly
     shorter than the clip. When Whisper returns one segment covering the whole 0–10s, its end
     tells us nothing, so it **falls back to `speech_end()`**. Trusting Whisper there once nearly
     shipped 7.7 seconds of dead air.
   - `speech_end()` reads the clip's own loudness. Its threshold is **60% of the way from the clip's
     noise floor to its peak**, plus a 0.45s beat. Two other methods failed:
     - `silencedetect` failed because a dhaba is never quiet.
     - A fixed margin above the floor failed because dish clatter counted as speech.
     - Checked against Whisper on four clips: 5.00/5.02, 5.70/5.86, 5.80/5.80, 4.75/4.80.
   - **It fails on constant machine noise** (a motorbike engine never drops). For those clips, pass
     `ends=[…]` explicitly.
   - Result: batch 2 lost **112.9 seconds** of dead air in total.
2. **Normalise and join (`concat`).** Flow returns 720×1280 at 24fps; Reels wants 1080×1920 at
   30fps. Every clip is scaled, cropped and resampled to 1080×1920 / 30fps / 48 kHz first;
   otherwise the join stutters at every cut. Encoding: x264 CRF 20, AAC 192k, `+faststart`.
3. **"Furniture" (`add_furniture`):**
   - **PART N** badge, red, top-left. `part=0` means standalone and draws no badge.
   - **AI-Generated** label, top-right.
   - The last frame is **frozen for 2.6s and darkened**, with the end card text on top. Cutting to
     black looks cheap and kills the urge to rewatch.
   - The audio **fades out** under the end card and is padded to the full length, so the room
     sound doesn't stop dead.

**Two machine facts that will bite you:**

- **This ffmpeg has no `drawtext`** (it was built without freetype). All text is drawn as
  transparent PNGs with Pillow and laid over the video with `overlay`. Don't bring `drawtext` back.
- **Pillow must have libraqm**, or Hindi renders wrong **with no error**: `किसनै` becomes `कसिनै`.
  That once shipped on an end card. Plain `pip install Pillow` gets a version **without** raqm.
  Fix:
  ```bash
  brew install libraqm
  pip install --force-reinstall --no-binary :all: --no-cache-dir Pillow
  ```
  `tests/test_devanagari_shaping.py` fails loudly if this breaks. Today: Pillow 12.3.0, raqm True.
- The Devanagari font is the macOS system font
  `/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc`. On another OS, Pillow falls back
  to a default font, and Hindi will not render properly.

---

## 15. Quality gates: how we know a video is "ready"

The project's core habit is **assert on a real change, never on a command's "success"**. Most bugs
here were found by looking at the output, not by tests passing.

### 15.1 Gate 1: the Whisper round-trip on every source clip

- **What runs it:** `tools/verify_lines.py`, with `mlx-whisper` running `whisper-large-v3`
  locally. It used to run on Groq's hosted Whisper; that key is dead.
- **Why it exists:** Veo has spoken a different word from the written one at least twice (`पहचाण`,
  `पाछै`), and both were caught here, not by listening once.
- **How it compares:**
  - Haryanvi goes through a Hindi model, so spellings shift on every line (गाड्डी→गाड़ी, सै→है,
    बतावूँ→बताऊं). Comparing **consonant skeletons** removes those false alarms.
  - Latin words (`WiFi`) and number words (`चार हज़ार`→"4000") are exempt.
  - **None of that leniency is allowed to reach the real errors.**
    `tests/test_line_verification.py` (19 tests) keeps पहचाण→"पैर पैन", पाछै→"अच्छे",
    चाय→"चाहे", गाड्डी→कुत्ता, जमीन→मकान and रोटियाँ→गाड़ियाँ all **caught**.
- **A deliberate deletion:** a whole-line similarity fallback was written and then removed, because
  it let पाछै→"अच्छे" through. A gate that quietly passes the exact error it was built for is worse
  than no gate.
- `assemble_batch2.py` **refuses to assemble** while any clip is flagged.

### 15.2 Gate 2: trim sanity

This is the Whisper-end vs `speech_end()` rule in §14. Each clip's numbers are stored in
`meta.json → verification`: `speech_end`, `trim_to`, `raw`.

### 15.3 Gate 3: `tools/verify_final.py` on the finished file

1. **Format:** 1080×1920, 30fps.
2. **Audio length vs video length**, within 0.5s. "No audio track" is reported as correct only for
   a music-mode video.
3. **`ffmpeg -f null -`**: no decode errors.
4. **Picture and sound together.** The final is sliced at every cut, **re-encoded** (never
   `-c copy`: that drops the audio before the first keyframe and invents failures), and each slice
   is transcribed. Each slice must resemble **its own line more than any other line**. That catches
   a swapped, duplicated or mis-trimmed segment, without failing on a short opening word that
   Whisper sometimes drops in short windows.
5. **Contact sheet:** one frame per shot plus the end card, in `/tmp/<key>_sheet.jpg`. A person
   reads every frame against its line. This habit caught the burning torch, the empty room, the
   dark screen and the grinning dog.

### 15.4 Gate 4: a person watches it

**Still not done for any current video.** Until it is, call them "verified by tooling", not
"watched".

---

## 16. Content strategy: what we make and why

Everything here comes from **47 reels measured live** across four research rounds (Jul 20–31). The
details are in the Obsidian notes `aica-reels-research` and `aica-format-rules`, and in
`docs/superpowers/specs/`.

### 16.1 Findings that change how you think

1. **Followers barely matter.** @solve_thispuzzle went from **488 followers to 16.1M views**. A new
   faceless account is not at a disadvantage; format quality does the work.
2. **Serials compound.** Later parts beat Part 1: a crime serial's Part 4 got **8× more comments**
   than its Part 1. @official_sheru_empire doubled from 46K to 98K in about 8 days on serials.
3. **The two biggest narrated reels put no text on screen**, just a Part badge. Captions over
   speech read as amateur. When text *is* the only channel, **speech bubbles beat a banner by
   about 6×**.
4. **Craft beats topic, by a lot.** The identical child-Hanuman story ran at 6.6M, 612K, 297K,
   31.6K and **1,460** views across five accounts.
5. **The enemy is the template, not the AI.** YouTube's 2025 "inauthentic content" rule bars
   templated mass production, not AI itself. AI faceless content can be monetised.

### 16.2 Where the opportunity is (verified)

| Opportunity | Evidence | Our video |
|---|---|---|
| **Haryanvi AI comedy** (the biggest gap) | 426K reels of demand, top posts at 34M views; the best AI competitor post had **4 likes**. We can do Haryanvi lip sync; they can't. | सासु का WiFi |
| **Animal-as-human drama** | @official_sheru_empire 98K; @BandarApnaDost 3.97M subscribers | दोस्ती का हिसाब |
| **Photoreal animal × crime serial** | No one was found combining these two | खून का सौदा |
| **Bhakti-adjacent horror** (a verdict on the viewer) | The reverent version flopped (6 likes); numbered episodes collapse (Ep-16 got 416 likes vs Ep-8's 251K views) | तेरा हिसाब |
| **Vastu as fear** | @unhealthy_ai: 293K followers, **43M views**, only 20 YouTube subscribers | घर का वो कोना |
| Talking organs or food, serialised | @fact_health__ai: Part 59 got 87.4K likes; one reel did 8.6M views | not built yet |
| Riddle / paheli | 11% comment-to-like ratio | not built yet |

**Not built yet (ideas from the research):** organs testifying in Yamraj's court; a riddle at the
end of Part 1 whose answer is Part 2; Ghibli-style 90s nostalgia as a serial; Haryanvi versions of
any proven Hindi format.

### 16.3 Rules for bhakti and mythology (why the first attempt flopped)

1. **Deliver a verdict on the viewer's life**, not information about the past ("you left food on
   your plate, here is your punishment").
2. **Never number the episodes.**
3. The winning genre is **bhakti-adjacent horror**, not reverent devotion.

### 16.4 Don't build

- AI news anchors (legal exposure in India).
- Depictions of the Sikh Gurus or Sahibzade.
- Bhojpuri AI *stories*: all 18 accounts studied were under 10K views. Bhojpuri *music* works.
- Temple mysteries (they need real footage).
- Anything using real cricket footage (copyright).
- Shock sexual-crime headlines: the worst performer of all those measured, and outside Manan's
  rules anyway.

---

## 17. Format and caption rules built into the code

| Area | Rule | Where it lives |
|---|---|---|
| Audio mode | `drama_50s` and `joke_10s` are **narrated**; `serial_75s` and `montage_35s` are **music**. The audio mode decides voice, on-screen text and timing. | `modules/formats.py` |
| On-screen text | Narrated → **none**. Music → banner (or bubble). Unknown format → banner. | `agents/composition_writer.py → text_mode_for` |
| Timing | Narrated: the **measured** speech length + 0.25s. Music: `0.8s + words/2.6`, between 2.2s and 4.5s. The LLM's own estimate was always 0.55–0.64s off. | `agents/voiceover.py`, `modules/timing.py` |
| Image prompts | English only; describe the shot (subject, action, setting, time, framing); vary the framing between scenes | `prompts/script_prompts.py` |
| Style lock | Grade, lens and grain **only, never a place**. Guarded by `tests/test_style_lock.py`, which uses word boundaries so "g**rain**" doesn't trip it. | `modules/style.py` |
| Hook | A question, a bold claim, or starting mid-action. Never scene-setting. | prompts |
| Cliffhanger | Inside the **last spoken line**, not only in the caption | prompts |
| Dialect | Written as real dialect: `मन्ने`, `कोन्या`, `घणी`, `तेरे गैल` | prompts |
| Hashtags | Instagram: **5 at most**, specific beats big (`#hindikahani` > `#viral`). `#Shorts` on **YouTube only**. | `modules/caption.py` |
| Caption asks | Follow, share with 3 friends, comment a keyword. Stacking asks drove one account to **more comments than likes**. | `modules/caption.py` |
| Part pointers | Point at the **previous** part (already posted). **A finale or standalone must not promise a next part.** | `modules/caption.py` (+ test) |
| Composition | Crossfades, a different camera move per scene, a hard text kill at each clip boundary, the AI badge starting after the disclosure card | `composition_writer.py` |
| Voices (edge-tts) | Only 2 Hindi voices exist; 8 character ids are told apart by **rate and pitch**. edge-tts has no real SSML, so there are no emotion controls. | `integrations/edge_tts_client.py` |
| Open question | All the reference reels write **Roman Hinglish** on screen; ours uses Devanagari. Never tested which works better. | – |

---

## 18. Environment, setup and keys

### 18.1 Machine

| Thing | Value (checked 2026-10-02 on the Mac) |
|---|---|
| OS / hardware | macOS, Apple M3 Pro, 18 GB |
| Python | **3.12** in `.venv`. Python 3.14 breaks the pinned `pydantic-core`; the venv uses `/opt/homebrew/bin/python3.12`. |
| Tests | `289 passed` |
| Pillow | 12.3.0, **raqm True** |
| mlx-whisper | installed in the venv |
| ffmpeg | installed, **no `drawtext` filter** |
| Node.js | v26 (HyperFrames needs ≥ 22) |
| agent-browser | 0.26.0 at `/opt/homebrew/bin/agent-browser` |
| Debug Chrome profile | `~/.aica-chrome`: holds all five AI Pro accounts, last used 2026-09-05 (§9.2) |

### 18.2 Setting up from scratch

```bash
cd ~/Desktop/manan/aica
/opt/homebrew/bin/python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
brew install libraqm ffmpeg
pip install --force-reinstall --no-binary :all: --no-cache-dir Pillow   # Devanagari shaping
pip install mlx-whisper numpy                                            # Flow path; not in requirements.txt
npm i -g agent-browser                                                   # Flow driver
python3 -m pytest tests/ -q
```

⚠ **`requirements.txt` is incomplete and partly misleading** for the current workflow:

- It pins `Pillow==11.0.0` as a wheel, which has **no raqm**.
- It doesn't list `mlx-whisper` or `numpy`, which `assemble.py` imports directly.

A fresh install that skips the extra steps above will run, and then render broken Hindi or fail at
verification.

### 18.3 Keys and settings (`.env`, git-ignored; names only, never values)

| Variable | Used for | State on 2026-10-02 |
|---|---|---|
| `GROQ_API_KEY` | Pipeline A's idea and script LLM (and Whisper, formerly) | Set, but **dead** (`Access denied`). A new key is needed only to run Pipeline A again. |
| `GEMINI_API_KEY` | Gemini images and TTS | Set, but **invalid** (starts `AQ.`; real ones start `AIza`, from aistudio.google.com) |
| `FAL_KEY` | fal.ai paid images | Empty |
| `YOUTUBE_CLIENT_ID` / `_SECRET` / `_REFRESH_TOKEN` | Auto-upload | Empty, so upload is skipped |
| `IMAGE_PROVIDER` | `pollinations` / `fal` / `gemini` | `pollinations` (`config.py` defaults to `fal` if unset) |
| `TTS_PROVIDER` | `edge` / `kokoro` / `gemini` | `edge` |
| `BGM_MODE` | `silent` (default) / `baked` | Unset = **silent**, which is intended. Leave it. |
| `YOUTUBE_PRIVACY`, `PUBLISH_PLATFORM`, `DEFAULT_FORMAT`, `MUSIC_DIR`, `CHARACTER_REF_IMAGE_URL` | Defaults in `config.py` | – |

**Google Flow needs no key.** It runs through the signed-in browser, which is why it's free.

Other keys in the same `.env` (GitHub, Notion, Firecrawl, Supabase…) belong to Manan's wider
tooling, not to aica. `.env` is a symlink to `../claude-transfer/.env`.

### 18.4 Shell traps

- zsh does **not** split unquoted variables, so `$AB goto …` breaks. Put browser commands in a
  `.sh` file and run it with `bash` (all the tools already do this).
- `. .env` fails in zsh; use `. ./.env`, with `set -a` before it.
- Background commands lose the venv; chain `source .venv/bin/activate` in the same command.
- Piping a long background job through `tail` hides all output until it ends.
- `/tmp` is wiped on reboot (raw clips, contact sheets, the old Chrome profile).

---

## 19. Tests

```bash
source .venv/bin/activate && python3 -m pytest tests/ -q      # 289 passed, ~40s
```

- **No test touches the network or runs real tools.** Groq, image services, HyperFrames, YouTube
  and ffmpeg calls all go through wrappers that the tests replace with fakes.
- One trap: patching `os.path.exists` globally breaks `os.makedirs`, so `agents/render.py` exposes
  `_exists` and `_getsize` for tests to patch instead.
- Tests that guard real past failures:

| Test file | What it protects |
|---|---|
| `test_devanagari_shaping.py` | Pillow has raqm, so `किसनै` doesn't come out as `कसिनै` |
| `test_line_verification.py` | The Whisper gate still catches every real misread we've seen (19 tests) |
| `test_style_lock.py` | No genre look names a location |
| `test_caption.py` | ≤5 Instagram hashtags, `#Shorts` YouTube-only, a finale or standalone never promises a next part |
| `test_prompt_terms.py` | torch→flashlight and friends |
| `test_assemble.py` | Trim, join and furniture command construction |
| `test_audio_sync.py`, `test_music_mode_timing.py` | Scenes timed from real audio or reading speed |
| `test_graph.py`, `test_runner.py`, `test_series_runner.py` | Pipeline A wiring, approval gates, series chaining |

Testing a change end to end means producing a real video and putting it through §15. Passing
tests are necessary, but not enough.

---

## 20. Known traps, condensed

**Flow / browser**
- The old `flow_clip.sh` exits 0 and produces nothing on today's Flow. Use `flow_clip_v2.sh`.
- Leftover overlay backdrops swallow clicks silently. The script clears them; if a run dies early,
  suspect this first.
- Always click the **last** Approve; old ones stay on screen.
- Don't count clips by accessibility role or by image alt text. Count by geometry: grid tiles sit
  left of x≈1300, chat thumbnails sit right of it.
- Flow's chat agent can stall under load ("queued… high demand"). A short follow-up message nudges
  it, or use another account; each account's queue is separate.
- Don't run a tab-switching poller while someone else is using the browser.

**Audio / voice**
- Veo dialogue videos: no music on top. Music-mode videos: silent on purpose.
- edge-tts reads a sentence-initial `चाय` as "चाहे".
- Kokoro is an English model (the Hindi accent is wrong) and exits 0 even when it fails, so check
  that the file exists.

**Pictures**
- English prompts only; a Hindi prompt returned a puppy.
- A style lock that names a place puts every scene in that place.
- "torch" means a burning stick to the image model.
- Pollinations seeds give you either consistency *or* variety, never both. Use animal heads
  instead.

**Rendering (Pipeline A / HyperFrames)**
- An empty GSAP timeline fails `hyperframes check` (`sweep_static`).
- A text fade ending on a clip boundary needs a matching `tl.set` (`gsap_exit_missing_hard_kill`).
- The AI badge must start after the full-screen disclosure card (`content_overlap`).
- The CLI has no `--cwd`, `validate` is deprecated in favour of `check`, and render takes
  `--quality X --output Y`.
- Hindi URLs used as cache filenames hit `ENAMETOOLONG`, so images are downloaded to `scene_N.jpg`.

**Verification**
- Never slice with `-c copy` when verifying.
- Whisper's segment end equal to the clip length means "unknown"; measure the audio instead.

**Git**
- Never `git add -A`. Push as Manan0802. Never commit `.env`, `.claude`, `.mcp.json` or `.DS_Store`.

---

## 21. Current status as of 2026-10-02

### ✅ Done

- **10 finished videos** in `library/`: 2 posted, **8 upload-ready** (§8), all through the tooling
  checks in §15.1–15.3.
- Pipeline B works end to end on `authuser=0` with the September 2026 Flow.
- The Whisper gate runs locally (no Groq dependency).
- 289 tests pass.

### 💾 Git and backups

On 2026-10-02 the batch-2 tool chain and this guide were committed and pushed to GitHub as
Manan0802, then merged into **`main`**. That work includes:

- `content/batch2/`
- `tools/flow_clip_v2.sh`, `batch_generate.sh`, `batch_all.sh`, `run_batch2.sh`,
  `verify_lines.py`, `verify_final.py`, `assemble_batch2.py`
- `tests/test_line_verification.py`
- the warning header in `tools/flow_clip.sh`
- this guide

Left out of git on purpose:

- `AGENTS.md`, `.agents/`, `.codex/`: Manan's Codex tool configuration, not app code
- `logs/`: machine logs

Separately, **`library/` has no backup at all.** It is git-ignored and lives only on this Mac.

**Login risk:** Chrome's profiles were rearranged after 2026-08-08. The debug folder
`~/.aica-chrome` is now the only place all five AI Pro accounts are signed in together. If it is
deleted, or if its session expires, Manan has to add the missing accounts to a normal Chrome
profile before it can be copied again (§9.2).

### 🔴 Blocked on Manan

1. **Unlock Flow accounts 1–4.** In the debug Chrome window, open `flow.google.com/?authuser=N` and
   click through the onboarding by hand, about 30 seconds each (exact steps in §9.2). This makes
   4× the daily clips available. Running them truly in parallel still needs building (§10.4).
2. **A new Groq key**, only if Pipeline A's script writing is wanted again.
3. **A valid Gemini key** (`AIza…`) from aistudio.google.com, only if Gemini images or TTS are
   wanted.
4. **Deploy the review gallery:** `cd web && npx wrangler d1 create aica-review`, paste the printed
   id into `web/wrangler.toml`, then run
   `npx wrangler d1 execute aica-review --remote --file schema.sql` and
   `npx wrangler pages deploy public`.
5. **Keep the Jio 5G plan (₹349 or more) active**, or Flow stops being free.

### ⏭ Open / next

- [ ] Someone **watches all 8 ready videos end to end** in a player, then they get posted in order.
- [ ] **दोस्ती का हिसाब Part 3** (the end card already asks `के शेरू वा चाबी लेगा?`) and
      **खून का सौदा Part 2** (`कालिया नै कौण सा नाम लिया?`). Don't stop at 3 parts.
- [ ] Rebuild **आख़री कॉल Part 1** (it predates the `torch`→`flashlight` fix).
- [ ] Test **Google Vids** (portrait, using "Ingredients" for the character lock) and the
      **Gemini app's** video mode. Both are untapped, separate credit pools.
- [ ] Try **Veo 3.1 Lite + Extend** (10 credits per 8s) for longer shots.
- [ ] Research **YouTube Shorts** specifically; all current data is from Instagram.
- [ ] Test **Roman Hinglish vs Devanagari** for on-screen text.
- [ ] Not built from the original plan: a scheduler, Instagram API publishing (needs a Business
      account plus Meta review), WhatsApp approvals, and an analytics feedback loop.

---

## 22. Where to read more

| Source | What's there |
|---|---|
| Obsidian: `~/Desktop/manan/manan-memory/Projects/aica.md` | Index and headline status |
| Obsidian: `Projects/aica/aica-handoff.md` | The full A–Z handoff (accounts, credits, Flow driving, prompts, assembly). Its Flow-driving section is **pre-September** (the gotchas note has the update). Its Chrome profile instructions were **corrected on 2026-10-02** (§9.2 has the full version). |
| Obsidian: `Projects/aica/session-state.md` | Where things stood on 2026-09-05 |
| Obsidian: `Projects/aica/aica-gotchas.md` | Every bug, with its root cause and fix, including the September Flow rebuild |
| Obsidian: `Projects/aica/aica-reels-research.md` | 47 reels, 26 domains, 5 unclaimed combinations |
| Obsidian: `Projects/aica/aica-format-rules.md` | The format rules and the evidence for each |
| Obsidian: `Projects/aica/aica-tools-research.md` | Every tool evaluated (video, TTS, images, Google capacity, hosting) and why it was picked or rejected |
| `docs/superpowers/specs/` and `plans/` | The original design, phase plans and research write-ups |
| `AI_Content_Creation_PRD.md` | The original long-range vision |
| The code comments | Unusually thorough. Most functions explain *why* they exist and which failure they prevent. |

---

## 23. FAQ for newcomers

**Is anything uploaded automatically?**
No. Manan uploads by hand. YouTube upload code exists, but it is switched off because no
credentials are set.

**Why not use the automatic pipeline (A) for everything?**
Its script LLM key is dead, and still images with zoom effects look weak next to real Veo video.
Pipeline B produces much better videos at the same cost (₹0).

**Why animal heads?**
They keep characters looking the same from clip to clip (human faces drift), and that look is a
proven, popular genre in India.

**Why are some videos silent?**
On purpose. Trending audio helps a reel get shown, and it can only be added inside the Instagram
app. Videos with Veo dialogue are the opposite: never add music to those.

**Why does each clip need its own Flow project?**
Within one project, only the first prompt ever produces a video. The rest are accepted and then
never run.

**A script says "✓ Done", but nothing happened. Why?**
On this app, "✓ Done" means the command ran, not that it worked. Check for a real change instead:
the prompt box emptied, the approval count went up, or a file appeared on disk. Take a screenshot.

**How does the login work? Does a script type passwords?**
No script ever types a password. The five Google accounts are signed in inside a separate Chrome
data folder (`~/.aica-chrome`), made by copying a normal Chrome profile's session files. That Chrome
runs with a debug port the scripts can control. Every login is explained in §9.

**What should a new helper do first?**
Read §0–§10, then follow the start-of-session routine in §10.2 before touching anything.

**How much does a video cost?**
About 5–6 clips × 15 credits = 75–90 Flow credits, which come free with the subscription. Nothing
else costs money.

**Can I run this on Windows?**
Pipeline A mostly yes; the original spec was written for a Windows laptop. Pipeline B is
Mac-specific today: `mlx-whisper`, the macOS Devanagari font path, Chrome profile paths and
`stat -f%z`.

**I changed something. How do I know I didn't break it?**
Run the tests (289 should pass). If you touched anything that produces video, also make one real
video and run it through §15.

**Who decides what content to make?**
Manan, guided by the research in §16. Stay inside the rules in §4.
