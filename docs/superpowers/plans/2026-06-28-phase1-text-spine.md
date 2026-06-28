# Phase 1 — Text Spine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the runnable backbone of the AI Content Agent — a LangGraph pipeline that turns a niche into ranked topic ideas, then a full structured video script, with pluggable human approval gates — all locally, no GPU, no media yet.

**Architecture:** A LangGraph `StateGraph` holds a typed `ContentState` and routes `idea_generator → [HITL topic] → script_writer → [HITL script]`. External LLM work goes through one thin Groq client. Human approval goes through a `Notifier` protocol whose default `CLINotifier` works with zero setup (WhatsApp adapter is a later phase). Trends come through a `TrendsProvider` protocol whose default `SeedTrendsProvider` reads a static list, so the spine runs without Reddit/News API keys.

**Tech Stack:** Python 3.11+, langgraph, langchain-groq, pydantic, python-dotenv, loguru, pytest.

## Global Constraints

- Python 3.11+ only.
- No GPU / no local heavy ML — this phase is text-only, CPU-only.
- Free-first: the only external API used in Phase 1 is Groq (free tier). Everything else runs offline/local.
- All LLM calls go through `integrations/groq_client.py` — no agent calls the Groq SDK directly.
- All human interaction goes through the `Notifier` protocol — no agent calls `input()`/`print()` for approvals directly.
- Unit tests must NOT hit the network. LLM and trends calls are mocked. One optional integration test is gated behind the `GROQ_API_KEY` env var and skipped if absent.
- Language default: Hinglish. Niche default: configurable, multi-domain.

---

## File Structure

- `requirements.txt` — pinned deps
- `.env.example` / `.env` (gitignored) — `GROQ_API_KEY`
- `.gitignore`
- `config.py` — loads env, niche list, defaults, model name
- `orchestrator/state.py` — `ContentState` TypedDict + `new_state()` factory
- `orchestrator/graph.py` — `build_graph()` wiring nodes + SQLite checkpointer
- `orchestrator/runner.py` — CLI entry: `run_job(niche, mode)`
- `integrations/groq_client.py` — `GroqClient.complete()`
- `agents/idea_generator.py` — `idea_generator_node(state)` + `TrendsProvider`/`SeedTrendsProvider`
- `agents/script_writer.py` — `script_writer_node(state)`
- `modules/notifier.py` — `Notifier` protocol + `CLINotifier` + `AutoApproveNotifier`
- `prompts/idea_prompts.py`, `prompts/script_prompts.py` — system prompts per niche
- `tests/...` — one test module per unit

---

### Task 1: Project scaffold, config, and dependencies

**Files:**
- Create: `requirements.txt`, `.gitignore`, `.env.example`, `config.py`
- Create: `orchestrator/__init__.py`, `agents/__init__.py`, `integrations/__init__.py`, `modules/__init__.py`, `prompts/__init__.py`, `tests/__init__.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `config.SETTINGS` (object with `.groq_api_key: str | None`, `.groq_model: str`, `.niches: list[str]`, `.default_niche: str`, `.default_language: str`, `.default_mode: str`)

- [ ] **Step 1: Create the virtualenv and git repo**

Run (PowerShell, in project root):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
git init
```
Expected: `.venv` created, `Initialized empty Git repository`.

- [ ] **Step 2: Write `requirements.txt`**

```
langgraph==0.2.74
langchain-groq==0.2.3
groq==0.13.1
pydantic==2.10.4
python-dotenv==1.0.1
loguru==0.7.3
pytest==8.3.4
```

- [ ] **Step 3: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: all install without error.

- [ ] **Step 4: Write `.gitignore`**

```
.venv/
__pycache__/
*.pyc
.env
outputs/
*.sqlite
.pytest_cache/
```

- [ ] **Step 5: Write `.env.example`**

```
GROQ_API_KEY=
```

- [ ] **Step 6: Create empty package `__init__.py` files**

Create each of: `orchestrator/__init__.py`, `agents/__init__.py`, `integrations/__init__.py`, `modules/__init__.py`, `prompts/__init__.py`, `tests/__init__.py` — each an empty file.

- [ ] **Step 7: Write the failing test for config**

`tests/test_config.py`:
```python
from config import SETTINGS

def test_settings_has_defaults():
    assert SETTINGS.groq_model
    assert "horror" in SETTINGS.niches
    assert SETTINGS.default_language == "hinglish"
    assert SETTINGS.default_mode in {"full_auto", "semi_auto", "script_only", "manual"}
```

