"""Locked art direction per niche.

A series generates its own `style_prompt` once and reuses it across every part — that is what
makes the parts look like one show. A single one-off job had nothing, so each scene came back
looking like a different production. These are the fallback looks, written the way the image
models expect: English, concrete, camera- and light-first.
"""

_LOOKS = {
    "horror": (
        "cinematic horror still, deep shadows with a single hard light source, cold desaturated "
        "teal and amber grade, 35mm film grain, shallow depth of field"
    ),
    "crime": (
        "gritty crime thriller still, harsh contrast, cold blue shadows against warm practical "
        "light, handheld 35mm look, heavy film grain"
    ),
    "thriller": (
        "tense thriller still, high contrast low-key lighting, muted colour palette, "
        "anamorphic 35mm look, shallow depth of field"
    ),
    "facts": (
        "clean documentary still, soft even light, rich saturated colour, sharp focus, "
        "50mm lens, shallow background blur"
    ),
    # anthropomorphic organs/food arguing — the aihealthstudio764 template (8.6M views)
    "health": (
        "Pixar style 3D animation still, glossy character render with large expressive eyes, "
        "warm dramatic key light, rich saturated colour, shallow depth of field"
    ),
    "nostalgia": (
        "warm nostalgic still, soft low-angle light, faded 1990s Indian film stock, "
        "soft halation, slight vignette, 35mm grain"
    ),
}

_DEFAULT = (
    "cinematic still, dramatic directional lighting, rich contrast, 35mm film look, "
    "shallow depth of field"
)

# NOTE: a look is pasted into every image prompt in the video, so it must describe only the
# GRADE, LENS and GRAIN. Naming a place or weather ("streetlight", "rain-slick") forces every
# indoor scene outdoors — see tests/test_style_lock.py.


def style_for_niche(niche: str) -> str:
    return _LOOKS.get((niche or "").lower(), _DEFAULT)
