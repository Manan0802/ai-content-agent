# 📄 PRD — AI Content Creation System
**Version:** 1.0  
**Author:** Manan  
**Status:** Pre-Build / Research Phase  
**Last Updated:** June 2026  

---

## 📌 TABLE OF CONTENTS

1. [Project Vision & Overview](#1-project-vision--overview)
2. [Business Model & Monetization](#2-business-model--monetization)
3. [System Architecture (Full Pipeline)](#3-system-architecture-full-pipeline)
4. [Module-by-Module Specification](#4-module-by-module-specification)
   - 4.1 Orchestrator (LangGraph Brain)
   - 4.2 Idea & Topic Generator Agent
   - 4.3 Script Writer Agent
   - 4.4 Voiceover Agent
   - 4.5 Visual / Image Generator Agent
   - 4.6 Character Consistency Module
   - 4.7 Video Assembly Agent
   - 4.8 Subtitle & Edit Agent
   - 4.9 Upload Agent
   - 4.10 Human-in-the-Loop (HITL) Layer
   - 4.11 Analytics & Feedback Agent
5. [Character Design System](#5-character-design-system)
6. [Tech Stack (Free vs Paid)](#6-tech-stack-free-vs-paid)
7. [Data Flow & State Management](#7-data-flow--state-management)
8. [Infrastructure & Storage](#8-infrastructure--storage)
9. [File & Folder Structure](#9-file--folder-structure)
10. [Phase-wise Build Plan](#10-phase-wise-build-plan)
11. [Open Source Tools & MCPs to Research](#11-open-source-tools--mcps-to-research)
12. [Success Metrics & KPIs](#12-success-metrics--kpis)
13. [Known Constraints & Risks](#13-known-constraints--risks)
14. [Open Decisions (Pre-Build)](#14-open-decisions-pre-build)

---

## 1. PROJECT VISION & OVERVIEW

### Tagline
> "Fully automated AI video production pipeline — idea se upload tak, bina manual kaam ke."

### What We're Building
A **multi-agent AI system** that autonomously generates, produces, and publishes short-form and long-form video content to YouTube and Instagram. The system supports:

- **Niche:** Multi-topic (Horror, Tech/AI, Finance, Motivation, Mythology, Comedy, Viral/Trending)
- **Languages:** Hinglish primary; English/Hindi flexible per content type
- **Formats:** YouTube Shorts (30-60s) + Long-form (8-15 min) + Instagram Reels
- **Character:** Mixed — anime-style mascot for branded series + faceless for general content
- **Automation Level:** Flexible — can run fully autonomous OR with human approval checkpoints

### Core Philosophy
- **Free-first stack** → upgrade tools only after revenue starts
- **Passive income** → system runs without daily intervention
- **Flexible HITL** → human approves where quality matters most
- **Future-proof** → system can be freelanced to clients later

### Who Uses This System
- **Phase 1:** Manan — personal passive income channel
- **Phase 2:** Freelance offering — build for clients
- **Phase 3 (optional):** Productize as SaaS

---

## 2. BUSINESS MODEL & MONETIZATION

### Revenue Streams

#### Stream 1: YouTube AdSense
- **Unlock condition:** 1,000 subscribers + 4,000 watch hours (long-form) OR 10M Shorts views in 90 days
- **Expected timeline:** 3-6 months of consistent daily posting
- **Estimated CPM (India):** ₹50-150 per 1000 views (Hindi content)
- **Estimated CPM (Global/English):** ₹300-800 per 1000 views

#### Stream 2: Instagram Reels Bonus
- **Unlock condition:** Meta Reels Play Bonus program (invite-based, 10K+ followers)
- **Expected:** ₹0.01-0.05 per reel view (variable)

#### Stream 3: Affiliate Marketing
- **Method:** Product links in video descriptions / pinned comments
- **Best niches:** Finance tools, Tech products, Online courses
- **Expected:** ₹500-5000/month early stage; scales with audience

#### Stream 4: Sponsorships / Brand Deals
- **Unlocks at:** ~10K-50K subscribers
- **Expected rate:** ₹5,000-50,000/video depending on niche + audience

#### Stream 5: Freelance (Future)
- **Offer:** "AI video production system" for brands/creators
- **Price point:** ₹10,000-50,000/month per client
- **Leverage:** Same system, different content/branding

### Monetization Timeline (Realistic)
```
Month 1-2  → Build system, start posting, ₹0 income
Month 3-4  → Growing channel, affiliate links active, ₹500-2000/month
Month 5-6  → AdSense unlocked, ₹2000-8000/month
Month 6+   → Sponsors + AdSense + Affiliate, ₹10,000+/month (target)
```

### Budget Plan
- **Starting:** ₹500-1000/month
- **Allocation:**
  - Voiceover (ElevenLabs starter): ~₹400/month
  - Video generation credits (Kling/Pika): ~₹400/month
  - Remaining for misc APIs
- **Upgrade trigger:** Once revenue > ₹3,000/month

---

## 3. SYSTEM ARCHITECTURE (FULL PIPELINE)

### High-Level Pipeline
```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (LangGraph)                      │
│              Main brain — routes between all agents              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │     IDEA / TOPIC AGENT            │
         │  (trending + niche research)      │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │  [HITL CHECKPOINT 1 — Optional]   │
         │     Human approves topic          │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │       SCRIPT WRITER AGENT         │
         │  (niche-aware, tone-aware)        │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │  [HITL CHECKPOINT 2 — Optional]   │
         │     Human reviews script          │
         └────────────────┬─────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
 ┌────────────▼──────────┐ ┌──────────▼──────────────┐
 │   VOICEOVER AGENT     │ │  VISUAL / IMAGE AGENT    │
 │  (TTS generation)     │ │  (scene-by-scene images) │
 └────────────┬──────────┘ └──────────┬──────────────┘
              │                       │
              │            ┌──────────▼──────────────┐
              │            │  CHARACTER CONSISTENCY   │
              │            │  MODULE (LoRA / CREF)    │
              │            └──────────┬──────────────┘
              │                       │
         ┌────▼───────────────────────▼─────┐
         │       VIDEO ASSEMBLY AGENT        │
         │  (audio + visuals → video file)   │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │    SUBTITLE & EDIT AGENT          │
         │  (captions, cuts, transitions)    │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │  [HITL CHECKPOINT 3 — Recommended]│
         │     Human reviews final video     │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │         UPLOAD AGENT              │
         │  (YouTube API + Instagram API)    │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │     ANALYTICS & FEEDBACK AGENT   │
         │  (track performance, learn)       │
         └──────────────────────────────────┘
```

### Execution Modes

| Mode | Description | Use Case |
|---|---|---|
| **Full Auto** | Idea → Upload, no human touch | Trending/faceless content |
| **Semi-Auto** | Human approves topic + final video | Branded series |
| **Script-Only Auto** | Human gives topic, AI does rest | When Manan has specific idea |
| **Manual Trigger** | Human triggers each stage | Learning / debugging phase |

---

## 4. MODULE-BY-MODULE SPECIFICATION

---

### 4.1 ORCHESTRATOR (LangGraph Brain)

**Role:** Master controller. Manages state, routes between agents, handles HITL checkpoints, error recovery.

**Framework:** LangGraph (StateGraph)

**State Schema:**
```python
class ContentState(TypedDict):
    # Meta
    job_id: str                    # Unique video job ID
    created_at: str
    status: str                    # idle | running | paused_for_human | complete | failed
    mode: str                      # full_auto | semi_auto | script_only | manual

    # Content
    topic: str
    niche: str                     # horror | tech | finance | motivation | trending
    language: str                  # hindi | english | hinglish
    format: str                    # short | long
    tone: str                      # dark | educational | motivational | funny
    has_character: bool

    # Pipeline outputs
    script: dict                   # {hook, body, cta, word_count}
    voiceover_path: str            # Local file path
    scene_prompts: list[str]       # Image gen prompts per scene
    image_paths: list[str]
    video_path: str                # Raw assembled video
    final_video_path: str          # After subtitle + edit
    thumbnail_path: str

    # Upload meta
    title: str
    description: str
    tags: list[str]
    youtube_video_id: str
    instagram_post_id: str

    # HITL
    hitl_checkpoints: list[str]    # Which checkpoints enabled
    human_approved: dict           # {topic: bool, script: bool, final: bool}

    # Analytics
    youtube_views: int
    youtube_likes: int
    insta_views: int

    # Errors
    errors: list[str]
```

**LangGraph Nodes:**
```
idea_generator → [hitl_topic?] → script_writer → [hitl_script?] 
→ [voiceover_gen | visual_gen] (parallel) → video_assembler 
→ subtitle_editor → [hitl_final?] → uploader → analytics_tracker
```

**Key Features:**
- Parallel execution for voiceover + visuals (saves time)
- Retry logic on API failures (3 retries, exponential backoff)
- Checkpoint save — resume failed jobs from last successful step
- Job queue — multiple videos can be queued

---

### 4.2 IDEA & TOPIC GENERATOR AGENT

**Role:** Decides what the next video will be about. Researches trending topics, scores viral potential.

**Inputs:** Niche list, language preference, format type, blacklist (already done topics)

**Outputs:** Top 3-5 topic suggestions with viral score, title draft, hook concept

**Process:**
1. Scrape/search trending topics from:
   - YouTube Trending API (public)
   - Google Trends (via pytrends)
   - Reddit (r/india, r/technology, r/HorrorStories, etc.)
   - Twitter/X Trends (via API)
   - NewsAPI for latest happenings
2. Filter by niche relevance
3. Score each topic: recency + engagement_potential + niche_fit + competition_level
4. Return ranked list

**LLM Prompt Strategy:**
```
System: You are a viral content strategist for a Hinglish YouTube channel covering 
[niche]. Given these trending topics: [topics_list], suggest the top 3 video ideas 
with hooks, expected audience emotion, and format recommendation (short/long).
Output JSON: {ideas: [{title, hook, format, niche, tone, viral_score}]}
```

**Tools Used:**
- `pytrends` — Google Trends
- `praw` — Reddit API
- `newsapi-python` — Latest news
- `youtube-search-python` — YouTube trending
- LLM: Groq Llama 3.3 (free) for scoring + ideation

**HITL Checkpoint 1:** Show top 3 ideas → human picks one OR approves AI pick

---

### 4.3 SCRIPT WRITER AGENT

**Role:** Takes approved topic → writes full video script, scene-by-scene, with voiceover text and visual direction.

**Inputs:** Topic, niche, tone, language, format (short/long), character presence

**Outputs:**
```json
{
  "title": "5 Dark Facts About Indian History Jo Aapko Pata Nahi",
  "hook": "...",
  "segments": [
    {
      "scene_number": 1,
      "duration_sec": 8,
      "voiceover_text": "...",
      "visual_direction": "Dark ancient fort at midnight, torches flickering",
      "character_visible": true,
      "emotion": "mysterious"
    }
  ],
  "outro_cta": "Subscribe karo agar yeh nahi pata tha...",
  "total_duration_estimate": 55,
  "word_count": 320,
  "hashtags": ["#darkfacts", "#indianhistory", "#shorts"],
  "thumbnail_concept": "Split face — half ancient warrior, half modern shocked face"
}
```

**LLM Strategy:**
- Model: Groq Llama 3.3 (primary) / Claude Sonnet (quality fallback)
- System prompt: Niche-specific persona + YouTube best practices
- Chain of thought: Hook → Body → CTA → Scene breakdown

**Script Templates by Format:**
- **Short (60s):** Hook (5s) → 3-5 facts/points (45s) → CTA (10s)
- **Long (10 min):** Hook (30s) → Intro (1 min) → 5-7 main segments (7 min) → Outro/CTA (1.5 min)

**Quality Checks:**
- Hook must be in first 3 seconds (retention)
- Word count matches duration estimate
- Visual directions are specific enough for image gen
- CTA present in every video

**HITL Checkpoint 2 (optional):** Show full script → human edits/approves

---

### 4.4 VOICEOVER AGENT

**Role:** Converts voiceover text → natural audio file

**Inputs:** Script voiceover text (per segment), language, tone/emotion, character voice

**Outputs:** `.mp3`/`.wav` file per segment + merged full audio

**Tool Options:**

| Tool | Quality | Cost | Hindi Support | Emotion Control |
|---|---|---|---|---|
| Edge-TTS | ⭐⭐⭐ | Free | ✅ | Limited |
| Coqui TTS | ⭐⭐⭐ | Free (self-host) | Partial | Good |
| ElevenLabs | ⭐⭐⭐⭐⭐ | ₹400/mo starter | ✅ | Excellent |
| Google Cloud TTS | ⭐⭐⭐⭐ | Pay-per-use | ✅ | Good |
| Sarvam AI TTS | ⭐⭐⭐⭐ | Free tier available | ✅✅ (Indian) | Good |

**Decision:**
- **Phase 1:** Edge-TTS (free) for all content
- **Phase 2:** Sarvam AI TTS for Hindi content (Indian accent, already familiar)
- **Phase 3:** ElevenLabs for premium/character voice

**Voice Profiles:**
- Character voice: Fixed consistent voice ID (ElevenLabs custom / Edge-TTS preset)
- Narrator voice: Separate profile for faceless content

**Processing:**
```
Script text → TTS API → per-segment audio → merge with pydub → normalize volume → output merged.mp3
```

**Libraries:**
- `edge-tts` (Python)
- `pydub` — audio merging + normalization
- `elevenlabs` SDK — when upgraded

---

### 4.5 VISUAL / IMAGE GENERATOR AGENT

**Role:** Takes visual_direction from each scene → generates corresponding image

**Inputs:** Scene visual direction text, character reference (if has_character=True), style/niche, emotion

**Outputs:** One image per scene, consistent style

**Tool Options:**

| Tool | Cost | Quality | Character Consistency | Speed |
|---|---|---|---|---|
| Stable Diffusion (local) | Free | ⭐⭐⭐⭐ | ✅ (with LoRA) | Depends on GPU |
| ComfyUI (local) | Free | ⭐⭐⭐⭐⭐ | ✅✅ (workflow) | Depends on GPU |
| Midjourney API | ~₹1500/mo | ⭐⭐⭐⭐⭐ | ✅ (--cref) | Fast |
| FLUX.1 (Replicate) | Pay-per-image | ⭐⭐⭐⭐⭐ | ✅ | Fast |
| Stability AI API | Pay-per-image | ⭐⭐⭐⭐ | Medium | Fast |
| Bing Image Creator | Free (limited) | ⭐⭐⭐ | Poor | Slow |

**Decision:**
- **Phase 1 (no GPU):** FLUX.1 on Replicate (pay-per-image, ~$0.003/image) OR free tier
- **Phase 1 (has GPU 4GB+):** Local AUTOMATIC1111 + anime LoRA
- **Phase 2:** ComfyUI with character consistency workflow

**Prompt Engineering:**
```
Base prompt: [visual_direction] + [style token: anime, dark, cinematic] + [quality tokens]
Negative prompt: blurry, watermark, bad anatomy, text, multiple faces
Character reference: fed as IP-Adapter input or --cref param
```

**Style Tokens by Niche:**
```python
STYLE_MAP = {
    "horror": "dark atmosphere, horror, dramatic lighting, anime style, cinematic",
    "tech": "futuristic, cyberpunk, neon lights, digital world, anime aesthetic",
    "finance": "professional, gold coins, stock charts, clean modern, anime style",
    "motivation": "sunrise, determination, epic landscape, anime protagonist",
    "mythology": "ancient india, gods, epic battle, traditional art style"
}
```

---

### 4.6 CHARACTER CONSISTENCY MODULE

**Role:** Ensures the anime character looks the same across all scenes and videos

**Character Spec (to be designed once):**
```yaml
character:
  name: "TBD by Manan"
  gender: "TBD"
  style: "Anime"
  hair: "TBD — fixed color + style"
  eyes: "TBD — fixed color"
  outfit: "TBD — signature look"
  color_palette: ["primary", "secondary", "accent"]
  expressions: ["neutral", "shocked", "smirking", "serious", "excited"]
```

**Consistency Methods (pick based on GPU):**

**Method A — LoRA Training (Best, needs GPU)**
- Train a LoRA on 20-30 character images
- Use in AUTOMATIC1111 / ComfyUI
- Same character every time, any pose/scene
- One-time effort, permanent consistency

**Method B — IP-Adapter + Reference Image (No training needed)**
- Feed character reference image + scene prompt
- ComfyUI IP-Adapter node
- 80-90% consistent, occasional drift
- Good for Phase 1

**Method C — Midjourney --cref (Easiest)**
- Character reference image + --cref URL + --cw 100
- Very consistent for same-style images
- Paid tool

**Method D — Fixed Avatar (HeyGen / D-ID)**
- Create once → lip-syncs with voiceover
- 100% face consistency
- Cost: HeyGen ~₹1200/month

**Recommendation for Phase 1:**
- If no GPU → Method D (HeyGen) for character scenes
- If GPU available → Method B (IP-Adapter) → train LoRA when established

---

### 4.7 VIDEO ASSEMBLY AGENT

**Role:** Combines audio + images → raw video file. Optionally adds motion to static images.

**Inputs:** Merged audio file, scene images, scene durations from script

**Outputs:** Raw `.mp4` video file

**Process:**
```
For each scene:
  1. Get image + voiceover audio duration
  2. Add motion (optional) — zoom in/out, pan, Ken Burns effect
  3. Sync image duration to audio segment duration
Merge all scenes → raw_video.mp4
Add background music (optional, royalty-free)
```

**Tool Options:**

| Tool | Cost | Input | Output | Motion |
|---|---|---|---|---|
| FFmpeg | Free | Images + Audio | MP4 | Basic (zoom/pan via filters) |
| MoviePy | Free | Images + Audio | MP4 | Basic |
| Kling API | Credits | Image | Video clip (5s) | AI motion ✅ |
| Runway Gen-3 | Credits | Image | Video clip | AI motion ✅ |
| Pika Labs | Credits | Image | Video clip | AI motion ✅ |

**Decision:**
- **Phase 1:** FFmpeg + MoviePy (free) — Ken Burns effect on images
- **Phase 2:** Kling/Pika free credits for key scenes
- **Phase 3:** Paid video gen for full AI motion

**FFmpeg Ken Burns (Example):**
```bash
ffmpeg -loop 1 -i scene1.png -vf "zoompan=z='min(zoom+0.001,1.5)':d=125" \
       -t 5 -pix_fmt yuv420p scene1.mp4
```

**Background Music:**
- Source: YouTube Audio Library (royalty-free) OR Pixabay Music
- Auto-select by niche mood
- Volume: 10-15% of voiceover volume

---

### 4.8 SUBTITLE & EDIT AGENT

**Role:** Generates and burns subtitles. Adds intro/outro. Applies basic edits.

**Inputs:** Raw video + audio transcript

**Outputs:** Final edited `.mp4` with subtitles

**Subtitle Generation:**
```
Audio file → Whisper (OpenAI) / faster-whisper → .srt file 
→ style subtitles (font, color, position) → burn into video via FFmpeg
```

**Subtitle Style (viral format):**
```
Font: Bold, large (Impact or similar)
Color: White text + black outline OR yellow highlight on current word
Position: Lower-center (Shorts) / Lower-third (Long)
Animation: Word-by-word highlight (captions style)
Max chars per line: 25 (Shorts), 40 (Long)
```

**Tools:**
- `faster-whisper` — fast local transcription (free)
- `FFmpeg` — subtitle burning
- `ass` subtitle format for styled captions

**Editing Steps:**
1. Add 1-2 second black fade-in at start
2. Add branded outro (5 seconds — subscribe animation)
3. Add chapter markers (long-form only)
4. Thumbnail frame extraction (best frame)

**Thumbnail Agent (Sub-module):**
- Extract best frame from video
- Add text overlay with Pillow
- Apply niche-specific filter
- Output: `thumbnail.jpg` (1280x720 for long, 1080x1920 for Shorts)

---

### 4.9 UPLOAD AGENT

**Role:** Uploads final video + metadata to YouTube and Instagram

**YouTube Upload:**

```python
# YouTube Data API v3
# Scope: youtube.upload

metadata = {
    "title": state["title"],
    "description": state["description"],  # includes affiliate links, socials
    "tags": state["tags"],
    "categoryId": niche_to_category_id[state["niche"]],
    "defaultLanguage": state["language"],
    "privacyStatus": "public"  # or "unlisted" for review mode
}

# Upload video file
# Upload thumbnail separately
# Add to playlist (optional)
```

**Instagram Upload (Graph API):**
```python
# Meta Graph API
# Type: REELS for Shorts content

# Step 1: Create media container
# Step 2: Upload video to container URL
# Step 3: Publish container
# Caption includes hashtags + CTA
```

**Upload Schedule:**
- Default: Upload immediately after approval
- Scheduled: Set publish time (peak hours — 7-9 PM IST for India)
- Drafts: Upload as draft for manual publish later

**YouTube Category Map:**
```python
CATEGORY_MAP = {
    "horror": "24",        # Entertainment
    "tech": "28",          # Science & Technology
    "finance": "22",       # People & Blogs
    "motivation": "22",    # People & Blogs
    "mythology": "27",     # Education
    "comedy": "23"         # Comedy
}
```

---

### 4.10 HUMAN-IN-THE-LOOP (HITL) LAYER

**Role:** Pause pipeline, notify human, wait for approval before continuing.

**Notification Methods:**
- Telegram Bot (PRIMARY — free, instant)
- WhatsApp (via Twilio — paid)
- Email (via SMTP — free)
- Local CLI prompt (for development)

**HITL Flow:**
```
Agent completes step → Check if HITL enabled for this checkpoint
→ YES: Send notification with preview + options
→ Wait for response (timeout: 24 hours → auto-approve or auto-cancel)
→ Human responds: APPROVE / REJECT / EDIT
→ Pipeline resumes or loops back
```

**Telegram Bot Commands:**
```
/approve_topic  — Approve suggested topic
/reject_topic   — Request new topic
/approve_script — Script looks good, continue
/edit_script    — Opens edit interface
/approve_video  — Final video approved, upload
/reject_video   — Regenerate or manual fix
/status         — Check current job status
/queue          — See upcoming video queue
```

**Preview Delivery:**
- Topic: Text message with top 3 options + scores
- Script: Text document preview
- Final video: Video file sent directly to Telegram (if <50MB) or sharing link

---

### 4.11 ANALYTICS & FEEDBACK AGENT

**Role:** Tracks performance of uploaded videos. Feeds learnings back to Idea Generator.

**Data Collected (per video):**
```python
{
    "video_id": "...",
    "niche": "horror",
    "format": "short",
    "language": "hinglish",
    "has_character": True,
    "upload_timestamp": "...",
    "youtube_metrics": {
        "views_24h": int,
        "views_7d": int,
        "likes": int,
        "comments": int,
        "avg_watch_time": float,
        "ctr": float,           # Click-through rate
        "impressions": int
    },
    "insta_metrics": {
        "plays": int,
        "likes": int,
        "shares": int,
        "saves": int
    },
    "viral_score": float        # Computed composite score
}
```

**Feedback Loop:**
- High-performing niche → prioritize more of same niche
- High-performing format → increase that format ratio
- Low CTR → A/B test different thumbnail styles
- Low retention → adjust script hook strategy

**Scheduler:**
- Check analytics: 24 hours after upload, 7 days after upload
- Generate weekly performance report (Telegram summary)

---

## 5. CHARACTER DESIGN SYSTEM

### Character Creation Pipeline (One-Time Setup)

```
Step 1: Define character visually (name, look, style)
Step 2: Generate 20-30 reference images in consistent style
Step 3: Select best 10-15 images as "canon" references
Step 4: [If GPU] Train LoRA on these images
Step 5: [If no GPU] Set up IP-Adapter workflow in ComfyUI Cloud
Step 6: Test character in 5+ different scene types
Step 7: Lock design — DO NOT change after launch
```

### Character Expressions Needed
For each expression, generate 5+ variants:
- Neutral / Presenter
- Shocked / Surprised
- Smirking / Confident
- Serious / Dark
- Excited / Happy
- Thinking / Curious

### Character Scenes Needed
- Full body (talking, standing)
- Half body (explaining)
- Close-up face (emotional moments)
- Action poses (niche-specific)
- Background variants (dark forest, tech room, ancient temple, etc.)

### Character Brand Elements
```yaml
channel_mascot:
  name: "TBD"
  tagline: "TBD"
  signature_pose: "TBD"
  signature_catchphrase: "TBD"  # For outro/CTA
  color_palette:
    primary: "#TBD"
    secondary: "#TBD"
    accent: "#TBD"
```

---

## 6. TECH STACK (FREE VS PAID)

### Core Stack

| Layer | Free Option | Paid Option | Decision |
|---|---|---|---|
| **Orchestration** | LangGraph (free) | — | LangGraph ✅ |
| **LLM (Script/Ideas)** | Groq Llama 3.3 (free) | Claude Sonnet | Groq primary, Claude fallback |
| **Voiceover** | Edge-TTS / Sarvam AI | ElevenLabs | Edge-TTS → Sarvam upgrade |
| **Image Gen** | FLUX.1 free tier / SD local | Midjourney / Replicate | Depends on GPU check |
| **Video Gen** | FFmpeg + free credits | Kling / Runway | FFmpeg + credits |
| **Subtitles** | faster-whisper + FFmpeg | — | Free stack ✅ |
| **Upload** | YouTube API + Meta Graph API | — | Free ✅ |
| **HITL Notify** | Telegram Bot API | — | Telegram ✅ |
| **Database** | SQLite / TinyDB | MongoDB Atlas | SQLite Phase 1 |
| **Storage** | Local + Google Drive | AWS S3 | Local + Drive Phase 1 |
| **Scheduling** | APScheduler / Cron | — | APScheduler ✅ |
| **Trending Research** | pytrends + praw + newsapi | — | Free ✅ |
| **Analytics Pull** | YouTube Analytics API | — | Free ✅ |

### Python Libraries Master List
```
# Orchestration
langgraph
langchain
langchain-groq

# LLM APIs
groq
anthropic

# Voiceover
edge-tts
pydub
sarvam-ai (check official SDK)

# Image Generation
diffusers (Hugging Face)
replicate (for FLUX/other models)
Pillow (image manipulation)

# Video Assembly
moviepy
ffmpeg-python

# Transcription / Subtitles
faster-whisper
pysrt (SRT file handling)

# Upload
google-api-python-client (YouTube)
requests (Meta Graph API)

# Trending Research
pytrends
praw (Reddit)
newsapi-python
youtube-search-python

# Notifications
python-telegram-bot

# Database
tinydb OR sqlite3

# Storage
google-api-python-client (Drive)

# Scheduling
apscheduler

# Utilities
python-dotenv
loguru (logging)
pydantic (state validation)
tenacity (retry logic)
```

---

## 7. DATA FLOW & STATE MANAGEMENT

### Job Lifecycle
```
NEW → IDEA_GENERATED → [HITL_TOPIC] → SCRIPT_WRITTEN → [HITL_SCRIPT]
→ PRODUCING (parallel: VOICEOVER + VISUALS) → VIDEO_ASSEMBLED 
→ SUBTITLED → [HITL_FINAL] → UPLOADING → UPLOADED → TRACKING → COMPLETE
```

### Database Schema (SQLite)

**Table: jobs**
```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    status TEXT,
    mode TEXT,
    niche TEXT,
    language TEXT,
    format TEXT,
    topic TEXT,
    title TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    youtube_url TEXT,
    insta_url TEXT,
    error_log TEXT
);
```

**Table: analytics**
```sql
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY,
    job_id TEXT,
    platform TEXT,
    checked_at TIMESTAMP,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    watch_time REAL,
    ctr REAL
);
```

**Table: asset_registry**
```sql
CREATE TABLE asset_registry (
    id INTEGER PRIMARY KEY,
    job_id TEXT,
    asset_type TEXT,      -- script | audio | image | video | thumbnail
    file_path TEXT,
    created_at TIMESTAMP,
    size_bytes INTEGER
);
```

---

## 8. INFRASTRUCTURE & STORAGE

### Phase 1 (Local Machine + Free Cloud)

```
Local Machine:
  ├── Pipeline code (Python)
  ├── Generated assets (temp storage)
  ├── SQLite database
  └── Model weights (if GPU available)

Google Drive (Free 15GB):
  ├── Final videos backup
  ├── Character reference images
  └── Approved scripts archive

Free Cloud (Render / Railway free tier):
  └── Telegram bot webhook (if needed 24/7)
```

### Phase 2 (After Revenue)
```
VPS (₹500-800/month):
  └── Always-on pipeline runner

Cloudflare R2 / Backblaze B2:
  └── Asset storage (cheap S3-compatible)
```

### File Organization (Local)
```
ai_content_system/
├── outputs/
│   ├── {job_id}/
│   │   ├── script.json
│   │   ├── audio/
│   │   │   ├── segment_01.mp3
│   │   │   └── merged_audio.mp3
│   │   ├── images/
│   │   │   ├── scene_01.png
│   │   │   └── scene_02.png
│   │   ├── video_raw.mp4
│   │   ├── video_final.mp4
│   │   └── thumbnail.jpg
├── character/
│   ├── reference_images/
│   ├── lora_weights/ (if trained)
│   └── expressions/
├── assets/
│   ├── background_music/
│   ├── intro_outro/
│   └── fonts/
└── logs/
    └── pipeline.log
```

---

## 9. FILE & FOLDER STRUCTURE

```
ai-content-system/
├── README.md
├── .env                          # API keys (never commit)
├── .env.example
├── requirements.txt
├── config.py                     # Global config, niche maps, style maps
│
├── orchestrator/
│   ├── __init__.py
│   ├── graph.py                  # LangGraph StateGraph definition
│   ├── state.py                  # ContentState TypedDict
│   └── runner.py                 # Run jobs, queue management
│
├── agents/
│   ├── idea_generator.py
│   ├── script_writer.py
│   ├── voiceover_agent.py
│   ├── visual_agent.py
│   ├── video_assembler.py
│   ├── subtitle_agent.py
│   ├── upload_agent.py
│   └── analytics_agent.py
│
├── modules/
│   ├── character_consistency.py  # Character ref management
│   ├── hitl_handler.py           # Telegram bot + approval flow
│   ├── thumbnail_generator.py
│   └── scheduler.py              # APScheduler jobs
│
├── integrations/
│   ├── youtube_api.py
│   ├── instagram_api.py
│   ├── telegram_bot.py
│   ├── groq_client.py
│   ├── elevenlabs_client.py
│   ├── replicate_client.py
│   └── google_drive.py
│
├── database/
│   ├── db.py                     # SQLite connection + queries
│   └── migrations/
│
├── utils/
│   ├── ffmpeg_utils.py
│   ├── audio_utils.py
│   ├── image_utils.py
│   ├── file_utils.py
│   └── logger.py
│
├── prompts/
│   ├── script_prompts.py         # Per-niche script system prompts
│   ├── idea_prompts.py
│   └── visual_prompts.py         # Style tokens per niche
│
├── outputs/                      # Generated content (gitignored)
│   └── .gitkeep
│
└── tests/
    ├── test_script_agent.py
    ├── test_voiceover.py
    └── test_upload.py
```

---

## 10. PHASE-WISE BUILD PLAN

### Phase 0: Setup & Research (Week 1)
- [ ] GPU check on Manan's machine
- [ ] Set up Python environment + install all dependencies
- [ ] Get all API keys: Groq, YouTube, Meta Graph, Telegram, NewsAPI
- [ ] Design character (Figma / Canva rough sketch)
- [ ] Research open-source alternatives (see Section 11)
- [ ] Set up Google Drive folder structure
- [ ] Create YouTube channel + Instagram account for the bot

### Phase 1: Core Pipeline — Text-Only (Week 2)
- [ ] `state.py` — ContentState schema
- [ ] `graph.py` — LangGraph skeleton (nodes without logic)
- [ ] `idea_generator.py` — pytrends + Groq LLM
- [ ] `script_writer.py` — Groq script generation, JSON output
- [ ] `hitl_handler.py` — Telegram bot basic setup
- [ ] Test: Topic → Script → Telegram approval flow

### Phase 2: Audio + Visuals (Week 3-4)
- [ ] `voiceover_agent.py` — Edge-TTS integration
- [ ] `visual_agent.py` — FLUX/SD image generation
- [ ] `character_consistency.py` — Reference image workflow
- [ ] `video_assembler.py` — FFmpeg + MoviePy Ken Burns
- [ ] Test: Full pipeline without subtitles

### Phase 3: Finishing + Upload (Week 5)
- [ ] `subtitle_agent.py` — faster-whisper + FFmpeg
- [ ] `thumbnail_generator.py` — Pillow text overlay
- [ ] `upload_agent.py` — YouTube + Instagram upload
- [ ] `analytics_agent.py` — Basic metrics pull
- [ ] End-to-end test with real video upload (unlisted)

### Phase 4: Polish + Automate (Week 6)
- [ ] `scheduler.py` — Daily video queue
- [ ] Error recovery + retry logic
- [ ] Logging system (loguru)
- [ ] First 10 real videos uploaded
- [ ] Performance review — which niches/formats working?

### Phase 5: Optimize (Month 2+)
- [ ] A/B test thumbnails
- [ ] Train character LoRA (if GPU or cloud)
- [ ] Upgrade voiceover to Sarvam/ElevenLabs
- [ ] Add Kling/Pika for AI video motion
- [ ] Analytics feedback loop active

---

## 11. OPEN SOURCE TOOLS & MCPs TO RESEARCH

### Claude Code Research Tasks (Priority Order)

```
1. TRANSCRIPTION:
   Research: faster-whisper vs whisper-timestamped vs whisperX
   Goal: Word-level timestamps for animated captions
   Repo: https://github.com/SYSTRAN/faster-whisper

2. IMAGE GENERATION (No GPU):
   Research: FLUX.1 on fal.ai vs Replicate vs Together AI pricing
   Goal: Cheapest per-image cost with good quality
   Search: "FLUX.1 schnell API free tier 2024"

3. IMAGE GENERATION (With GPU):
   Research: ComfyUI vs AUTOMATIC1111 for IP-Adapter workflows
   Goal: Character consistency without LoRA training
   Repos: https://github.com/comfyanonymous/ComfyUI

4. VIDEO MOTION:
   Research: Kling API availability + pricing in India
   Alternative: Stable Video Diffusion (local)
   Search: "Kling AI API pricing 2024 India"

5. ANIMATED CAPTIONS:
   Research: auto-editor, capgen, captacity open source
   Goal: Word-highlight animation like CapCut auto-captions
   Search: "open source word highlight captions python"

6. THUMBNAIL AUTOMATION:
   Research: Bannerbear API vs local Pillow approach
   Goal: Professional thumbnails without manual design
   Search: "automated youtube thumbnail generation python"

7. TRENDING RESEARCH:
   Research: pytrends reliability + alternatives (Google Trends scraping)
   Also: nitter for Twitter trends (X API too expensive)
   Search: "pytrends alternative 2024 google trends API"

8. SCHEDULING:
   Research: APScheduler vs Celery vs RQ for job queuing
   Goal: Reliable queue that survives restarts
   Search: "python job queue persistent APScheduler Celery comparison"

9. VOICEOVER (HINDI):
   Research: Sarvam AI TTS API current pricing + quality
   Research: Kokoro TTS (open source, multilingual)
   Repos: https://github.com/remsky/Kokoro-FastAPI

10. MCPs RELEVANT TO THIS PROJECT:
    Research and test:
    - YouTube MCP (any available? for channel analytics)
    - Telegram MCP (bot management)
    - Google Drive MCP (already connected — test for file storage)
    - NewsAPI MCP (if available)
    - Reddit MCP (praw alternative)
    - FFmpeg MCP (check if exists)
```

### Key GitHub Repos to Audit
```
- https://github.com/SYSTRAN/faster-whisper
- https://github.com/comfyanonymous/ComfyUI
- https://github.com/AUTOMATIC1111/stable-diffusion-webui
- https://github.com/jnordberg/tortoise-tts
- https://github.com/myshell-ai/OpenVoice
- https://github.com/langchain-ai/langgraph
- https://github.com/google/python-youtube (YouTube API wrapper)
- Search: "faceless youtube channel automation python github"
- Search: "AI youtube shorts generator open source"
- Search: "automated video creation pipeline python"
```

---

## 12. SUCCESS METRICS & KPIs

### Channel Metrics (Monthly Targets)

| Metric | Month 1 | Month 3 | Month 6 |
|---|---|---|---|
| Videos uploaded | 20+ | 60+ | 120+ |
| YouTube Subscribers | 100 | 500 | 1000+ |
| YouTube Views | 1,000 | 15,000 | 50,000+ |
| Shorts Plays | 5,000 | 50,000 | 500,000 |
| Instagram Followers | 200 | 1,000 | 5,000 |
| Monthly Revenue | ₹0 | ₹500-2000 | ₹5,000-15,000 |

### System Metrics

| Metric | Target |
|---|---|
| Time: Idea → Uploaded video | < 30 minutes (full auto) |
| Cost per video | < ₹15 |
| Human time per video | < 5 minutes (review only) |
| Pipeline success rate | > 90% |
| Videos per week capacity | 7-14 |

---

## 13. KNOWN CONSTRAINTS & RISKS

| Risk | Severity | Mitigation |
|---|---|---|
| No GPU — local SD not possible | High | Use FLUX.1 API / cloud |
| YouTube API quota limits | Medium | Batch uploads, quota management |
| Instagram Graph API restrictions | Medium | Test early, have manual fallback |
| Free video gen credits exhausted | High | Budget ₹400/month for credits |
| Character consistency drift | Medium | Lock reference images, test thoroughly |
| Algorithm changes (YouTube/Insta) | Low | Diversify platforms from day 1 |
| IP/Copyright on visuals | Medium | Use original AI-gen only, no celeb faces |
| Edge-TTS sounds robotic | Medium | Upgrade to Sarvam/ElevenLabs quickly |
| Content policy violations | High | No face reveal, no misinformation, add disclaimers |

---

## 14. OPEN DECISIONS (PRE-BUILD)

These must be answered before Phase 1 starts:

| # | Decision | Options | Blocker? |
|---|---|---|---|
| 1 | **GPU availability** | Check laptop GPU model/VRAM | YES — changes image gen tool |
| 2 | **Character final design** | Need visual concept decided | YES — needed for consistency |
| 3 | **Channel name** | Brand identity | YES — needed for account creation |
| 4 | **First niche to launch with** | Horror? Tech? Finance? | Recommended: Horror/Dark Facts (highest CTR) |
| 5 | **Automation mode default** | Full auto vs topic-approval only | Medium — shapes HITL design |
| 6 | **Sarvam TTS vs Edge-TTS** | Quality vs free | Low — can swap anytime |

---

## APPENDIX: ENVIRONMENT VARIABLES NEEDED

```env
# LLM
GROQ_API_KEY=
ANTHROPIC_API_KEY=

# Voiceover
ELEVENLABS_API_KEY=       # When upgrading
SARVAM_API_KEY=           # When upgrading

# Image Generation
REPLICATE_API_TOKEN=
STABILITY_API_KEY=

# YouTube
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=

# Instagram / Meta
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_ACCOUNT_ID=

# Telegram HITL Bot
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# News / Research
NEWS_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=

# Google Drive
GOOGLE_DRIVE_CREDENTIALS_JSON=

# Storage paths
OUTPUT_DIR=./outputs
CHARACTER_DIR=./character
ASSETS_DIR=./assets
```

---

*PRD v1.0 — Subject to updates post GPU check and character design decisions.*
*Next step: Claude Code research pass on Section 11 open source tools.*
