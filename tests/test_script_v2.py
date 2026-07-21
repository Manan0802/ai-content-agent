import json
from modules.formats import get_format
from orchestrator.state import new_state
from prompts.script_prompts import script_system_prompt
from agents.script_writer import script_writer_node


class FakeGroq:
    def __init__(self, payload):
        self.payload = payload
        self.last_system = None

    def complete(self, system, user, json_mode=False):
        self.last_system = system
        return self.payload


V2_PAYLOAD = json.dumps({
    "title": "रोज़-रोज़ मोमोज़?",
    "hook": "क्या आप भी रोज़ मोमोज़ खाते हैं?",
    "characters": [
        {"id": "stomach", "name": "पेट", "voice_hint": "gruff male"},
        {"id": "liver", "name": "लिवर", "voice_hint": "tired old male"},
    ],
    "segments": [
        {"scene_number": 1, "duration_sec": 6, "speaker": "stomach",
         "dialogue": "अरे यार, ये कितनी चौमिन खाती है रे",
         "visual_direction": "angry cartoon stomach", "character_visible": True},
        {"scene_number": 2, "duration_sec": 6, "speaker": "liver",
         "dialogue": "मेरे सारे फिल्टर भर चुके हैं",
         "visual_direction": "tired cartoon liver", "character_visible": False},
    ],
    "cliffhanger": "अब असली कहानी शुरू होगी",
    "outro_cta": "फॉलो करो", "hashtags": ["#health"],
})


def _state(fmt="drama_50s", language="hindi"):
    s = new_state("horror", "semi_auto", language, "short", ["script"])
    s["topic"] = "मोमोज़"
    s["format_profile"] = fmt
    return s


def test_script_v2_parses_characters_and_speaker_dialogue():
    out = script_writer_node(_state(), groq=FakeGroq(V2_PAYLOAD))
    sc = out["script"]
    assert [c["id"] for c in sc["characters"]] == ["stomach", "liver"]
    assert sc["segments"][0]["speaker"] == "stomach"
    assert "चौमिन" in sc["segments"][0]["dialogue"]
    assert sc["cliffhanger"]


def test_prompt_is_format_aware():
    p = get_format("drama_50s")
    sysmsg = script_system_prompt("horror", "hindi", profile=p)
    assert "50" in sysmsg                      # target duration
    assert "6" in sysmsg and "9" in sysmsg     # segment range
    assert "5" in sysmsg                       # max characters
    assert "narrated" in sysmsg or "voice" in sysmsg.lower()


def test_prompt_is_language_aware_for_regional():
    p = get_format("serial_75s")
    hary = script_system_prompt("horror", "haryanvi", profile=p)
    assert "haryanvi" in hary.lower()
    assert "devanagari" in hary.lower()
    # music mode must tell the model there is no voiceover
    assert "music" in hary.lower() or "no voiceover" in hary.lower()


def test_script_writer_passes_format_profile_into_prompt():
    g = FakeGroq(V2_PAYLOAD)
    script_writer_node(_state(fmt="joke_10s"), groq=g)
    assert "11" in g.last_system or "10" in g.last_system  # joke duration reached the prompt


def test_old_script_without_characters_still_works():
    legacy = json.dumps({"title": "T", "hook": "h", "segments": [
        {"scene_number": 1, "duration_sec": 5, "voiceover_text": "v",
         "visual_direction": "d", "character_visible": False}],
        "outro_cta": "x", "hashtags": []})
    out = script_writer_node(_state(), groq=FakeGroq(legacy))
    assert out["script"]["segments"][0]["voiceover_text"] == "v"
    assert out["script"].get("characters", []) == []


def test_bad_json_records_error():
    out = script_writer_node(_state(), groq=FakeGroq("not json"))
    assert out["script"] == {}
    assert out["errors"]
