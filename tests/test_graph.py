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


class FakeFal:
    def generate_hero_image(self, prompt, ref):
        return "https://x/hero.png"

    def generate_broll_image(self, prompt):
        return "https://x/broll.png"


class FakeTTS:
    def synthesize(self, text, output_path, voice=None):
        return output_path


class FakeCLI:
    def lint(self, d):
        pass

    def validate(self, d):
        pass

    def inspect(self, d):
        pass

    def render(self, d, out, quality="high"):
        pass


class FakeYouTube:
    def is_configured(self):
        return True

    def upload_video(self, file_path, title, description, tags, privacy="unlisted"):
        return "vid123"


IDEAS = json.dumps({"ideas": [
    {"title": "Best One", "hook": "h", "format": "short", "niche": "horror",
     "tone": "dark", "viral_score": 95}]})
SCRIPT = json.dumps({"title": "Best One", "hook": "h", "segments": [], "outro_cta": "x",
    "total_duration_estimate": 50, "word_count": 100, "hashtags": [], "thumbnail_concept": "y"})
SCRIPT_WITH_SEGMENTS = json.dumps({"title": "Best One", "hook": "h", "segments": [
    {"scene_number": 1, "duration_sec": 5, "voiceover_text": "v1",
     "visual_direction": "dark fort", "character_visible": True, "emotion": "dark"},
], "outro_cta": "x", "total_duration_estimate": 50, "word_count": 100,
    "hashtags": [], "thumbnail_concept": "y"})


def test_full_run_completes_and_picks_top_topic(tmp_path, monkeypatch):
    import agents.render as render_mod
    monkeypatch.setattr(render_mod, "_exists", lambda p: True)
    monkeypatch.setattr(render_mod, "_getsize", lambda p: 1024)

    app = build_graph(groq=FakeGroq(IDEAS, SCRIPT), trends=SeedTrendsProvider(),
                      notifier=AutoApproveNotifier(), fal=FakeFal(), tts=FakeTTS(),
                      hf_cli=FakeCLI(), project_dir=str(tmp_path))
    s = new_state("horror", "semi_auto", "hinglish", "short", ["topic", "script"])
    out = app.invoke(s)
    assert out["topic"] == "Best One"
    assert out["script"]["title"] == "Best One"
    assert out["status"] == "media_complete"
    assert out["render_output_path"]


def test_reject_topic_fails_fast():
    class RejectNotifier:
        def ask_approval(self, title, preview):
            return "reject"

    app = build_graph(groq=FakeGroq(IDEAS, SCRIPT), trends=SeedTrendsProvider(),
                      notifier=RejectNotifier())
    s = new_state("horror", "semi_auto", "hinglish", "short", ["topic", "script"])
    out = app.invoke(s)
    assert out["status"] == "failed"
    assert out["script"] == {}


def test_full_run_produces_rendered_video(monkeypatch, tmp_path):
    import agents.render as render_mod
    monkeypatch.setattr(render_mod, "_exists", lambda p: True)
    monkeypatch.setattr(render_mod, "_getsize", lambda p: 1024)

    app = build_graph(groq=FakeGroq(IDEAS, SCRIPT_WITH_SEGMENTS), trends=SeedTrendsProvider(),
                      notifier=AutoApproveNotifier(), fal=FakeFal(), tts=FakeTTS(),
                      hf_cli=FakeCLI(), project_dir=str(tmp_path))
    s = new_state("horror", "semi_auto", "hinglish", "short",
                  ["topic", "script", "render"])
    out = app.invoke(s)
    assert out["status"] == "media_complete"
    assert out["render_output_path"]


def test_full_run_publishes_when_youtube_configured(monkeypatch, tmp_path):
    import agents.render as render_mod
    monkeypatch.setattr(render_mod, "_exists", lambda p: True)
    monkeypatch.setattr(render_mod, "_getsize", lambda p: 1024)

    app = build_graph(groq=FakeGroq(IDEAS, SCRIPT_WITH_SEGMENTS), trends=SeedTrendsProvider(),
                      notifier=AutoApproveNotifier(), fal=FakeFal(), tts=FakeTTS(),
                      hf_cli=FakeCLI(), youtube=FakeYouTube(), project_dir=str(tmp_path))
    s = new_state("horror", "semi_auto", "hinglish", "short",
                  ["topic", "script", "render", "publish"])
    out = app.invoke(s)
    assert out["status"] == "published"
    assert out["youtube_url"] == "https://youtu.be/vid123"
