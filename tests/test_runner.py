from orchestrator import runner


def test_run_job_wires_real_graph(monkeypatch):
    import json

    class FakeGroq:
        def __init__(self, *a, **k):
            self._n = 0

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
