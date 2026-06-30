import json
from orchestrator.state import new_state
from agents.idea_generator import idea_generator_node, SeedTrendsProvider


class FakeGroq:
    def __init__(self, payload):
        self.payload = payload

    def complete(self, system, user, json_mode=False):
        return self.payload


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
