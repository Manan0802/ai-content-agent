from modules.voices import VOICE_POOL, assign_voices
from orchestrator.state import new_state
from agents.voiceover import voiceover_node


class FakeTTS:
    def __init__(self):
        self.calls = []

    def synthesize(self, text, output_path, voice=None):
        self.calls.append({"text": text, "path": output_path, "voice": voice})
        return output_path


def test_voice_pool_only_uses_real_kokoro_english_voices():
    # verified live via `npx hyperframes tts --list`
    real = {"af_heart", "af_nova", "af_sky", "am_adam", "am_michael",
            "bf_emma", "bf_isabella", "bm_george"}
    for gender, voices in VOICE_POOL.items():
        assert gender in {"male", "female"}
        assert set(voices) <= real, gender
        assert voices


def test_two_characters_get_different_voices():
    chars = [{"id": "stomach", "voice_hint": "gruff male"},
             {"id": "liver", "voice_hint": "tired old male"}]
    v = assign_voices(chars)
    assert v["stomach"] != v["liver"]


def test_same_character_gets_same_voice_across_calls():
    a = assign_voices([{"id": "stomach", "voice_hint": "gruff male"}])
    b = assign_voices([{"id": "stomach", "voice_hint": "gruff male"},
                       {"id": "heart", "voice_hint": "young female"}])
    assert a["stomach"] == b["stomach"]  # stable across parts of a series


def test_gender_hint_is_respected():
    v = assign_voices([{"id": "a", "voice_hint": "gruff male"},
                       {"id": "b", "voice_hint": "young female"}])
    assert v["a"] in VOICE_POOL["male"]
    assert v["b"] in VOICE_POOL["female"]


def _state_with_script(audio_mode_format):
    s = new_state("horror", "semi_auto", "hindi", "short", ["script"],
                  format_profile=audio_mode_format)
    s["script"] = {
        "characters": [{"id": "stomach", "voice_hint": "gruff male"},
                       {"id": "heart", "voice_hint": "young female"}],
        "segments": [
            {"scene_number": 1, "duration_sec": 5, "speaker": "stomach", "dialogue": "line one"},
            {"scene_number": 2, "duration_sec": 5, "speaker": "heart", "dialogue": "line two"},
        ],
    }
    return s


def test_narrated_mode_uses_per_speaker_voices(tmp_path):
    tts = FakeTTS()
    out = voiceover_node(_state_with_script("drama_50s"), tts=tts, output_dir=str(tmp_path))
    assert len(out["audio_assets"]) == 2
    voices = [c["voice"] for c in tts.calls if c["text"] in ("line one", "line two")]
    assert len(set(voices)) == 2          # two speakers -> two distinct voices
    assert out["voice_map"]["stomach"]


def test_music_mode_skips_tts_entirely(tmp_path):
    tts = FakeTTS()
    out = voiceover_node(_state_with_script("serial_75s"), tts=tts, output_dir=str(tmp_path))
    assert out["audio_assets"] == []
    assert tts.calls == []                # NO voiceover at all in music mode


def test_legacy_script_without_speakers_still_narrates(tmp_path):
    s = new_state("horror", "semi_auto", "hindi", "short", ["script"])
    s["script"] = {"segments": [
        {"scene_number": 1, "duration_sec": 5, "voiceover_text": "legacy line"}]}
    tts = FakeTTS()
    out = voiceover_node(s, tts=tts, output_dir=str(tmp_path))
    assert len(out["audio_assets"]) == 1
    assert tts.calls[0]["text"] == "legacy line"
