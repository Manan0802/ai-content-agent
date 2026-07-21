from orchestrator import runner


class FakeGroq:
    def __init__(self, *a, **k):
        self._n = 0

    def complete(self, system, user, json_mode=False):
        import json
        self._n += 1
        if self._n == 1:
            return json.dumps({"ideas": [{"title": "Z", "hook": "h", "format": "short",
                "niche": "tech", "tone": "fun", "viral_score": 80}]})
        return json.dumps({"title": "Z", "hook": "h", "segments": [
            {"scene_number": 1, "duration_sec": 5, "voiceover_text": "v1",
             "visual_direction": "a robot", "character_visible": True, "emotion": "fun"},
        ], "outro_cta": "s", "total_duration_estimate": 30, "word_count": 50,
            "hashtags": [], "thumbnail_concept": "t"})


class FakeFal:
    def __init__(self, *a, **k):
        pass

    def generate_hero_image(self, prompt, ref):
        return "https://x/hero.png"

    def generate_broll_image(self, prompt):
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
        return True

    def upload_video(self, file_path, title, description, tags, privacy="unlisted"):
        return "vid123"


def test_run_job_wires_real_graph(monkeypatch):
    monkeypatch.setattr(runner, "GroqClient", FakeGroq)
    monkeypatch.setattr(runner, "FalClient", FakeFal)
    monkeypatch.setattr(runner, "PollinationsClient", FakeFal)  # whichever provider config picks
    monkeypatch.setattr(runner, "HyperFramesTTS", FakeTTS)
    monkeypatch.setattr(runner, "HyperFramesCLI", FakeCLI)
    monkeypatch.setattr(runner, "YouTubeClient", FakeYouTube)
    import agents.render as render_mod
    monkeypatch.setattr(render_mod.os.path, "exists", lambda p: True)
    monkeypatch.setattr(render_mod.os.path, "getsize", lambda p: 1024)

    saved = {}
    monkeypatch.setattr(runner, "save_job",
                        lambda state, outputs_dir: saved.update(state=state))

    out = runner.run_job(niche="tech", mode="semi_auto", auto=True)
    assert out["status"] == "published"
    assert out["topic"] == "Z"
    assert out["render_output_path"]
    assert out["youtube_url"] == "https://youtu.be/vid123"
    assert saved["state"]["job_id"] == out["job_id"]  # runner persisted the job
