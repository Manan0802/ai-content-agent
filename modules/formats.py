"""Format profiles — how long a video is, how many scenes, and how it carries its audio.

Every number here comes from measured reference reels, not guesses. See
`docs/superpowers/specs/2026-07-21-audio-analysis.md`:

    joke_10s     krjha_fivestar        10.8s   900K likes   two-line punchline
    montage_35s  chitrakatha_nostalgia 34.0s   1.7M likes   song + imagery, one spoken line
    drama_50s    aihealth_momos        50.5s   8.6M views   4-5 organs arguing, then a moral
    serial_75s   desiitoons_ladakh     91.0s   453K likes   story serial, music + on-screen text

`audio_mode` is the important axis:
    "narrated" -> multi-voice Kokoro TTS, one voice per character
    "music"    -> NO TTS at all; a BGM track plus burned-in dialogue text.
                  This is what shadow_files0 / realistic_crime / nighttales169 actually do —
                  all four of those reels transcribed to the same devotional song, no voiceover.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class FormatProfile:
    name: str
    target_duration_sec: float
    segment_range: tuple[int, int]
    audio_mode: str          # "narrated" | "music"
    max_characters: int      # 0 for music mode — no TTS voices to assign
    description: str


FORMATS: dict[str, FormatProfile] = {
    "joke_10s": FormatProfile(
        name="joke_10s",
        target_duration_sec=11.0,
        segment_range=(2, 3),
        audio_mode="narrated",
        max_characters=2,
        description="One setup, one reveal. Two speakers, nothing else. Highest views-per-second.",
    ),
    "montage_35s": FormatProfile(
        name="montage_35s",
        target_duration_sec=34.0,
        segment_range=(5, 7),
        audio_mode="music",
        max_characters=0,
        description="Emotional/nostalgia montage carried by a song and imagery, minimal text.",
    ),
    "drama_50s": FormatProfile(
        name="drama_50s",
        target_duration_sec=50.0,
        segment_range=(6, 9),
        audio_mode="narrated",
        max_characters=5,
        description="Anthropomorphic characters argue about a habit, then a calm moral payoff.",
    ),
    "serial_75s": FormatProfile(
        name="serial_75s",
        target_duration_sec=75.0,
        segment_range=(8, 12),
        audio_mode="music",
        max_characters=0,
        description="Story serial: moody track, silent visuals, dialogue burned on screen.",
    ),
}


def get_format(name: str) -> FormatProfile:
    try:
        return FORMATS[name]
    except KeyError:
        raise ValueError(
            f"unknown format {name!r}; expected one of {sorted(FORMATS)}"
        ) from None
