import os
import wave
from integrations.gemini_tts import GeminiTTS, VOICE_MAP


def _pcm(seconds=1.0, rate=24000):
    return b"\x00\x01" * int(rate * seconds)


def test_writes_a_real_wav_file(tmp_path, monkeypatch):
    t = GeminiTTS(api_key="k")
    monkeypatch.setattr(t, "_synth", lambda text, voice: _pcm(0.5))
    out = t.synthesize("रात के साढ़े ग्यारह बजे थे", str(tmp_path / "a.wav"))

    assert os.path.exists(out)
    with wave.open(out, "rb") as w:
        assert w.getnchannels() == 1
        assert w.getframerate() == 24000     # Gemini TTS returns 24kHz mono PCM
        assert w.getnframes() > 0


def test_character_voices_map_to_distinct_gemini_voices(tmp_path, monkeypatch):
    used = []
    t = GeminiTTS(api_key="k")
    monkeypatch.setattr(t, "_synth", lambda text, voice: (used.append(voice), _pcm(0.2))[1])

    t.synthesize("a", str(tmp_path / "1.wav"), voice="am_michael")
    t.synthesize("b", str(tmp_path / "2.wav"), voice="af_heart")
    assert len(set(used)) == 2
    assert all(v in VOICE_MAP.values() for v in used)


def test_unknown_voice_falls_back_to_a_valid_one(tmp_path, monkeypatch):
    used = []
    t = GeminiTTS(api_key="k")
    monkeypatch.setattr(t, "_synth", lambda text, voice: (used.append(voice), _pcm(0.2))[1])
    t.synthesize("x", str(tmp_path / "x.wav"), voice="not_a_real_voice")
    assert used[0] in VOICE_MAP.values()


def test_empty_audio_raises_instead_of_writing_silence(tmp_path, monkeypatch):
    import pytest
    t = GeminiTTS(api_key="k")
    monkeypatch.setattr(t, "_synth", lambda text, voice: b"")
    with pytest.raises(RuntimeError):
        t.synthesize("x", str(tmp_path / "y.wav"))


def test_is_configured():
    assert GeminiTTS(api_key="k").is_configured() is True
    # None = "fall back to .env"; "" = explicitly no key
    assert GeminiTTS(api_key="").is_configured() is False
