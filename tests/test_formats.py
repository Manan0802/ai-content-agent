import pytest
from modules.formats import FORMATS, get_format, FormatProfile


def test_all_four_profiles_exist():
    assert set(FORMATS) == {"joke_10s", "montage_35s", "drama_50s", "serial_75s"}


def test_profiles_have_sane_values():
    for name, p in FORMATS.items():
        assert isinstance(p, FormatProfile)
        assert p.name == name
        assert 5 <= p.target_duration_sec <= 120, name
        lo, hi = p.segment_range
        assert 1 <= lo <= hi <= 15, name
        assert p.audio_mode in {"narrated", "music"}, name
        assert p.description


def test_music_profiles_have_no_tts_characters():
    # music mode uses on-screen dialogue + BGM, so no TTS voices are assigned
    for p in FORMATS.values():
        if p.audio_mode == "music":
            assert p.max_characters == 0, p.name
        else:
            assert p.max_characters >= 2, p.name


def test_durations_match_the_measured_reference_reels():
    # from docs/superpowers/specs/2026-07-21-audio-analysis.md
    assert FORMATS["joke_10s"].target_duration_sec <= 12       # 900K reel was 10.8s
    assert 30 <= FORMATS["montage_35s"].target_duration_sec <= 38   # 1.7M reel was 34.0s
    assert 45 <= FORMATS["drama_50s"].target_duration_sec <= 55     # 8.6M reel was 50.5s
    assert 60 <= FORMATS["serial_75s"].target_duration_sec <= 91    # 453K reel was 91s


def test_get_format_returns_profile_and_rejects_unknown():
    assert get_format("drama_50s").audio_mode == "narrated"
    assert get_format("serial_75s").audio_mode == "music"
    with pytest.raises(ValueError):
        get_format("nope")


def test_settings_expose_format_and_language_defaults():
    from config import SETTINGS
    assert SETTINGS.default_format in FORMATS
    assert "haryanvi" in SETTINGS.supported_languages
    assert "punjabi" in SETTINGS.supported_languages
    assert "hindi" in SETTINGS.supported_languages
