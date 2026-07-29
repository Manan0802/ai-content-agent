import os
from integrations.edge_tts_client import EdgeTTS, VOICE_MAP


def test_hindi_voices_are_the_native_ones():
    # hi-IN-* are actual Hindi-trained neural voices — Kokoro is an English model
    # phonemising Devanagari, which is why it sounds wrong.
    assert set(VOICE_MAP.values()) >= {"hi-IN-MadhurNeural", "hi-IN-SwaraNeural"}


def test_writes_audio_file(tmp_path, monkeypatch):
    t = EdgeTTS()
    monkeypatch.setattr(t, "_speak", lambda text, voice, dest, rate, pitch: open(dest, "wb").write(b"\xff\xfb" + b"\x00" * 4096))
    out = t.synthesize("रात के साढ़े ग्यारह बजे थे", str(tmp_path / "a.wav"))
    assert os.path.exists(out) and os.path.getsize(out) > 1024


def test_male_and_female_map_to_different_hindi_voices(tmp_path, monkeypatch):
    used = []
    t = EdgeTTS()
    monkeypatch.setattr(t, "_speak",
                        lambda text, voice, dest, rate, pitch: (
                            used.append(voice), open(dest, "wb").write(b"\x00" * 2048))[1])
    t.synthesize("a", str(tmp_path / "1.wav"), voice="am_michael")   # male
    t.synthesize("b", str(tmp_path / "2.wav"), voice="af_heart")     # female
    assert used == ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]


def test_unknown_voice_falls_back(tmp_path, monkeypatch):
    used = []
    t = EdgeTTS()
    monkeypatch.setattr(t, "_speak",
                        lambda text, voice, dest, rate, pitch: (
                            used.append(voice), open(dest, "wb").write(b"\x00" * 2048))[1])
    t.synthesize("x", str(tmp_path / "x.wav"), voice="nope")
    assert used[0] in VOICE_MAP.values()


def test_empty_output_raises(tmp_path, monkeypatch):
    import pytest
    t = EdgeTTS()
    monkeypatch.setattr(t, "_speak", lambda text, voice, dest, rate, pitch: open(dest, "wb").write(b""))
    with pytest.raises(RuntimeError):
        t.synthesize("x", str(tmp_path / "y.wav"))


def test_is_configured_needs_no_key():
    # the whole point: free, no API key, unlimited
    assert EdgeTTS().is_configured() is True
