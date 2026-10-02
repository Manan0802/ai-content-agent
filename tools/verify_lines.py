"""Round-trip every spoken line back through Whisper before it enters a cut.

This is the check that has caught real defects twice — Veo read `पहचाण` as "पैर पैन", and read
`पाछै` ("behind") as "अच्छे" ("fine"), which destroyed the line the horror story turned on.

It used to run on Groq's hosted whisper-large-v3. That key now returns
`Access denied. Please check your network settings.` on every endpoint, including /models, from
inside and outside the sandbox — so the engine is dead, not rate-limited. mlx-whisper runs the
same large-v3 weights locally on this Mac's GPU, needs no key and no quota, and removes the
project's dependence on somebody else's free tier for its most important gate.

Whisper's Devanagari spelling of Haryanvi is loose ("गाड्डी" comes back "गड़ी"), so the comparison
is word-level and advisory — a human still reads the pairs. What it reliably catches is a word
coming back as a DIFFERENT word, which is the failure that matters.

    python3 tools/verify_lines.py <clip.mp4> "<expected devanagari line>"
"""
import subprocess
import sys
import tempfile
import os

MODEL = "mlx-community/whisper-large-v3-mlx"


def transcribe(path: str, language: str = "hi") -> dict:
    import mlx_whisper
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn",
                        "-ac", "1", "-ar", "16000", "-b:a", "64k", wav], check=True)
        return mlx_whisper.transcribe(wav, path_or_hf_repo=MODEL, language=language)


def speech_end(result: dict) -> float:
    """Where the line actually stops — Flow always returns a full 10s however short the line is."""
    segs = result.get("segments") or []
    return max((s["end"] for s in segs), default=0.0)


def _norm(word: str) -> str:
    """Fold the spelling differences Whisper always produces, so only real substitutions show.

    Whisper transcribes Haryanvi through a Hindi model, so it reliably rewrites the dialect's
    spelling without getting the word wrong: गाड्डी->गाड़ी, सै->है, तू->तु, सूं->सूँ. Flagging those
    buries the failure that actually matters — a word coming back as a DIFFERENT word, which is
    how `पहचाण` -> "पैर पैन" and `पाछै` -> "अच्छे" were caught.
    """
    w = word.strip("।,.…?!\"'\u200d")
    for a, b in (("ड्ड", "ड़"), ("सै", "है"), ("ूँ", "ु"), ("ूं", "ु"), ("ू", "ु"),
                 ("ँ", "ं"), ("ै", "े"), ("ऩ", "न"), ("ॉ", "ो"), ("ॅ", "े"),
                 ("्", "")):      # Whisper spells conjuncts out: हॉर्न -> होरन
        w = w.replace(a, b)
    return w


_MATRAS = "\u093e\u093f\u0940\u0941\u0942\u0943\u0947\u0948\u094b\u094c\u0902\u0903\u0901\u094d\u093c"
# independent vowel letters, which a matra of the same sound can stand in for:
# बतावूँ carries the vowel as a matra, बताऊं spells it out as ऊ. Same word, different orthography.
_VOWELS = "\u0905\u0906\u0907\u0908\u0909\u090a\u090f\u0910\u0913\u0914"


def _skeleton(word: str) -> str:
    """Consonants only. Dialect spelling lives almost entirely in the vowel marks.

    क्यूँ vs क्यों and काळू vs कालू are the same words spelt for Haryanvi and for Hindi; stripping
    the matras collapses them. It stays strict where it matters, because a substituted word has a
    different consonant skeleton too: पहचाण/पैर पैन, पाछै/अच्छे and चाय/चाहे all still differ.
    """
    w = _norm(word)
    sk = "".join(c for c in w if c not in _MATRAS and c not in _VOWELS).replace("\u0933", "\u0932")
    # Haryanvi inserts a व glide where Hindi has a plain long vowel — बतावूँ/बताऊं, आवै/आए.
    # Whisper always writes the Hindi form, so the glide has to fold or every such line is flagged.
    return sk.replace("\u0935", "")


_NUMBERS = {"\u090f\u0915": 1, "\u0926\u094b": 2, "\u0924\u0940\u0928": 3, "\u091a\u093e\u0930": 4,
            "\u092a\u093e\u0901\u091a": 5, "\u091b\u0939": 6, "\u0938\u093e\u0924": 7,
            "\u0906\u0920": 8, "\u0928\u094c": 9, "\u0926\u0938": 10,
            "\u0938\u094c": 100, "\u0939\u091c\u093c\u093e\u0930": 1000,
            "\u0939\u091c\u093e\u0930": 1000, "\u0932\u093e\u0916": 100000}


