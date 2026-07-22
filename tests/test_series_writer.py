import json
from orchestrator.state import new_state
from prompts.series_prompts import series_system_prompt
from agents.series_writer import series_writer_node


class FakeGroq:
    def __init__(self, payload):
        self.payload = payload
        self.last_system = None
        self.last_user = None

    def complete(self, system, user, json_mode=False):
        self.last_system, self.last_user = system, user
        return self.payload


SERIES_PAYLOAD = json.dumps({
    "series_title": "कर्ज़",
    "logline": "एक अमीर आदमी गरीब बनकर सच्चाई ढूँढता है",
    "style_prompt": "semi realistic Indian comic art, moody night lighting, cinematic",
    "characters": [
        {"id": "sheru", "name": "शेरू", "voice_hint": "gruff male",
         "appearance": "tall man, black jacket, beard"},
        {"id": "kalu", "name": "कालू", "voice_hint": "young male",
         "appearance": "short man, white shirt"},
    ],
    "parts": [
        {"part_number": 1, "beat_summary": "शेरू गरीब बनने का फैसला करता है",
         "cliffhanger": "अब असली कहाणी शुरू होगी"},
        {"part_number": 2, "beat_summary": "कालू को शक होता है",
         "cliffhanger": "वो आदमी कौन था?"},
        {"part_number": 3, "beat_summary": "सच्चाई सामने आती है",
         "cliffhanger": "क्या शेरू बच पाएगा?"},
    ],
})


def _state(parts=3, fmt="serial_75s", language="haryanvi"):
    s = new_state("horror", "semi_auto", language, "short", ["series"], format_profile=fmt)
    s["topic"] = "एक अमीर आदमी जो गरीब बन गया"
    s["series_parts"] = parts
    return s


def test_series_node_sets_series_with_all_parts():
    out = series_writer_node(_state(), groq=FakeGroq(SERIES_PAYLOAD))
    series = out["series"]
    assert series["series_title"] == "कर्ज़"
    assert len(series["parts"]) == 3
    assert [p["part_number"] for p in series["parts"]] == [1, 2, 3]


def test_every_part_has_a_cliffhanger():
    out = series_writer_node(_state(), groq=FakeGroq(SERIES_PAYLOAD))
    for p in out["series"]["parts"]:
        assert p["cliffhanger"].strip()


def test_characters_and_style_are_shared_across_the_series():
    out = series_writer_node(_state(), groq=FakeGroq(SERIES_PAYLOAD))
    series = out["series"]
    assert series["style_prompt"]                       # one locked art style for all parts
    assert [c["id"] for c in series["characters"]] == ["sheru", "kalu"]
    assert all(c.get("appearance") for c in series["characters"])


def test_series_id_is_set():
    out = series_writer_node(_state(), groq=FakeGroq(SERIES_PAYLOAD))
    assert out["series_id"]


def test_prompt_carries_part_count_format_and_language():
    g = FakeGroq(SERIES_PAYLOAD)
    series_writer_node(_state(parts=5, fmt="serial_75s", language="haryanvi"), groq=g)
    assert "5" in g.last_system
    assert "75" in g.last_system                       # target duration per part
    assert "haryanvi" in g.last_system.lower()


def test_prompt_demands_cliffhangers_and_locked_style():
    p = series_system_prompt(niche="horror", language="haryanvi",
                             format_name="serial_75s", parts=3)
    low = p.lower()
    assert "cliffhanger" in low
    assert "style_prompt" in low
    assert "appearance" in low                         # so characters stay consistent


def test_bad_json_records_error_and_leaves_series_empty():
    out = series_writer_node(_state(), groq=FakeGroq("not json"))
    assert out["series"] == {}
    assert out["errors"]


def test_fewer_parts_than_requested_is_recorded_not_crashed():
    short = json.dumps({
        "series_title": "T", "logline": "l", "style_prompt": "s",
        "characters": [{"id": "a", "name": "A", "voice_hint": "male", "appearance": "x"}],
        "parts": [{"part_number": 1, "beat_summary": "b", "cliffhanger": "c"}],
    })
    out = series_writer_node(_state(parts=3), groq=FakeGroq(short))
    assert len(out["series"]["parts"]) == 1
    assert any("expected 3" in e for e in out["errors"])
