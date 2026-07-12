# Phase 3 — YouTube Publish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans, task-by-task, TDD, commit + push after every green step.

**Goal:** Take the rendered MP4 from Phase 2 and upload it to YouTube as an **unlisted** video, behind a human "publish?" gate — with title/description/#Shorts/tags built automatically from the script. Verify: mocked tests now; one real unlisted upload once the user connects a channel. **No Instagram, no analytics, no thumbnail in this plan** (see scope boundary).

**Scope boundary (deliberate, honest):**
- **YouTube only.** Instagram Reels publishing needs a Business account + Meta app review (2–4 week approval, per the 2026-07-06 research in spec §6) — that's its own later plan with a manual fallback. Not blocking YouTube.
- **Unlisted, not public.** First uploads go unlisted so the user reviews the real thing on YouTube before making it public. A config flag allows `public`/`private` later.
- **No custom thumbnail.** Research confirmed YouTube **rejects custom thumbnails for Shorts** (`thumbnails.set` errors). Since this pipeline makes vertical Shorts, a thumbnail step would just fail — skipped by design, noted so it's not mistaken for an omission.
- **No analytics pull.** The YouTube Analytics API feedback loop (into `idea_generator`) is a separate later task — it needs videos that have actually accumulated views first.
- **#Shorts tagging.** Research confirmed a Short is identified by `#Shorts` in the title or description (no API flag). We put it in the description automatically.

## Architecture (this phase)

```
... render → [HITL render] → status="media_complete"
  └─ uploader_node:
       (skip cleanly if no render_output_path, or no YouTube creds configured)
       → [HITL publish?]        (new gate — publishing is public-facing, never silent)
       → YouTube Data API videos.insert (resumable upload, privacy=unlisted)
       → sets state["youtube_video_id"], state["youtube_url"], status="published"
```

**Auth model:** YouTube Data API v3 uses OAuth 2.0. Getting a token requires a **one-time browser consent** by the user (only they can approve access to their channel). We handle it exactly like every other external dep: a small `scripts/youtube_auth.py` helper runs the consent flow once and saves a **refresh token**; the pipeline then reads `client_id` / `client_secret` / `refresh_token` from `.env` and mints access tokens automatically, no further human step. All code is built mockable so the full suite runs with zero network/OAuth.

**Tech stack (added):** `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`.

## What the user must do (for a LIVE upload — NOT needed to build/test the code)

1. Create a YouTube channel (if not already) + a Google Cloud project; enable **YouTube Data API v3**.
2. Create an **OAuth 2.0 Client ID** (type: Desktop app); note `client_id` + `client_secret`.
3. Run `python -m scripts.youtube_auth` once → browser consent → it writes `YOUTUBE_REFRESH_TOKEN` to `.env`.
4. **Apply for a quota audit early** (spec §6): default quota = ~6 uploads/day; Google's review takes weeks. Fine for testing; needed before scaling.

None of this blocks building/testing — same pattern as fal.ai/Groq. The live smoke test (Task 6) waits on it.

## Global Constraints

- Same as Phase 1/2: no agent calls the Google SDK directly — it goes through `YouTubeClient` whose `_insert`/token methods are mockable. Unit tests never hit the network or OAuth.
- `uploader_node` follows the error contract: on failure append to `errors`, set safe state, never raise out of a node. Missing creds or missing video → skip cleanly with a recorded note, not a crash (so a Groq-only / no-YouTube run still completes at `media_complete`).

## File Structure (additions)

- `integrations/youtube_client.py` — `YouTubeClient`
- `agents/uploader.py` — `uploader_node`
- `scripts/__init__.py`, `scripts/youtube_auth.py` — one-time OAuth consent → refresh token
- Edits: `config.py`, `orchestrator/state.py`, `orchestrator/graph.py`, `orchestrator/runner.py`, `.env.example`, `requirements.txt`, `README.md`
- Tests: `tests/test_youtube_client.py`, `tests/test_uploader.py`, graph/runner updates

---

### Task 1: Config + deps for YouTube

**Files:** edit `config.py`, `.env.example`, `requirements.txt`, `tests/test_config.py`

**Interfaces — adds to `Settings`:** `youtube_client_id: str | None`, `youtube_client_secret: str | None`, `youtube_refresh_token: str | None`, `youtube_privacy: str = "unlisted"`, `publish_platform: str = os.getenv("PUBLISH_PLATFORM", "youtube")`.

Steps: failing test asserting `SETTINGS.youtube_privacy == "unlisted"`; add fields (reading `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` / `YOUTUBE_REFRESH_TOKEN` / `YOUTUBE_PRIVACY` from env); add the three google libs to `requirements.txt` + install; `.env.example` gets the YouTube vars; test green → commit + push.

---

### Task 2: YouTubeClient wrapper

**Files:** create `integrations/youtube_client.py`; test `tests/test_youtube_client.py`

**Interfaces:**
- `YouTubeClient(client_id=None, client_secret=None, refresh_token=None)` — reads from SETTINGS if omitted.
- `.is_configured() -> bool` — True only if all three creds present (lets `uploader_node` skip cleanly).
- `.upload_video(file_path, title, description, tags, privacy="unlisted") -> str` — returns the video id. Internally builds the `videos.insert` body and calls `self._insert(body, file_path)` (the mockable seam, mirrors `GroqClient._chat`). `_insert` builds the real service (google-auth refresh creds → `googleapiclient.discovery.build("youtube","v3")`) + `MediaFileUpload(file_path, resumable=True)` + resumable `next_chunk()` loop, returns `response["id"]`.

