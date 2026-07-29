"""Edge ships exactly two Hindi neural voices — Madhur (male) and Swara (female). The 8.6M-view
reference reel is four characters arguing, and if two of them sound identical the format falls
apart: the viewer stops tracking who is speaking.

`assign_voices` already hands out 8 distinct ids, but they all collapsed onto those two voices.
Pitch and rate are what separate them — a slower, lower Madhur reads as an older man; a faster,
higher Swara reads as a young girl. Same engine, audibly different characters.
"""
import pytest
from integrations.edge_tts_client import EdgeTTS, profile_for
from modules.voices import VOICE_POOL


ALL_IDS = VOICE_POOL["male"] + VOICE_POOL["female"]


@pytest.mark.parametrize("vid", ALL_IDS)
def test_every_assignable_voice_has_a_profile(vid):
    base, rate, pitch = profile_for(vid)
    assert base in ("hi-IN-MadhurNeural", "hi-IN-SwaraNeural")
    assert rate.endswith("%") and (pitch.endswith("Hz"))


def test_gender_survives_the_mapping():
    for vid in VOICE_POOL["male"]:
        assert profile_for(vid)[0] == "hi-IN-MadhurNeural"
    for vid in VOICE_POOL["female"]:
        assert profile_for(vid)[0] == "hi-IN-SwaraNeural"


def test_no_two_characters_end_up_sounding_the_same():
    profiles = [profile_for(v) for v in ALL_IDS]
    assert len(set(profiles)) == len(profiles)


def test_an_unknown_voice_id_still_speaks():
    base, rate, pitch = profile_for("something-unmapped")
    assert base in ("hi-IN-MadhurNeural", "hi-IN-SwaraNeural")


def test_synthesize_uses_the_characters_own_pitch_and_rate(tmp_path):
    seen = {}

    class Spy(EdgeTTS):
        def _speak(self, text, voice, dest, rate, pitch):
            seen[voice] = (rate, pitch)
            open(dest, "wb").write(b"x" * 2048)

    tts = Spy()
    tts.synthesize("नमस्ते", str(tmp_path / "a.wav"), voice="am_adam")
    tts.synthesize("नमस्ते", str(tmp_path / "b.wav"), voice="bm_george")

    # both are Madhur, but they must not be read with identical settings
    assert len(seen) == 1                        # same base voice…
    assert profile_for("am_adam")[1:] != profile_for("bm_george")[1:]   # …different delivery
