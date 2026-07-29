"""Edge TTS — free, unlimited, and genuinely Hindi-native.

This is the best voice option available to us, and it costs nothing:

- **Kokoro** is an English model phonemising Devanagari through `--lang hi`. It's intelligible
  but the accent is wrong.
- **Gemini TTS** speaks Hindi properly, but the free tier's quota is small and ours ran out
  within a handful of calls.
- **Edge TTS** ships `hi-IN-MadhurNeural` (male) and `hi-IN-SwaraNeural` (female) — real
  Hindi-trained neural voices — with no API key and no quota. Verified live 2026-07-22.

Found via MoneyPrinterTurbo's `app/services/voice.py`.

Interface matches HyperFramesTTS/GeminiTTS (`synthesize(text, output_path, voice=None)`), and the
Kokoro voice ids from `modules/voices.py` are mapped onto the Hindi voices, so per-character
voice assignment keeps working across a series.
"""
import os
import asyncio

_MALE = "hi-IN-MadhurNeural"
_FEMALE = "hi-IN-SwaraNeural"

# Edge has exactly two Hindi voices, but a script can have five characters. Pitch and rate do the
# separating: lower + slower reads as older, higher + faster as younger. Each id gets its own
# delivery so no two characters in one scene sound like the same person.
#                  (base voice, rate,   pitch)
VOICE_PROFILES: dict[str, tuple[str, str, str]] = {
    "am_adam":      (_MALE,   "+8%",  "+0Hz"),     # lead male, neutral
    "am_michael":   (_MALE,   "+0%",  "-8Hz"),     # older, heavier
    "bm_george":    (_MALE,   "+16%", "+6Hz"),     # younger, quicker
    "af_heart":     (_FEMALE, "+8%",  "+0Hz"),     # lead female, neutral
    "af_nova":      (_FEMALE, "+18%", "+8Hz"),     # young girl
    "af_sky":       (_FEMALE, "+0%",  "-6Hz"),     # older woman
    "bf_emma":      (_FEMALE, "+12%", "+4Hz"),
    "bf_isabella":  (_FEMALE, "-4%",  "-10Hz"),    # slowest, deepest
}
_DEFAULT_PROFILE = (_FEMALE, "+8%", "+0Hz")

# kept for callers that only need the base voice
VOICE_MAP = {k: v[0] for k, v in VOICE_PROFILES.items()}


def profile_for(voice_id: str | None) -> tuple[str, str, str]:
    """(edge voice, rate, pitch) for a character's assigned voice id."""
    return VOICE_PROFILES.get(voice_id or "", _DEFAULT_PROFILE)


class EdgeTTS:
    def __init__(self, voice: str = "af_heart", rate: str = "+8%", pitch: str = "+0Hz"):
        self._voice = voice
        self._rate = rate      # reels are paced faster than natural speech
        self._pitch = pitch

    def is_configured(self) -> bool:
        return True            # no key, no quota

    def _speak(self, text: str, voice: str, dest: str, rate: str, pitch: str) -> None:
        import edge_tts

        async def run():
            comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            with open(dest, "wb") as f:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])

        asyncio.run(run())

    def synthesize(self, text: str, output_path: str, voice: str | None = None) -> str:
        edge_voice, rate, pitch = profile_for(voice or self._voice)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        self._speak(text, edge_voice, output_path, rate, pitch)
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1024:
            raise RuntimeError(f"edge tts produced no audio for: {text[:50]!r}")
        return output_path
