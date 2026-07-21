"""Voice assignment — one distinct voice per character.

The 8.6M-view reference reel (`aihealth_momos`) is not narration, it's four organs arguing:
stomach, small intestine, liver and heart each have their own personality and voice. That's the
format we're matching, so each character in a script gets its own Kokoro voice.

Voice IDs verified live with `npx hyperframes tts --list`. Kokoro ships 12 voices in this build;
we only use the 8 English (en-US / en-GB) ones — the es/fr/ja/zh voices mispronounce Indian-
language text badly. Hindi/Haryanvi pronunciation comes from the `--lang hi` phonemizer override,
not from a Hindi voice (there isn't one).

Assignment is deterministic per character id so a character keeps the same voice across every
part of a series.
"""
import hashlib

VOICE_POOL: dict[str, list[str]] = {
    "male": ["am_adam", "am_michael", "bm_george"],
    "female": ["af_heart", "af_nova", "af_sky", "bf_emma", "bf_isabella"],
}

_FEMALE_WORDS = ("female", "woman", "girl", "lady", "aunty", "mother", "maa", "ladki")
_MALE_WORDS = ("male", "man", "boy", "guy", "father", "papa", "bhai", "uncle")


def _gender_of(voice_hint: str) -> str:
    h = (voice_hint or "").lower()
    if any(w in h for w in _FEMALE_WORDS):
        return "female"
    if any(w in h for w in _MALE_WORDS):
        return "male"
    return "female"  # Kokoro's female voices are its strongest; safe default


def _stable_index(character_id: str, n: int) -> int:
    digest = hashlib.md5(character_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % max(n, 1)


def assign_voices(characters: list[dict]) -> dict[str, str]:
    """Map character id -> Kokoro voice id, stable per character, no duplicates in one script."""
    assigned: dict[str, str] = {}
    used: set[str] = set()
    for ch in characters or []:
        cid = ch.get("id")
        if not cid:
            continue
        pool = VOICE_POOL[_gender_of(ch.get("voice_hint", ""))]
        start = _stable_index(cid, len(pool))
        # start from this character's own stable slot, probe forward only on collision
        for offset in range(len(pool)):
            voice = pool[(start + offset) % len(pool)]
            if voice not in used:
                break
        assigned[cid] = voice
        used.add(voice)
    return assigned
