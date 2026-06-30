import json
from orchestrator.state import new_state
from agents.script_writer import script_writer_node


class FakeGroq:
    def __init__(self, payload):
        self.payload = payload

    def complete(self, system, user, json_mode=False):
        return self.payload


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
