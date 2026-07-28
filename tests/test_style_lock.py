"""A style lock is pasted into EVERY image prompt in a video, so anything it names becomes
mandatory in every frame. That is exactly what you want for grade, lens and grain — and exactly
what you must not do with a location.

Found the hard way: the crime look said "sodium streetlight orange" and "rain-slick surfaces",
so a phone on a table indoors rendered as a phone on a wet street, and a police officer in a dark
room rendered outdoors under a streetlight. Three of eleven cards contradicted their own line.
"""
import re
import pytest
from modules.style import style_for_niche, _LOOKS

# words that pin a scene to a place or weather — a per-scene decision, never a series-wide one
_SETTING_WORDS = [
    "street", "streetlight", "rain", "rain-slick", "wet", "road", "indoor", "outdoor",
    "moonlight", "window", "forest", "city", "room", "sky",
]


def _setting_words_in(look: str) -> list[str]:
    # whole words only — "grain" must not trip the "rain" check
    return [w for w in _SETTING_WORDS if re.search(rf"\b{re.escape(w)}\b", look)]


@pytest.mark.parametrize("niche", sorted(_LOOKS))
def test_a_look_never_dictates_where_the_scene_happens(niche):
    look = style_for_niche(niche).lower()
    found = _setting_words_in(look)
    assert not found, (
        f"{niche} look pins the setting via {found} — it will drag every indoor scene outdoors"
    )


def test_the_fallback_look_is_also_setting_free():
    assert not _setting_words_in(style_for_niche("unknown-niche").lower())


@pytest.mark.parametrize("niche", sorted(_LOOKS))
def test_a_look_still_actually_directs_the_image(niche):
    """Stripping the setting must not leave it so vague it stops locking anything."""
    look = style_for_niche(niche).lower()
    assert len(look) > 40
    assert any(w in look for w in ["grain", "lens", "mm", "contrast", "depth of field"])
