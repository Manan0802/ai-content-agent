# Phase 4 — Series & Format Engine

> **Status 2026-07-22: Tasks 1-9 complete and pushed (120 tests green). Task 10 (live 3-part
> series) running.** Two decisions changed during the build, both driven by evidence:
> 1. **`BGM_MODE=silent` is now the default** for music formats. Manan pointed out he'll add the
>    song in the Instagram/YouTube app at post time — and trending audio genuinely cannot be
>    attached via API, so a baked track forfeits that reach. `baked` remains available.
> 2. **Series cliffhanger chaining uses the *script's* cliffhanger, not the outline's** — the
>    next part pays off what the viewer actually heard, not what the plan intended.
>
> Real bug found and fixed on the way: tests were monkeypatching `os.path.exists` globally, which
> silently broke `os.makedirs` (it uses it internally) so part directories were never created.
> `render_node` now exposes a module-level `_exists`/`_getsize` seam instead.

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Task-by-task, TDD,
> commit + push after every green step.

**Goal:** Turn the pipeline from *"one video, one narrator, one fixed length"* into what the
reference accounts actually do — **multi-part series**, in the **right format for the genre**,
with either **multi-voice dialogue** or **music + on-screen text**, in **Hindi / Haryanvi / Punjabi**.

Every decision below traces to measured evidence in:
- `docs/superpowers/specs/2026-07-20-reels-reference-analysis.md` (view counts per topic)
- `docs/superpowers/specs/2026-07-21-reels-batch2-analysis.md` (comment-bait funnel, serials)
- `docs/superpowers/specs/2026-07-21-audio-analysis.md` (**the audio findings — the big one**)

## What the research forces us to change

| Current pipeline | What the winners actually do | Evidence |
|---|---|---|
| One narrator voice | **Multi-character dialogue**, distinct voice per character | `aihealth_momos` 8.6M — stomach/intestine/liver/heart argue |
| Always TTS narration | **Thriller genre uses NO voiceover** — music + burned-in text | `shadow_p1/p2`, `realistic_crime`, `nighttales` all transcribe to the same song |
| Fixed ~45-60s | **10s to 91s depending on format** | 900K reel = 10.8s; 453K reel = 91s |
| Single standalone video | **Multi-part serials**, cliffhanger inside the dialogue | `r1_sheru` ends "अब असली कहाणी शुरू होगी"; Part 4 > Part 1 |
| Hinglish roman only | **Haryanvi / Punjabi written in dialect** | `r1_sheru`, `desiitoons_ladakh`, `babysardar` |
| Plain caption | **follow + share-to-3 + comment-emoji + YT link** | `technoyash_food` — 72.7K comments > 59K likes |

## Architecture

```
run_series(topic, format, language, parts=N)
  └─ series_writer        (Groq: one story → N parts, each with its own hook + cliffhanger)
       → [HITL series?]
  └─ for each part:
       script_writer      (format-aware: duration, segment count, characters[], speaker per line)
       visuals            (LOCKED style + character prompt shared across ALL parts)
       audio:
         mode=narrated →  multi-voice TTS (one Kokoro voice per character)
         mode=music    →  no TTS; pick BGM track; text-only dialogue
       composition_writer (Devanagari overlay top; speaker-aware dialogue; part badge)
       render → uploader
```

**Format profiles** (from the measured durations):

| Profile | Duration | Segments | Audio mode | Genre |
|---|---|---|---|---|
| `joke_10s` | 10-12s | 2-3 | narrated (2 voices) | irony / punchline |
| `montage_35s` | 30-38s | 5-7 | music | nostalgia / emotional |
| `drama_50s` | 45-55s | 6-9 | narrated (3-5 voices) | anthropomorphic health |
| `serial_75s` | 60-91s | 8-12 | music | thriller / crime / story |

## Global constraints

- Same discipline as Phases 1-3: every external call behind a mockable wrapper; unit tests never
  touch network/subprocess; error contract (append to `errors`, never raise out of a node).
- **Backwards compatible:** the existing single-video `run_job()` must keep working unchanged.
  Series is additive.