- [ ] **Step 8: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'config'`.

- [ ] **Step 9: Write `config.py`**

```python
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = "llama-3.3-70b-versatile"
    niches: list[str] = field(
        default_factory=lambda: [
            "horror", "tech", "finance", "motivation", "mythology", "comedy", "trending",
        ]
    )
    default_niche: str = "horror"
    default_language: str = "hinglish"
    default_mode: str = "semi_auto"


SETTINGS = Settings()
```

- [ ] **Step 10: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 11: Commit**

```
git add .
git commit -m "chore: scaffold project, config, deps"
```

---

### Task 2: ContentState schema

**Files:**
- Create: `orchestrator/state.py`
- Test: `tests/test_state.py`

**Interfaces:**
- Produces:
  - `ContentState` (TypedDict, total=False) with keys: `job_id:str`, `created_at:str`, `status:str`, `mode:str`, `niche:str`, `language:str`, `format:str`, `topic:str`, `topic_candidates:list[dict]`, `script:dict`, `hitl_checkpoints:list[str]`, `human_approved:dict`, `errors:list[str]`
  - `new_state(niche:str, mode:str, language:str, format:str, hitl_checkpoints:list[str]) -> ContentState`

- [ ] **Step 1: Write the failing test**

`tests/test_state.py`:
```python
from orchestrator.state import new_state

