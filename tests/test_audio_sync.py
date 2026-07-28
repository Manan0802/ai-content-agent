from orchestrator.state import new_state
from agents.voiceover import voiceover_node


class FakeTTS:
    """Writes a file and reports a length that is deliberately NOT what the script guessed."""
    def __init__(self, durations):
        self.durations = durations
        self.i = 0

    def synthesize(self, text, output_path, voice=None):
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(b"\x00" * 4096)
        return output_path


def _state():
    s = new_state("horror", "semi_auto", "hindi", "short", [], format_profile="drama_50s")
    s["script"] = {
        "characters": [{"id": "a", "voice_hint": "male"}],
        "segments": [
            # the LLM guessed 5s and 5s; the real speech is 7.2s and 2.1s
            {"scene_number": 1, "duration_sec": 5, "speaker": "a", "dialogue": "लंबी लाइन"},
            {"scene_number": 2, "duration_sec": 5, "speaker": "a", "dialogue": "छोटी"},
        ],
    }
    return s


def test_scene_duration_is_taken_from_the_real_audio_not_the_llm_guess(tmp_path):
    """The LLM's duration_sec is a guess. If the slot doesn't match the actual speech, the
    image cuts while the voice is still talking (or sits in dead air after it)."""
    s = voiceover_node(_state(), tts=FakeTTS(None), output_dir=str(tmp_path),
                       probe=lambda p: {"scene_1.wav": 7.2, "scene_2.wav": 2.1}[p.split("/")[-1]])

    segs = s["script"]["segments"]
    assert segs[0]["duration_sec"] > 7.0     # was 5, real speech is 7.2
    assert segs[1]["duration_sec"] < 3.0     # was 5, real speech is 2.1


def test_a_small_breath_is_added_after_each_line(tmp_path):
    s = voiceover_node(_state(), tts=FakeTTS(None), output_dir=str(tmp_path),
                       probe=lambda p: 4.0, tail_sec=0.25)
    for seg in s["script"]["segments"]:
        # long enough to not clip the voice, short enough not to feel like dead air
        assert 4.0 < seg["duration_sec"] <= 4.5


def test_audio_assets_record_the_measured_duration(tmp_path):
    s = voiceover_node(_state(), tts=FakeTTS(None), output_dir=str(tmp_path),
                       probe=lambda p: 3.3)
    assert all(a["duration_sec"] == 3.3 for a in s["audio_assets"])


def test_unmeasurable_audio_keeps_the_script_duration(tmp_path):
    def bad_probe(path):
        raise RuntimeError("ffprobe missing")

    s = voiceover_node(_state(), tts=FakeTTS(None), output_dir=str(tmp_path), probe=bad_probe)
    assert s["script"]["segments"][0]["duration_sec"] == 5     # falls back, doesn't crash
    assert any("duration" in e for e in s.get("errors", []))


def test_music_mode_never_uses_the_audio_probe(tmp_path):
    """There is no voiceover in music mode, so there is nothing to measure — those cards are
    timed by reading speed instead (see tests/test_music_mode_timing.py)."""
    s = new_state("horror", "semi_auto", "hindi", "short", [], format_profile="serial_75s")
    s["script"] = {"characters": [], "segments": [
        {"scene_number": 1, "duration_sec": 6, "dialogue": "text only"}]}

    def exploding_probe(path):
        raise AssertionError("music mode must not probe audio")

    out = voiceover_node(s, tts=FakeTTS(None), output_dir=str(tmp_path), probe=exploding_probe)
    assert out["audio_assets"] == []
    assert out["script"]["segments"][0]["duration_sec"] != 6   # re-timed from the text
