# Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans, task-by-task, TDD, commit + push after every green step.

**Goal:** A local web dashboard where the user can *see* the AI Content Agent's work — every job that has run, its status, niche, topic, full script, and a playable preview of the rendered video — in one clean browser page. Requested 2026-07-07 after Phase 2's pipeline went code-complete.

**Scope boundary (honest):** The pipeline's HITL gates are still **blocking CLI prompts** inside a single process (the async `interrupt()`/`SqliteSaver` resume refactor is deferred to Phase 5 per the spec's §6 research log). So a job only becomes visible to the dashboard **after it finishes** (complete or failed) — there is no live "paused, waiting for you in the browser" state yet, and no browser approve/reject buttons. Those land when the async-HITL refactor does. This dashboard is a **read-only monitoring view** of finished jobs plus their outputs. Building it now is still worth it: it's the persistence + view layer everything later builds on, and it lights up the moment real jobs run.

**Why FastAPI:** one small app serves JSON + the HTML page + the MP4 file, and Phase 3 will want real API endpoints anyway (trigger upload, pull analytics) — so this isn't throwaway. Kept to a single module; no heavier framework machinery than needed.

## Architecture

```
runner.run_job() → (after graph.invoke) → job_store.save_job(state)
                                              writes outputs/<job_id>/state.json

dashboard/app.py (FastAPI)
  GET /               → the HTML dashboard page
  GET /api/jobs       → [{job_id, status, niche, topic, created_at, has_video}]  (newest first)
  GET /api/jobs/{id}  → full ContentState dict for one job
  GET /video/{id}     → streams outputs/<id>/render/final.mp4
```

## Global Constraints

- Same rules as Phase 1/2: unit tests never hit the network; `job_store` tested against `tmp_path`, the server tested with FastAPI's `TestClient`. No test starts a real uvicorn server.
- The dashboard is **read-only** over the filesystem — it never mutates job state, never triggers a run. (Triggering runs from the browser is a later task, gated on async HITL.)
- Cross-platform: no POSIX-only path handling — use `os.path`/`pathlib`, since Windows is the primary machine.

## File Structure (additions)

- `modules/job_store.py` — `save_job`, `list_jobs`, `get_job`
- `dashboard/__init__.py`, `dashboard/app.py` — FastAPI app + the HTML page
- Edits: `orchestrator/runner.py` (call `save_job`), `requirements.txt` (fastapi, uvicorn), `README.md` (launch instructions)
- Tests: `tests/test_job_store.py`, `tests/test_dashboard.py`

---

### Task 1: Job persistence layer

**Files:** Create `modules/job_store.py`; test `tests/test_job_store.py`; edit `orchestrator/runner.py`

**Interfaces:**
- `save_job(state: ContentState, outputs_dir: str) -> str` — writes `<outputs_dir>/<job_id>/state.json` (creating dirs), returns the path.
- `list_jobs(outputs_dir: str) -> list[dict]` — reads every `<outputs_dir>/*/state.json`, returns a list of summary dicts `{job_id, status, niche, topic, created_at, has_video}` sorted by `created_at` descending. `has_video` = whether `<job_id>/render/final.mp4` exists and is non-empty. Missing/unreadable `outputs_dir` → `[]`.
- `get_job(job_id: str, outputs_dir: str) -> dict | None` — full parsed state.json for one job, or `None` if absent.

**Steps:**
1. Write failing tests: `save_job` then `get_job` round-trips a state; `list_jobs` returns newest-first and flags `has_video`; `list_jobs` on a nonexistent dir returns `[]`.
2. Run → fails (ModuleNotFoundError).
3. Implement `modules/job_store.py` (json dump/load, `glob` over `*/state.json`, sort by `created_at`).
4. Run → pass.
5. Wire into `runner.run_job`: after `app.invoke(state)`, call `save_job(result, SETTINGS.outputs_dir)` before returning. Update `tests/test_runner.py` if needed (the existing monkeypatched test writes to the real `outputs/` — point `SETTINGS.outputs_dir` usage at `tmp_path` via monkeypatch, or assert the file was written under a tmp dir). Keep the suite green + network/subprocess-free.
6. Full suite green → commit `feat: job_store (persist job state for the dashboard)` → push.