def test_new_state_sets_meta_and_defaults():
    s = new_state(niche="horror", mode="semi_auto", language="hinglish",
                  format="short", hitl_checkpoints=["topic", "script"])
    assert s["niche"] == "horror"
    assert s["mode"] == "semi_auto"
    assert s["status"] == "idle"
    assert s["job_id"]
    assert s["created_at"]
    assert s["topic_candidates"] == []
    assert s["errors"] == []
    assert s["human_approved"] == {}
    assert s["hitl_checkpoints"] == ["topic", "script"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_state.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `orchestrator/state.py`**

```python
import uuid
from datetime import datetime, timezone
from typing import TypedDict


class ContentState(TypedDict, total=False):
    job_id: str
    created_at: str
    status: str          # idle | running | paused_for_human | complete | failed
    mode: str            # full_auto | semi_auto | script_only | manual
    niche: str
    language: str
    format: str          # short | long
    topic: str
    topic_candidates: list[dict]
    script: dict
    hitl_checkpoints: list[str]
    human_approved: dict
    errors: list[str]


def new_state(niche: str, mode: str, language: str, format: str,
              hitl_checkpoints: list[str]) -> ContentState:
    return ContentState(
        job_id=str(uuid.uuid4())[:8],
        created_at=datetime.now(timezone.utc).isoformat(),
        status="idle",
        mode=mode,
        niche=niche,
        language=language,
        format=format,
        topic="",
        topic_candidates=[],
        script={},
        hitl_checkpoints=hitl_checkpoints,
        human_approved={},
        errors=[],
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_state.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```
git add orchestrator/state.py tests/test_state.py
git commit -m "feat: ContentState schema + new_state factory"
```

---

### Task 3: Notifier protocol + CLI and AutoApprove implementations

**Files:**
- Create: `modules/notifier.py`
- Test: `tests/test_notifier.py`

**Interfaces:**
- Produces:
  - `Notifier` (Protocol): `ask_approval(self, title: str, preview: str) -> str` returns one of `"approve" | "reject"`
  - `AutoApproveNotifier` — always returns `"approve"` (used in `full_auto`/tests)
  - `CLINotifier(input_fn=input, print_fn=print)` — prints preview, reads `a`/`r`, returns `"approve"`/`"reject"`. `input_fn`/`print_fn` are injectable for testing.

- [ ] **Step 1: Write the failing test**

`tests/test_notifier.py`:
```python
from modules.notifier import AutoApproveNotifier, CLINotifier

def test_autoapprove_always_approves():
    assert AutoApproveNotifier().ask_approval("t", "p") == "approve"

def test_cli_notifier_reads_approve():
    n = CLINotifier(input_fn=lambda _: "a", print_fn=lambda *a, **k: None)
    assert n.ask_approval("Topic", "preview text") == "approve"

def test_cli_notifier_reads_reject():
    n = CLINotifier(input_fn=lambda _: "r", print_fn=lambda *a, **k: None)
    assert n.ask_approval("Topic", "preview text") == "reject"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_notifier.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `modules/notifier.py`**

```python
from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class Notifier(Protocol):
    def ask_approval(self, title: str, preview: str) -> str:
        """Return 'approve' or 'reject'."""
        ...


class AutoApproveNotifier:
    def ask_approval(self, title: str, preview: str) -> str:
        return "approve"


class CLINotifier:
    def __init__(self, input_fn: Callable[[str], str] = input,
                 print_fn: Callable[..., None] = print):
        self._input = input_fn
        self._print = print_fn

    def ask_approval(self, title: str, preview: str) -> str:
        self._print(f"\n=== {title} ===\n{preview}\n")
        answer = self._input("Approve? [a]pprove / [r]eject: ").strip().lower()
        return "approve" if answer.startswith("a") else "reject"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_notifier.py -v`
Expected: 3 PASS.

- [ ] **Step 5: Commit**

```
git add modules/notifier.py tests/test_notifier.py
git commit -m "feat: pluggable Notifier (CLI + AutoApprove)"
```

---

### Task 4: Groq client wrapper

**Files:**
- Create: `integrations/groq_client.py`
- Test: `tests/test_groq_client.py`

**Interfaces:**
- Produces:
  - `GroqClient(api_key: str | None = None, model: str | None = None)`
  - `GroqClient.complete(self, system: str, user: str, json_mode: bool = False) -> str` — returns raw text; if `json_mode`, requests JSON object response. Internally calls `self._chat` which is a thin wrapper around the Groq SDK so tests can monkeypatch it.

- [ ] **Step 1: Write the failing test**

`tests/test_groq_client.py`:
```python
from integrations.groq_client import GroqClient

def test_complete_passes_messages_and_returns_text(monkeypatch):
    captured = {}
    def fake_chat(messages, json_mode):
        captured["messages"] = messages
        captured["json_mode"] = json_mode
        return "hello world"
    c = GroqClient(api_key="x", model="m")
    monkeypatch.setattr(c, "_chat", fake_chat)
    out = c.complete(system="sys", user="usr", json_mode=True)
    assert out == "hello world"
    assert captured["messages"][0]["role"] == "system"
    assert captured["messages"][0]["content"] == "sys"
    assert captured["messages"][1]["role"] == "user"
    assert captured["json_mode"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_groq_client.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `integrations/groq_client.py`**

```python
from groq import Groq
from config import SETTINGS


class GroqClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self._api_key = api_key or SETTINGS.groq_api_key
        self._model = model or SETTINGS.groq_model
        self._client = None  # lazy — never constructed in unit tests

    def _ensure_client(self) -> Groq:
        if self._client is None:
            if not self._api_key:
                raise RuntimeError("GROQ_API_KEY not set")
            self._client = Groq(api_key=self._api_key)
        return self._client

    def _chat(self, messages: list[dict], json_mode: bool) -> str:
        client = self._ensure_client()
        kwargs = {"model": self._model, "messages": messages, "temperature": 0.8}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content

    def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        return self._chat(messages, json_mode)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_groq_client.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```
git add integrations/groq_client.py tests/test_groq_client.py
git commit -m "feat: Groq client wrapper (mockable _chat)"
```

---

### Task 5: Idea generator node + trends provider

**Files:**
- Create: `prompts/idea_prompts.py`, `agents/idea_generator.py`
- Test: `tests/test_idea_generator.py`

**Interfaces:**
- Consumes: `ContentState` (Task 2), `GroqClient` (Task 4)
- Produces:
  - `TrendsProvider` (Protocol): `fetch(self, niche: str) -> list[str]`
  - `SeedTrendsProvider` — returns a static list of seed topics per niche
  - `idea_generator_node(state: ContentState, groq: GroqClient, trends: TrendsProvider) -> ContentState` — sets `state["topic_candidates"]` to a list of dicts `{title, hook, format, niche, tone, viral_score}`, sorted by `viral_score` desc, and `state["status"]="running"`. On error, appends to `state["errors"]` and leaves candidates `[]`.

- [ ] **Step 1: Write `prompts/idea_prompts.py`**

```python
def idea_system_prompt(niche: str, language: str) -> str:
    return (
        f"You are a viral content strategist for a {language} short-form video channel "
        f"in the '{niche}' niche. Given trending seed topics, propose the 3 best video ideas. "
        "Respond ONLY as a JSON object with key 'ideas' -> list of objects with keys: "
        "title, hook, format ('short'|'long'), niche, tone, viral_score (0-100 integer)."
    )
```

- [ ] **Step 2: Write the failing test**

`tests/test_idea_generator.py`:
```python
import json
from orchestrator.state import new_state
from agents.idea_generator import idea_generator_node, SeedTrendsProvider

class FakeGroq:
    def __init__(self, payload): self.payload = payload
    def complete(self, system, user, json_mode=False): return self.payload

def test_seed_trends_returns_list():
    assert isinstance(SeedTrendsProvider().fetch("horror"), list)
    assert SeedTrendsProvider().fetch("horror")

def test_idea_node_sets_sorted_candidates():
    payload = json.dumps({"ideas": [
        {"title": "A", "hook": "h", "format": "short", "niche": "horror", "tone": "dark", "viral_score": 70},
        {"title": "B", "hook": "h", "format": "short", "niche": "horror", "tone": "dark", "viral_score": 90},
    ]})
    s = new_state("horror", "semi_auto", "hinglish", "short", ["topic"])
    out = idea_generator_node(s, groq=FakeGroq(payload), trends=SeedTrendsProvider())
    assert [c["title"] for c in out["topic_candidates"]] == ["B", "A"]
    assert out["status"] == "running"

def test_idea_node_records_error_on_bad_json():
    s = new_state("horror", "semi_auto", "hinglish", "short", ["topic"])
    out = idea_generator_node(s, groq=FakeGroq("not json"), trends=SeedTrendsProvider())
    assert out["topic_candidates"] == []
    assert out["errors"]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_idea_generator.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 4: Write `agents/idea_generator.py`**

```python
import json
from typing import Protocol
from orchestrator.state import ContentState
from integrations.groq_client import GroqClient
from prompts.idea_prompts import idea_system_prompt

_SEEDS = {
    "horror": ["Bhoot bangla real story", "Cursed village India", "Haunted railway station"],
    "tech": ["New AI tool 2026", "Phone hidden features", "Coding job future"],
    "finance": ["SIP vs FD", "First salary mistakes", "Credit card trap"],
    "motivation": ["5am discipline", "Failure to comeback", "Stop scrolling"],
    "mythology": ["Mahabharata hidden fact", "Shiva untold story", "Ramayana mystery"],
    "comedy": ["Indian parents logic", "Hostel life", "Online class fails"],
    "trending": ["Today viral news", "Latest meme explained", "Trending challenge"],
}


class TrendsProvider(Protocol):
    def fetch(self, niche: str) -> list[str]: ...


class SeedTrendsProvider:
    def fetch(self, niche: str) -> list[str]:
        return _SEEDS.get(niche, _SEEDS["trending"])


def idea_generator_node(state: ContentState, groq: GroqClient,
                        trends: TrendsProvider) -> ContentState:
    state["status"] = "running"
    try:
        seeds = trends.fetch(state["niche"])
        system = idea_system_prompt(state["niche"], state["language"])
        user = "Trending seed topics:\n- " + "\n- ".join(seeds)
        raw = groq.complete(system=system, user=user, json_mode=True)
        ideas = json.loads(raw).get("ideas", [])
        ideas.sort(key=lambda i: i.get("viral_score", 0), reverse=True)
        state["topic_candidates"] = ideas
    except Exception as e:  # noqa: BLE001 - record, don't crash the pipeline
        state.setdefault("errors", []).append(f"idea_generator: {e}")
        state["topic_candidates"] = []
    return state
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_idea_generator.py -v`
Expected: 4 PASS.

- [ ] **Step 6: Commit**

```
git add agents/idea_generator.py prompts/idea_prompts.py tests/test_idea_generator.py
git commit -m "feat: idea_generator node + seed trends provider"
```

---

### Task 6: Script writer node

**Files:**
- Create: `prompts/script_prompts.py`, `agents/script_writer.py`
- Test: `tests/test_script_writer.py`

**Interfaces:**
- Consumes: `ContentState` (with `topic` set), `GroqClient`
- Produces:
  - `script_writer_node(state: ContentState, groq: GroqClient) -> ContentState` — sets `state["script"]` to a dict with keys `title, hook, segments (list of {scene_number, duration_sec, voiceover_text, visual_direction, character_visible, emotion}), outro_cta, total_duration_estimate, word_count, hashtags, thumbnail_concept`. On error appends to `errors` and leaves `script={}`.

- [ ] **Step 1: Write `prompts/script_prompts.py`**

```python
def script_system_prompt(niche: str, language: str, fmt: str) -> str:
    length = "45-60 seconds" if fmt == "short" else "8-12 minutes"
    return (
        f"You are an expert {language} scriptwriter for a '{niche}' video channel. "
        f"Write a {fmt} script (~{length}). Hook must land in the first 3 seconds. "
        "Every segment needs a specific visual_direction usable as an image prompt. "
        "Mark character_visible=true only for 1-2 key 'hero' scenes, false otherwise. "
        "Respond ONLY as a JSON object with keys: title, hook, segments "
        "(list of {scene_number, duration_sec, voiceover_text, visual_direction, "
        "character_visible (bool), emotion}), outro_cta, total_duration_estimate, "
        "word_count, hashtags (list), thumbnail_concept."
    )
```

- [ ] **Step 2: Write the failing test**

`tests/test_script_writer.py`:
```python
import json
from orchestrator.state import new_state
from agents.script_writer import script_writer_node

class FakeGroq:
    def __init__(self, payload): self.payload = payload
    def complete(self, system, user, json_mode=False): return self.payload

def _valid_payload():
    return json.dumps({
        "title": "T", "hook": "h",
        "segments": [
            {"scene_number": 1, "duration_sec": 5, "voiceover_text": "v",
             "visual_direction": "dark fort", "character_visible": True, "emotion": "dark"},
            {"scene_number": 2, "duration_sec": 5, "voiceover_text": "v2",
             "visual_direction": "old temple", "character_visible": False, "emotion": "calm"},
        ],
        "outro_cta": "subscribe", "total_duration_estimate": 10,
        "word_count": 40, "hashtags": ["#x"], "thumbnail_concept": "split face",
    })

def test_script_node_sets_script():
    s = new_state("horror", "semi_auto", "hinglish", "short", ["script"])
    s["topic"] = "Cursed village"
    out = script_writer_node(s, groq=FakeGroq(_valid_payload()))
    assert out["script"]["title"] == "T"
    assert len(out["script"]["segments"]) == 2
    assert out["script"]["segments"][0]["character_visible"] is True

def test_script_node_records_error_on_bad_json():
    s = new_state("horror", "semi_auto", "hinglish", "short", ["script"])
    s["topic"] = "x"
    out = script_writer_node(s, groq=FakeGroq("broken"))
    assert out["script"] == {}
    assert out["errors"]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_script_writer.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 4: Write `agents/script_writer.py`**

```python
import json
from orchestrator.state import ContentState
from integrations.groq_client import GroqClient
from prompts.script_prompts import script_system_prompt


def script_writer_node(state: ContentState, groq: GroqClient) -> ContentState:
    try:
        system = script_system_prompt(state["niche"], state["language"], state["format"])
        user = f"Topic: {state['topic']}\nWrite the full script now."
        raw = groq.complete(system=system, user=user, json_mode=True)
        state["script"] = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"script_writer: {e}")
        state["script"] = {}
    return state
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_script_writer.py -v`
Expected: 2 PASS.

- [ ] **Step 6: Commit**

```
git add agents/script_writer.py prompts/script_prompts.py tests/test_script_writer.py
git commit -m "feat: script_writer node"
```

---

### Task 7: Orchestrator graph with HITL gates + SQLite checkpoint

**Files:**
- Create: `orchestrator/graph.py`
- Test: `tests/test_graph.py`

**Interfaces:**
- Consumes: all nodes above, `Notifier` (Task 3)
- Produces:
  - `build_graph(groq, trends, notifier, checkpoint_path=":memory:")` -> compiled LangGraph app exposing `.invoke(state) -> ContentState`
  - Routing: `idea_generator` → (if `"topic"` in `hitl_checkpoints` and mode != `full_auto`) ask approval; on reject, END with `status="failed"`; on approve, set `topic` to top candidate and continue → `script_writer` → (if `"script"` in checkpoints) ask approval → END with `status="complete"` on approve.
  - On approve of topic, `human_approved["topic"]=True` and `state["topic"]=topic_candidates[0]["title"]`.

- [ ] **Step 1: Write the failing test**

`tests/test_graph.py`:
```python
import json
from orchestrator.state import new_state
from orchestrator.graph import build_graph
from agents.idea_generator import SeedTrendsProvider
from modules.notifier import AutoApproveNotifier

class FakeGroq:
    def __init__(self, idea_payload, script_payload):
        self._idea, self._script, self._n = idea_payload, script_payload, 0
    def complete(self, system, user, json_mode=False):
        self._n += 1
        return self._idea if self._n == 1 else self._script

IDEAS = json.dumps({"ideas": [
    {"title": "Best One", "hook": "h", "format": "short", "niche": "horror",
     "tone": "dark", "viral_score": 95}]})
SCRIPT = json.dumps({"title": "Best One", "hook": "h", "segments": [], "outro_cta": "x",
    "total_duration_estimate": 50, "word_count": 100, "hashtags": [], "thumbnail_concept": "y"})

def test_full_run_completes_and_picks_top_topic():
    app = build_graph(groq=FakeGroq(IDEAS, SCRIPT), trends=SeedTrendsProvider(),
                      notifier=AutoApproveNotifier())
    s = new_state("horror", "semi_auto", "hinglish", "short", ["topic", "script"])
    out = app.invoke(s)
    assert out["topic"] == "Best One"
    assert out["script"]["title"] == "Best One"
    assert out["status"] == "complete"

def test_reject_topic_fails_fast():
    class RejectNotifier:
        def ask_approval(self, title, preview): return "reject"
    app = build_graph(groq=FakeGroq(IDEAS, SCRIPT), trends=SeedTrendsProvider(),
                      notifier=RejectNotifier())
    s = new_state("horror", "semi_auto", "hinglish", "short", ["topic", "script"])
    out = app.invoke(s)
    assert out["status"] == "failed"
    assert out["script"] == {}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_graph.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `orchestrator/graph.py`**

```python
from functools import partial
from langgraph.graph import StateGraph, END
from orchestrator.state import ContentState
from agents.idea_generator import idea_generator_node
from agents.script_writer import script_writer_node


def _idea(state, groq, trends):
    return idea_generator_node(state, groq=groq, trends=trends)


def _hitl_topic(state, notifier):
    if "topic" not in state.get("hitl_checkpoints", []) or state["mode"] == "full_auto":
        decision = "approve"
    else:
        top = state["topic_candidates"][0]["title"] if state["topic_candidates"] else "(none)"
        preview = "\n".join(
            f"{i+1}. {c.get('title')} (score {c.get('viral_score')})"
            for i, c in enumerate(state["topic_candidates"])
        ) or "no candidates"
        decision = notifier.ask_approval(f"Pick topic — top: {top}", preview)
    if decision == "approve" and state["topic_candidates"]:
        state["topic"] = state["topic_candidates"][0]["title"]
        state["human_approved"]["topic"] = True
    elif decision != "approve":
        state["status"] = "failed"
    return state


def _route_after_topic(state):
    return "script_writer" if state["status"] != "failed" and state["topic"] else END


def _script(state, groq):
    return script_writer_node(state, groq=groq)


def _hitl_script(state, notifier):
    if "script" in state.get("hitl_checkpoints", []) and state["mode"] != "full_auto":
        decision = notifier.ask_approval("Review script", str(state["script"])[:1500])
        if decision != "approve":
            state["status"] = "failed"
            return state
    state["status"] = "complete"
    return state


def build_graph(groq, trends, notifier, checkpoint_path=":memory:"):
    g = StateGraph(ContentState)
    g.add_node("idea_generator", partial(_idea, groq=groq, trends=trends))
    g.add_node("hitl_topic", partial(_hitl_topic, notifier=notifier))
    g.add_node("script_writer", partial(_script, groq=groq))
    g.add_node("hitl_script", partial(_hitl_script, notifier=notifier))

    g.set_entry_point("idea_generator")
    g.add_edge("idea_generator", "hitl_topic")
    g.add_conditional_edges("hitl_topic", _route_after_topic,
                            {"script_writer": "script_writer", END: END})
    g.add_edge("script_writer", "hitl_script")
    g.add_edge("hitl_script", END)
    return g.compile()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_graph.py -v`
Expected: 2 PASS.

- [ ] **Step 5: Run the whole suite**

Run: `pytest -v`
Expected: all tests from Tasks 1-7 PASS.

- [ ] **Step 6: Commit**

```
git add orchestrator/graph.py tests/test_graph.py
git commit -m "feat: LangGraph orchestrator with HITL gates"
```

---

### Task 8: CLI runner + live smoke test

**Files:**
- Create: `orchestrator/runner.py`
- Test: `tests/test_runner.py`

**Interfaces:**
- Consumes: `build_graph`, `GroqClient`, `SeedTrendsProvider`, `CLINotifier`/`AutoApproveNotifier`, `SETTINGS`
- Produces:
  - `run_job(niche=None, mode=None, fmt="short", auto=False) -> ContentState` — builds real dependencies (Groq from SETTINGS), uses `AutoApproveNotifier` if `auto` else `CLINotifier`, runs the graph, returns final state.
  - `python -m orchestrator.runner` CLI entry that prints the resulting title + first segment count.

- [ ] **Step 1: Write the failing test**

`tests/test_runner.py`:
```python
from orchestrator import runner

def test_run_job_wires_real_graph(monkeypatch):
    import json
    class FakeGroq:
        def __init__(self, *a, **k): self._n = 0
        def complete(self, system, user, json_mode=False):
            self._n += 1
            if self._n == 1:
                return json.dumps({"ideas": [{"title": "Z", "hook": "h", "format": "short",
                    "niche": "tech", "tone": "fun", "viral_score": 80}]})
            return json.dumps({"title": "Z", "hook": "h", "segments": [],
                "outro_cta": "s", "total_duration_estimate": 30, "word_count": 50,
                "hashtags": [], "thumbnail_concept": "t"})
    monkeypatch.setattr(runner, "GroqClient", FakeGroq)
    out = runner.run_job(niche="tech", mode="semi_auto", auto=True)
    assert out["status"] == "complete"
    assert out["topic"] == "Z"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_runner.py -v`
Expected: FAIL with `ModuleNotFoundError` or `AttributeError`.

- [ ] **Step 3: Write `orchestrator/runner.py`**

```python
from config import SETTINGS
from orchestrator.state import new_state
from orchestrator.graph import build_graph
from integrations.groq_client import GroqClient
from agents.idea_generator import SeedTrendsProvider
from modules.notifier import CLINotifier, AutoApproveNotifier


def run_job(niche=None, mode=None, fmt="short", auto=False):
    niche = niche or SETTINGS.default_niche
    mode = mode or SETTINGS.default_mode
    groq = GroqClient()
    notifier = AutoApproveNotifier() if auto else CLINotifier()
    app = build_graph(groq=groq, trends=SeedTrendsProvider(), notifier=notifier)
    state = new_state(niche, mode, SETTINGS.default_language, fmt, ["topic", "script"])
    return app.invoke(state)


if __name__ == "__main__":
    result = run_job()
    title = result.get("script", {}).get("title", "(no script)")
    segs = len(result.get("script", {}).get("segments", []))
    print(f"\nStatus: {result['status']} | Title: {title} | Segments: {segs}")
    if result.get("errors"):
        print("Errors:", result["errors"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_runner.py -v`
Expected: PASS.

- [ ] **Step 5: Live smoke test (requires real GROQ_API_KEY in `.env`)**

Run: `python -m orchestrator.runner`
Expected: prints a real generated topic + script title + segment count. Approve `a` at each prompt. If `GROQ_API_KEY` missing, expect a clear `RuntimeError: GROQ_API_KEY not set` — that is the signal to add the key, not a code bug.

- [ ] **Step 6: Commit**

```
git add orchestrator/runner.py tests/test_runner.py
git commit -m "feat: CLI runner + end-to-end wiring"
```

---

## Self-Review Notes

- **Spec coverage:** orchestrator (LangGraph ✓), state (✓), idea_generator (✓ seed trends now; pytrends/praw deferred to Phase 1.5 per spec §6), script_writer with `character_visible` two-tier signal (✓), HITL pluggable notifier + CLI fallback (✓), multi-domain niche config (✓). Voice/visuals/render/upload are out of Phase 1 scope by design (Phases 2-3).
- **Deferred intentionally:** real trends APIs, SQLite checkpoint persistence across process restarts (graph compiles in-memory now; persistent checkpointer added when async pause/resume HITL lands in Phase 2), WhatsApp notifier adapter.
- **No placeholders:** every step has real code + commands.
- **Type consistency:** `ContentState` keys, `complete(system,user,json_mode)`, `ask_approval(title,preview)`, `fetch(niche)`, node signatures consistent across Tasks 2-8.
