"""Background music selection for music-mode formats.

Why a local folder instead of generation: `hyperframes-media`'s BGM engine retrieves from
HeyGen (paid credential) or generates with Lyria, which needs `google-genai` plus a Gemini API
key — verified 2026-07-21 by reading `scripts/audio.mjs` and `lyria-recipe.py`. The only bundled
audio in the skill is SFX, no music. So the zero-cost, zero-dependency default is a curated
folder the user fills with tracks they actually like:

    assets/music/dark/*.mp3        thriller, crime, horror
    assets/music/emotional/*.mp3   nostalgia, motivation, family
    assets/music/comedy/*.mp3      light, funny
    assets/music/devotional/*.mp3  bhakti, mythology

Selection is deterministic per series seed, so every part of one series shares the same track —
which is what makes a serial feel like one show.
"""
import os
import glob
import hashlib

MOODS = ("dark", "emotional", "comedy", "devotional")

_AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".ogg")

_NICHE_MOOD = {
    "horror": "dark",
    "crime": "dark",
    "thriller": "dark",
    "mythology": "devotional",
    "bhakti": "devotional",
    "comedy": "comedy",
    "motivation": "emotional",
    "finance": "emotional",
    "tech": "emotional",
    "trending": "emotional",
}


def mood_for_niche(niche: str) -> str:
    return _NICHE_MOOD.get((niche or "").lower(), "emotional")


def pick_track(mood: str, music_dir: str, seed: str = "") -> str | None:
    """Deterministically pick one track for `mood`. Returns None if none available."""
    folder = os.path.join(music_dir, mood)
    if not os.path.isdir(folder):
        return None
    tracks = sorted(
        p for p in glob.glob(os.path.join(folder, "*"))
        if p.lower().endswith(_AUDIO_EXTS) and os.path.isfile(p)
    )
    if not tracks:
        return None
    idx = int(hashlib.md5((seed or mood).encode("utf-8")).hexdigest()[:8], 16) % len(tracks)
    return tracks[idx]