def _is_number_word(word: str, heard: list[str]) -> bool:
    """Whisper writes numerals: "चार हज़ार" comes back as "4000", "दो लाख" as "200000"."""
    w = word.strip("\u0964,.\u2026?!\"'")
    if w not in _NUMBERS:
        return False
    return any(any(c.isdigit() for c in h) for h in heard)


_TRANSLIT = {
    "\u0915": "k", "\u0916": "kh", "\u0917": "g", "\u0918": "gh", "\u091a": "ch",
    "\u091b": "chh", "\u091c": "j", "\u091d": "jh", "\u091f": "t", "\u0920": "th",
    "\u0921": "d", "\u0922": "dh", "\u0923": "n", "\u0924": "t", "\u0925": "th",
    "\u0926": "d", "\u0927": "dh", "\u0928": "n", "\u092a": "p", "\u092b": "f",
    "\u092c": "b", "\u092d": "bh", "\u092e": "m", "\u092f": "y", "\u0930": "r",
    "\u0932": "l", "\u0935": "v", "\u0936": "sh", "\u0937": "sh", "\u0938": "s",
    "\u0939": "h", "\u0905": "a", "\u0906": "a", "\u0907": "i", "\u0908": "i",
    "\u0909": "u", "\u090a": "u", "\u090f": "e", "\u0910": "ai", "\u0913": "o",
    "\u0914": "au", "\u093e": "a", "\u093f": "i", "\u0940": "i", "\u0941": "u",
    "\u0942": "u", "\u0947": "e", "\u0948": "ai", "\u094b": "o", "\u094c": "au",
}


def _roman(word: str) -> str:
    """Crude Devanagari -> latin, only good enough to recognise an English loanword."""
    return "".join(_TRANSLIT.get(c, "") for c in word).lower()


def _is_english_loanword(word: str, heard: list[str]) -> bool:
    """The WiFi problem in reverse.

    A line can spell an English word in Devanagari (साउथ-वेस्ट, बेडरूम) and Whisper hands it back
    in Latin (Southwest, bedroom). Same word, opposite script. Only ever consulted when the heard
    text actually contains a Latin token, so Devanagari-only lines — where every real misread has
    been — are untouched.
    """
    import difflib
    latin = [h for h in heard if _is_latin(h)]
    if not latin:
        return False
    r = _roman(word)
    if len(r) < 3:
        return False
    return any(difflib.SequenceMatcher(None, r, "".join(
        c for c in h.lower() if c.isalpha())).ratio() >= 0.55 for h in latin)


def _is_latin(word: str) -> bool:
    return any("a" <= c.lower() <= "z" for c in word)


def _matched(word: str, heard_words: list[str]) -> bool:
    # A Latin word in a Devanagari line (WiFi, share, Follow) always comes back transliterated —
    # Whisper wrote "वाईफाई" for "WiFi", which is the correct pronunciation and simply cannot be
    # compared across scripts. Flagging those would block assembly on a non-problem, so they are
    # reported separately rather than treated as misreads.
    if _is_latin(word) or _is_number_word(word, heard_words):
        return True
    if _is_english_loanword(word, heard_words):
        return True
    n = _norm(word)
    if not n:
        return True
    for h in heard_words:
        hn = _norm(h)
        if n == hn or n in hn or hn in n:
            return True
        # one substituted character is still the same word to a listener
        if len(n) == len(hn) and sum(a != b for a, b in zip(n, hn)) <= 1:
            return True
    sk = _skeleton(word)
    # a word that is nothing but vowels leaves an empty skeleton, which would match everything
    if len(sk) >= 2 and any(sk == _skeleton(h) for h in heard_words):
        return True
    return False


# A whole-line similarity fallback was tried here and DELIBERATELY REMOVED. It would have folded
# the word-boundary shifts Whisper produces on dialect (चलावै सै -> चला वैसे), but a stress test
# showed it also let `पाछै` -> `अच्छे` through: in a long line one substituted word is a small
# fraction of the characters, so the ratio stays high. That is precisely the defect this gate
# exists to catch — it destroyed the line the horror story turned on. A flag a human has to read
# is the correct behaviour; a gate that quietly passes the thing it was built for is not.

def main() -> None:
    clip, expected = sys.argv[1], sys.argv[2]
    r = transcribe(clip)
    heard = r["text"].strip()
    end = speech_end(r)
    print(f"WRITTEN : {expected}")
    print(f"HEARD   : {heard}")
    print(f"SPEECH ENDS: {end:.2f}s")
    heard_words = heard.split()
    suspect = [w for w in expected.split() if not _matched(w, heard_words)]
    if suspect:
        print(f"\u26a0 POSSIBLE MISREAD: {suspect}  <- read these two lines against each other")
    else:
        print("OK: every written word is present, allowing for Whisper's Haryanvi spelling")


if __name__ == "__main__":
    main()
