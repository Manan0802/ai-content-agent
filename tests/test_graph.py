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
        def ask_approval(self, title, preview):
            return "reject"

    app = build_graph(groq=FakeGroq(IDEAS, SCRIPT), trends=SeedTrendsProvider(),
                      notifier=RejectNotifier())
    s = new_state("horror", "semi_auto", "hinglish", "short", ["topic", "script"])
    out = app.invoke(s)
    assert out["status"] == "failed"
    assert out["script"] == {}
