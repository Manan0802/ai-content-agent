import json
from orchestrator import series_runner


SERIES_JSON = json.dumps({
    "series_title": "कर्ज़", "logline": "l",
    "style_prompt": "semi realistic Indian comic art, moody night",
    "characters": [{"id": "sheru", "name": "शेरू", "voice_hint": "gruff male",
                    "appearance": "tall man, black jacket, beard"}],
    "parts": [
        {"part_number": 1, "beat_summary": "b1", "cliffhanger": "c1"},
        {"part_number": 2, "beat_summary": "b2", "cliffhanger": "c2"},
        {"part_number": 3, "beat_summary": "b3", "cliffhanger": "c3"},
    ],
})

PART_SCRIPT = json.dumps({
    "title": "कर्ज़ Part", "hook": "h",
    "characters": [{"id": "sheru", "name": "शेरू", "voice_hint": "gruff male"}],
    "segments": [{"scene_number": 1, "duration_sec": 6, "speaker": "sheru",
                  "dialogue": "मन्ने कुछ दिन गरीब बनके जीणा से",
                  "visual_direction": "dark street", "character_visible": True}],
    "cliffhanger": "अब असली कहाणी शुरू होगी", "outro_cta": "x", "hashtags": [],
})


class FakeGroq:
    """First call = series plan, every later call = a part script."""
    def __init__(self, *a, **k):
        self.n = 0
        self.prompts = []

    def complete(self, system, user, json_mode=False):
        self.n += 1
        self.prompts.append(user)
        return SERIES_JSON if self.n == 1 else PART_SCRIPT


class FakeFal:
    def __init__(self, *a, **k):
        self.prompts = []

    def generate_hero_image(self, prompt, ref):
        self.prompts.append(prompt)
        return "https://x/hero.png"

    def generate_broll_image(self, prompt):
        self.prompts.append(prompt)
        return "https://x/broll.png"


class FakeTTS:
    def __init__(self, *a, **k):
        pass

    def synthesize(self, text, output_path, voice=None):
        return output_path


class FakeCLI:
    def __init__(self, *a, **k):
        pass

    def lint(self, d):
        pass

    def validate(self, d):
        pass

    def inspect(self, d):
        pass

    def render(self, d, out, quality="high"):
        pass


class FakeYouTube:
    def __init__(self, *a, **k):
        pass

    def is_configured(self):
        return False          # skip upload in tests


def _patch(monkeypatch, fal=None):
    monkeypatch.setattr(series_runner, "GroqClient", FakeGroq)
    monkeypatch.setattr(series_runner, "FalClient", fal or FakeFal)
    monkeypatch.setattr(series_runner, "PollinationsClient", fal or FakeFal)
    monkeypatch.setattr(series_runner, "HyperFramesTTS", FakeTTS)
    monkeypatch.setattr(series_runner, "HyperFramesCLI", FakeCLI)
    monkeypatch.setattr(series_runner, "YouTubeClient", FakeYouTube)
    monkeypatch.setattr(series_runner, "save_job", lambda state, outputs_dir: None)
    import agents.render as render_mod
    monkeypatch.setattr(render_mod, "_exists", lambda p: True)
    monkeypatch.setattr(render_mod, "_getsize", lambda p: 1024)


def test_run_series_produces_one_state_per_part(monkeypatch, tmp_path):
    _patch(monkeypatch)
    out = series_runner.run_series(topic="एक अमीर आदमी", parts=3, auto=True,
                                   outputs_dir=str(tmp_path))
    assert len(out["parts"]) == 3
    assert [s["part_number"] for s in out["parts"]] == [1, 2, 3]


def test_all_parts_share_one_series_id(monkeypatch, tmp_path):
    _patch(monkeypatch)
    out = series_runner.run_series(topic="t", parts=3, auto=True, outputs_dir=str(tmp_path))
    ids = {s["series_id"] for s in out["parts"]}
    assert len(ids) == 1 and ids != {""}


def test_locked_style_prompt_is_applied_to_every_image(monkeypatch, tmp_path):
    fal = FakeFal()
    _patch(monkeypatch, fal=lambda *a, **k: fal)
    series_runner.run_series(topic="t", parts=3, auto=True, outputs_dir=str(tmp_path))
    assert fal.prompts, "no images generated"
    # the one locked art direction must appear in every single image prompt
    assert all("moody night" in p for p in fal.prompts)


def test_part_context_is_passed_into_each_part(monkeypatch, tmp_path):
    _patch(monkeypatch)
    out = series_runner.run_series(topic="t", parts=3, auto=True, outputs_dir=str(tmp_path))
    p1_brief, p2_brief = out["parts"][0]["topic"], out["parts"][1]["topic"]

    assert "b2" in p2_brief                              # part 2 gets its own beat
    assert "PART 2 of 3" in p2_brief
    # part 2 must pay off what part 1's SCRIPT actually ended on (what the viewer heard),
    # not merely what the outline planned
    assert "अब असली कहाणी शुरू होगी" in p2_brief
    assert "PAYING OFF" not in p1_brief                  # part 1 has nothing to pay off
    assert "b1" in p1_brief


def test_each_part_gets_its_own_output_dir(monkeypatch, tmp_path):
    _patch(monkeypatch)
    out = series_runner.run_series(topic="t", parts=3, auto=True, outputs_dir=str(tmp_path))
    dirs = {s["composition_path"].rsplit("/", 1)[0] for s in out["parts"]}
    assert len(dirs) == 3


def test_series_failure_records_error_and_returns_empty_parts(monkeypatch, tmp_path):
    class BadGroq(FakeGroq):
        def complete(self, system, user, json_mode=False):
            return "not json"
    _patch(monkeypatch)
    monkeypatch.setattr(series_runner, "GroqClient", BadGroq)
    out = series_runner.run_series(topic="t", parts=3, auto=True, outputs_dir=str(tmp_path))
    assert out["parts"] == []
    assert out["errors"]