Steps: failing test — monkeypatch `_insert` to capture the body + return `{"id":"abc123"}`; assert `upload_video(...)` returns `"abc123"`, that snippet.title/description/tags and status.privacyStatus are set correctly, and `#Shorts` handling is left to the caller (uploader builds the description). Add a test that `is_configured()` is False when a cred is missing. Implement. Green → commit + push.

---

### Task 3: uploader_node

**Files:** create `agents/uploader.py`; test `tests/test_uploader.py`

**Interfaces:**
- `uploader_node(state, youtube, notifier) -> ContentState`
- If `status == "failed"` or no `render_output_path` → record a note in `errors` and return unchanged (nothing to upload).
- If `not youtube.is_configured()` → set `state["errors"]` note "youtube not configured — skipped upload", leave `status="media_complete"`, return (a free/no-YouTube run still succeeds).
- Build metadata from the script: `title` = `script.title` (trimmed to 100 chars); `description` = hook + "\n\n" + the AI-disclosure text + "\n\n" + hashtags + " #Shorts"; `tags` = script.hashtags (stripped of `#`).
- If `"publish"` in `hitl_checkpoints` and mode != `full_auto` → `notifier.ask_approval("Publish to YouTube?", preview)`; reject → leave `media_complete`, record "publish rejected", return (reject is NOT a failure — the video is fine, just not posted).
- On approve/auto → `youtube.upload_video(...)`, set `state["youtube_video_id"]`, `state["youtube_url"] = "https://youtu.be/<id>"`, `status="published"`. On upload exception → `errors` + keep `media_complete` (don't lose the rendered video over an upload hiccup).

Steps: failing tests — FakeYouTube (`is_configured`→True, `upload_video`→"vid123"); ApproveNotifier → status "published" + url set; RejectNotifier → stays "media_complete", not published; unconfigured client → skipped, stays "media_complete"; failed prior state → untouched. Implement. Green → commit + push.

---

### Task 4: one-time OAuth helper

**Files:** create `scripts/__init__.py`, `scripts/youtube_auth.py`

`python -m scripts.youtube_auth` → `google_auth_oauthlib.flow.InstalledAppFlow.from_client_config({client_id, client_secret from SETTINGS}, scopes=["https://www.googleapis.com/auth/youtube.upload"])` → `run_local_server()` → prints the refresh token and appends `YOUTUBE_REFRESH_TOKEN=<token>` to `.env` (or tells the user to paste it). Scope kept to `youtube.upload` only (least privilege — no read/delete). This script is interactive/manual (not unit-tested — it's a one-shot user tool); keep it tiny and obvious. Commit + push.

---

### Task 5: wire uploader into graph + runner

**Files:** edit `orchestrator/state.py`, `orchestrator/graph.py`, `orchestrator/runner.py`, `tests/test_graph.py`

- `ContentState` gains `youtube_video_id: str`, `youtube_url: str` (default `""`); status vocabulary gains `published`.
- Graph: add `uploader` node after `render`. Route `render → uploader → END` (uploader itself decides to skip/gate/upload; it never hard-fails the run).
- `build_graph(..., youtube=None)` param; `_uploader(state, youtube, notifier)`.
- Runner: construct `YouTubeClient()`, pass in; default `hitl_checkpoints` becomes `["topic","script","render","publish"]`.
- Update graph/runner tests with a FakeYouTube so the full auto run reaches `published` (or `media_complete` when unconfigured). Keep suite network-free. Green → commit + push.

---

### Task 6: README + live smoke test

- README: add YouTube setup steps + the `scripts.youtube_auth` one-time flow + the quota-audit note; mark Phase 3 in the roadmap.
- Live smoke test (after the user does the 4 setup steps): `python -m orchestrator.runner` → approve topic/script/render/publish → a real unlisted video on their channel; print the `youtu.be/<id>` URL; it appears on the dashboard as `published` with the link. Verify with the user that the unlisted video plays on YouTube.
- Commit + push.

---

## Self-Review Notes

- **Scope honesty:** YouTube unlisted upload only. Instagram (Meta review), analytics feedback, and public-by-default are explicitly deferred with reasons — not forgotten.
- **Graceful degradation:** every skip path (no creds, no video, rejected publish) leaves the job at `media_complete`, not `failed` — the rendered video is never lost because of an upload-stage issue. Only a real upload API error is recorded, and even then the video stays.
- **Least privilege:** OAuth scope limited to `youtube.upload`.
- **One flagged unverified assumption:** exact `videos.insert` request body shape + resumable `next_chunk()` handling is per google-api-python-client docs (confirmed via context7), but the live OAuth + first real upload must be verified once the user connects a channel (Task 6) — same "verify against the real tool" discipline that caught the fal.ai slug and HyperFrames flags.
- **Testable seams:** `YouTubeClient._insert` + `is_configured()` keep the suite fully mocked; the interactive auth helper is the only non-unit-tested piece (a one-shot user tool by nature).
