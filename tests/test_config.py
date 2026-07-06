from config import SETTINGS


def test_settings_has_defaults():
    assert SETTINGS.groq_model
    assert "horror" in SETTINGS.niches
    assert SETTINGS.default_language == "hinglish"
    assert SETTINGS.default_mode in {"full_auto", "semi_auto", "script_only", "manual"}


def test_settings_has_media_defaults():
    assert SETTINGS.kokoro_voice == "af_heart"
    assert SETTINGS.video_width == 1080
    assert SETTINGS.video_height == 1920
    assert SETTINGS.outputs_dir == "outputs"
    assert SETTINGS.character_ref_image_url == ""
    assert "AI" in SETTINGS.ai_disclosure_text
    assert SETTINGS.ai_disclosure_duration_sec == 3.0
