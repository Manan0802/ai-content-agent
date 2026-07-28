"""Music mode has no voiceover, so there is no audio to measure — the LLM's duration_sec is
the only timing and it is just as much a guess as it was in narrated mode. A 3-word line and a
14-word line both came back as "5 seconds", so short cards dragged and long ones flashed past
before anyone could read them.

Reading time is the right clock here: the viewer's only job is to read the burned-in text.
"""
from modules.timing import reading_duration
from agents.voiceover import voiceover_node
from orchestrator.state import new_state


class FakeTTS:
    def synthesize(self, text, output_path, voice=None):
        raise AssertionError("music mode must never call TTS")


def test_a_longer_line_gets_more_time_on_screen():
    short = reading_duration("वो वापस आ गया")
    long = reading_duration("पुलिस ने कहा कि लाश तीन दिन पुरानी है और कोई गवाह नहीं")
    assert long > short


def test_even_a_two_word_card_stays_long_enough_to_notice():
    assert reading_duration("भागो") >= 2.0


def test_a_very_long_line_is_capped_so_the_cut_never_drags():
    huge = reading_duration(" ".join(["शब्द"] * 60))
    assert huge <= 4.5


def test_music_mode_retimes_every_scene_from_its_text():
    s = new_state("crime", "semi_auto", "hindi", "short", [], format_profile="serial_75s")
    s["script"] = {"characters": [], "segments": [
        {"scene_number": 1, "duration_sec": 5, "dialogue": "भागो"},
        {"scene_number": 2, "duration_sec": 5,
         "dialogue": "पुलिस ने कहा कि लाश तीन दिन पुरानी है और कोई गवाह नहीं"},
    ]}
    out = voiceover_node(s, tts=FakeTTS(), output_dir="/tmp/unused")

    d1, d2 = (seg["duration_sec"] for seg in out["script"]["segments"])
    assert d1 != 5 and d2 != 5          # both re-timed, neither left at the guess
    assert d2 > d1                       # the longer card gets the longer slot
