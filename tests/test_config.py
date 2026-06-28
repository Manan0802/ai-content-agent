from config import SETTINGS


def test_settings_has_defaults():
    assert SETTINGS.groq_model
    assert "horror" in SETTINGS.niches
    assert SETTINGS.default_language == "hinglish"
    assert SETTINGS.default_mode in {"full_auto", "semi_auto", "script_only", "manual"}
