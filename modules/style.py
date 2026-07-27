"""Locked art direction per niche.

A series generates its own `style_prompt` once and reuses it across every part — that is what
makes the parts look like one show. A single one-off job had nothing, so each scene came back
looking like a different production. These are the fallback looks, written the way the image
models expect: English, concrete, camera- and light-first.
"""

_LOOKS = {
    "horror": (
        "cinematic horror still, deep shadows, cold desaturated teal and amber, "
        "35mm film grain, shallow depth of field, moonlight and single practical light source"
    ),
    "crime": (
        "gritty crime thriller still, harsh contrast, sodium streetlight orange against "
        "night blue, handheld 35mm look, rain-slick surfaces, heavy film grain"
    ),
    "thriller": (
        "tense thriller still, high contrast low-key lighting, muted colour palette, "
        "anamorphic 35mm look, shallow depth of field"
    ),
    "facts": (
        "clean documentary still, natural daylight, rich saturated colour, sharp focus, "
        "50mm lens, shallow background blur"
    ),
    "nostalgia": (
        "warm nostalgic still, golden hour light, faded 1990s Indian film stock, "
        "soft halation, slight vignette"
    ),
}

_DEFAULT = (
    "cinematic still, dramatic directional lighting, rich contrast, 35mm film look, "
    "shallow depth of field"
)


def style_for_niche(niche: str) -> str:
    return _LOOKS.get((niche or "").lower(), _DEFAULT)
