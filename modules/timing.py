"""How long a burned-in text card should stay on screen.

Narrated scenes are timed by measuring the speech. Music-mode scenes have no speech at all, so
the clock is how long it takes to read the card. Below the floor the viewer never registers the
text; above the ceiling the cut drags and the reel loses the pace the reference accounts hold.
"""

_WORDS_PER_SEC = 2.6     # comfortable Devanagari reading speed on a phone
_NOTICE_SEC = 0.8        # time to register that new text appeared before reading starts
_MIN_SEC = 2.2
_MAX_SEC = 4.5


def reading_duration(text: str) -> float:
    words = len((text or "").split())
    raw = _NOTICE_SEC + words / _WORDS_PER_SEC
    return round(min(max(raw, _MIN_SEC), _MAX_SEC), 2)