- No new paid dependency. Music comes from a local `assets/music/` folder the user curates
  (see Task 4's verification step).

---

### Task 1: Format profiles + config

**Files:** create `config/formats.py`; test `tests/test_formats.py`

- `FORMATS: dict[str, FormatProfile]` — dataclass with `name, target_duration_sec,
  segment_range (min,max), audio_mode ("narrated"|"music"), max_characters, description`.
- `get_format(name) -> FormatProfile`, raises on unknown.
- Add `default_format` and `supported_languages = ["hindi","haryanvi","punjabi","hinglish"]` to `Settings`.

Tests: each profile has sane values; `music` profiles have `max_characters=0`; unknown name raises.

---

### Task 2: Script schema v2 — characters + speaker-tagged dialogue

**Files:** edit `prompts/script_prompts.py`, `agents/script_writer.py`; test updates

New script JSON shape (additive — old keys stay):
```json
{
  "title": "...", "hook": "...",
  "characters": [{"id":"stomach","name":"पेट","voice_hint":"gruff male"}],
  "segments": [{"scene_number":1,"duration_sec":5,"speaker":"stomach",
                "dialogue":"अरे यार, ये कितनी चौमिन खाती है रे",
                "visual_direction":"...","character_visible":true}],
  "cliffhanger": "अब असली कहाणी शुरू होगी",
  "outro_cta": "...", "hashtags":[...]
}
```
Prompt must be **format-aware and language-aware**: injects target duration, segment count,
max characters, audio mode, and the language (writing Haryanvi/Punjabi *in dialect*, Hindi in
Devanagari — not roman). Applies the batch-1 findings: hook must be a question/bold claim/
mid-action drop; dialogue lines short enough to burn on screen.

Tests: parses new shape; falls back gracefully when `characters` missing (old scripts);
records error on bad JSON.

---

### Task 3: Multi-voice TTS

**Files:** edit `integrations/hyperframes_tts.py`, `agents/voiceover.py`; tests

- `VOICE_POOL` — the 12 real Kokoro voices (verified list: `af_heart, af_nova, af_sky, am_adam,
  am_michael, bf_emma, bf_isabella, bm_george, ef_dora, ff_siwis, jf_alpha, zf_xiaobei`).
- `assign_voices(characters) -> {character_id: voice}` — deterministic (hash-based) so the same
  character keeps the same voice across every part of a series.
- `voiceover_node`: when `audio_mode == "narrated"`, synthesize **per segment using that
  segment's speaker's voice**. When `audio_mode == "music"`, skip TTS entirely and set
  `state["audio_assets"] = []`.

Tests: two characters get different voices; same character → same voice across calls;
music mode produces no TTS calls at all.

---

### Task 4: Music mode — BGM track selection

**Files:** create `modules/music.py`; test; add `assets/music/README.md`

- [ ] **Step 1 (verification, do first):** confirm how BGM can be sourced. The `hyperframes-media`
  skill ships `scripts/audio.mjs` (BGM via HeyGen retrieval, else local Lyria/MusicGen generation)
  — check whether the local generation path actually runs on this Mac without a HeyGen key, and
  how slow it is. **If it's heavy or unavailable, fall back to the simple design below** — do not
  block the phase on it.
- Simple design (the fallback, and probably the right default): `pick_track(mood, music_dir)`
  reads `assets/music/<mood>/*.mp3` (moods: `dark`, `emotional`, `comedy`, `devotional`) and
  returns a deterministic choice per series. User curates the folder; zero cost, zero deps,
  full control over vibe. Missing folder/mood → return `None` and record a note (never crash).
- Optional nicety once basic music works: `npx hyperframes beats <dir> --json` gives beat
  timestamps → snap scene cuts to the beat.

**Honest open question to flag to Manan:** Instagram's *trending audio* is attached in the IG app
at upload time and cannot be set through the Graph API. So a baked-in track means giving up the
trending-audio boost. Options: (a) bake music in and accept it, (b) render a **silent** variant for
manual IG posting where he picks trending audio in-app. Recommend supporting both via a flag.

---

### Task 5: composition_writer v2 — dialogue text + both audio modes

**Files:** edit `agents/composition_writer.py`; tests

- **Devanagari dialogue overlay**: large text, **top of frame** (matching `aihealthstudio764`),
  thick stroke, one line per segment. Speaker name prefix when >1 character.
- **narrated mode**: per-segment `<audio>` as today (already works).
- **music mode**: single BGM `<audio>` spanning the whole composition; no per-scene audio;
  dialogue text is the only "voice".
- **Part badge**: when part of a series, render "PART N" in a corner.
- Keep the existing AI-label + disclosure behaviour untouched.

Tests: music mode emits exactly one `<audio>`; narrated mode emits one per segment; dialogue text
appears; part badge appears only when `part_number` set; the HyperFrames contract rules that bit
us before still hold (root `data-start="0"`, every timed element has `class="clip"` + `id`).

---

### Task 6: Series writer — one story → N parts

**Files:** create `prompts/series_prompts.py`, `agents/series_writer.py`; tests

- `series_writer_node(state, groq) -> ContentState` sets `state["series"] = {title, logline,
  characters[], style_prompt, parts:[{part_number, beat_summary, cliffhanger}]}`.
- Prompt: split one story into N parts of the chosen format; **every part must end on a
  cliffhanger written into the dialogue**, and part N+1 must open by paying it off.
- `style_prompt` + `characters` are generated **once** and reused by every part — this is the
  consistency lock that makes a channel look like one show.

Tests: N parts returned; each has a cliffhanger; characters/style shared; bad JSON → error contract.

---

### Task 7: Series state + `run_series()`

**Files:** edit `orchestrator/state.py`, create `orchestrator/series_runner.py`; tests

- `ContentState` gains `series: dict`, `part_number: int`, `series_id: str`, `format: str`
  (format already exists as short/long — rename usage carefully or add `format_profile`).
- `run_series(topic, format, language, parts, auto)` — runs `series_writer` once, then loops the
  existing per-video graph per part with the shared character/style, writing each part to
  `outputs/<series_id>/part_<n>/`.
- Job store: series jobs listed together so the dashboard can group them.

Tests: 3-part series produces 3 job states with shared `series_id` and incrementing `part_number`;
all fully mocked.

---

### Task 8: Caption generator with engagement CTA

**Files:** create `modules/caption.py`; test; wire into `agents/uploader.py`

Builds the caption in the measured winning shape:
```
😱 <hook question>

<1-2 line premise>

👉 Part <N+1> प्रोफाइल पर है
❤️ Follow करो + 3 दोस्तों को share करो
💬 Comment में कोई भी emoji — DM में भेज दूँगा
▶️ Full video: <youtube_url>

#Shorts + <hashtags>
```
Configurable: which CTAs are on, YouTube link, part CTA only when in a series.
Tests: contains `#Shorts`; part CTA only when part_number set; respects toggles.

---

### Task 9: Wire format/series through the graph

**Files:** edit `orchestrator/graph.py`, `orchestrator/runner.py`; tests

Thread `format_profile` + `language` + `series` context into `_script`, `_voiceover`,
`_composition`. Keep `run_job()` behaviour identical when no series/format given (default profile).

Full suite green; existing Phase 1-3 tests unchanged.

---

### Task 10: Live end-to-end — produce a real 3-part series

- Run `run_series("<a thriller premise>", format="serial_75s", language="haryanvi", parts=3)`.
- Verify: 3 playable MP4s, same characters/style across parts, music mode (no TTS), Devanagari
  dialogue on screen, part badges, cliffhangers, captions with CTAs.
- Open them, judge quality against `shadow_files0`, and log what still falls short.
- Update README + roadmap. Commit + push.

---

## Self-review notes

- **Scope is bigger than Phase 2 (10 tasks) but every task is small and independently testable.**
  Tasks 1-5 alone already upgrade single-video quality; 6-8 add the series layer. If we need to
  stop early, stopping after Task 5 still leaves a strictly better pipeline.
- **Two genuinely unverified things**, flagged rather than assumed: (1) whether local BGM
  generation works on this Mac (Task 4 Step 1 checks before committing to a design), (2) the
  Instagram trending-audio tradeoff, which is a product decision for Manan, not a code decision.
- **Deliberately deferred:** local GPU image-gen, fal.ai character locking (still text-prompt
  consistency for now — the single biggest remaining quality gap after this phase), Instagram
  API publishing, analytics feedback.
- **Character consistency caveat:** locking `style_prompt` + character description across parts
  improves consistency a lot but will still drift, because Pollinations has no reference-image
  conditioning. Closing that gap needs fal.ai FLUX.2 or a local GPU — a separate decision Manan
  has already been briefed on.