---

### Task 2: FastAPI server + API endpoints

**Files:** Create `dashboard/__init__.py`, `dashboard/app.py`; test `tests/test_dashboard.py`; edit `requirements.txt`

**Interfaces:**
- `create_app(outputs_dir: str) -> FastAPI` — factory so tests inject a `tmp_path` outputs dir (don't read a module-level global).
- `GET /api/jobs` → `list_jobs(outputs_dir)` as JSON.
- `GET /api/jobs/{job_id}` → `get_job(...)` as JSON, or 404.
- `GET /video/{job_id}` → `FileResponse` of `<outputs_dir>/<job_id>/render/final.mp4`, or 404 if missing.
- `GET /` → the HTML page (Task 3; in Task 2 a placeholder string is fine).

**Steps:**
1. Add `fastapi==0.115.6` and `uvicorn==0.34.0` to `requirements.txt`; `pip install`.
2. Write failing tests with `TestClient(create_app(str(tmp_path)))`: `/api/jobs` returns a seeded job; `/api/jobs/{id}` returns 404 for unknown; `/video/{id}` returns 404 when no mp4. Seed by calling `save_job` into `tmp_path` first.
3. Run → fails.
4. Implement `dashboard/app.py` with `create_app`.
5. Run → pass. Full suite green → commit `feat: dashboard FastAPI server (jobs + video API)` → push.

---

### Task 3: Polished dashboard UI

**Files:** edit `dashboard/app.py` (serve the HTML at `/`); edit `README.md`

**Design bar (the user explicitly wants a strong UI):** dark theme, clean type scale, a responsive grid of job cards. Each card: a colored status badge (complete=green, failed=red, media_complete=blue, running/other=amber), the niche as a small tag, the topic as the card title, relative created time. Click a card → a detail panel: the full script (hook, per-segment voiceover + visual direction, hashtags) and, if `has_video`, an inline `<video controls>` pointed at `/video/{id}`. A header with the app name and a live job count. Poll `/api/jobs` every few seconds so a finished run appears without a manual refresh. Empty state when there are no jobs: a friendly "No jobs yet — add your GROQ_API_KEY to `.env` and run `python -m orchestrator.runner`" card. All CSS/JS inline in the one page (no external CDN dependency — must work offline).

**Steps:**
1. Replace the `/` placeholder with the full HTML page (inline `<style>` + `<script>` that fetches the JSON APIs and renders).
2. Add a test asserting `GET /` returns 200 and the HTML contains the app title and the JS fetch call (light smoke test — the API endpoints already carry the real logic tests).
3. Manually launch once to eyeball it: `uvicorn dashboard.app:create_app --factory --reload` (note the exact command in README), open `http://localhost:8000`, confirm the empty state renders. (No real jobs exist yet without a Groq key — the empty state is what should show.)
4. Add a **Dashboard** section to `README.md` with the launch command and what it shows.
5. Full suite green → commit `feat: polished dashboard UI (job cards + script + video preview)` → push.

---

## Self-Review Notes

- **Scope honesty:** read-only monitoring of finished jobs. Live "paused in browser" + approve/reject is explicitly out, gated on the deferred async-HITL refactor — not forgotten, called out here and in the spec §6 log.
- **No fake data:** the dashboard shows only what `job_store` persisted from real runs; the empty state tells the user exactly how to produce the first job. It stays empty (honestly) until a Groq key is added — it does not fabricate sample jobs.
- **Testable seams:** `create_app(outputs_dir)` factory + `job_store` functions taking an explicit dir keep everything unit-testable against `tmp_path`, no running server, no network.
- **Not over-built:** one FastAPI module, three JSON/file routes + one HTML page. No database (filesystem is the store), no auth (localhost personal tool), no build step (inline CSS/JS).
