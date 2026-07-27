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

# Kokoro voice id -> Edge Hindi voice, preserving gender so character casting still works
VOICE_MAP = {
    "am_adam": "hi-IN-MadhurNeural",
    "am_michael": "hi-IN-MadhurNeural",
    "bm_george": "hi-IN-MadhurNeural",
    "af_heart": "hi-IN-SwaraNeural",
    "af_nova": "hi-IN-SwaraNeural",
    "af_sky": "hi-IN-SwaraNeural",
    "bf_emma": "hi-IN-SwaraNeural",
    "bf_isabella": "hi-IN-SwaraNeural",
}
_DEFAULT_VOICE = "hi-IN-SwaraNeural"


class EdgeTTS:
    def __init__(self, voice: str = "af_heart", rate: str = "+8%", pitch: str = "+0Hz"):
        self._voice = voice
        self._rate = rate      # reels are paced faster than natural speech
        self._pitch = pitch

    def is_configured(self) -> bool:
        return True            # no key, no quota

    def _speak(self, text: str, voice: str, dest: str) -> None:
        import edge_tts

        async def run():
            comm = edge_tts.Communicate(text, voice, rate=self._rate, pitch=self._pitch)
            with open(dest, "wb") as f:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])

        asyncio.run(run())

    def synthesize(self, text: str, output_path: str, voice: str | None = None) -> str:
        edge_voice = VOICE_MAP.get(voice or self._voice, _DEFAULT_VOICE)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        self._speak(text, edge_voice, output_path)
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1024:
            raise RuntimeError(f"edge tts produced no audio for: {text[:50]!r}")
        return output_path
