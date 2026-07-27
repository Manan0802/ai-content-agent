"""Gemini TTS — proper Hindi/Hinglish voice, on the free tier.

Kokoro is English-trained; it pronounces Devanagari phonetically through a phonemizer override
and it sounds like it. `gemini-3.1-flash-tts-preview` speaks Hindi natively — verified live on
2026-07-22 with the real key, returning 24kHz mono PCM for a Haryanvi/Hindi thriller line.

Interface matches HyperFramesTTS (`synthesize(text, output_path, voice=None)`) so it drops into
`voiceover_node` with no other change. Kokoro voice ids are mapped onto Gemini's prebuilt voices,
so the existing per-character voice assignment (modules/voices.py) keeps working — a character
that got `am_michael` in one part gets the same Gemini voice in every other part.
"""
import os
import wave

MODEL = "gemini-3.1-flash-tts-preview"
SAMPLE_RATE = 24000

# Kokoro voice id -> Gemini prebuilt voice, keeping gender roughly consistent
VOICE_MAP = {
    "am_adam": "Charon",       # deep male
    "am_michael": "Puck",      # upbeat male
    "bm_george": "Fenrir",     # gravelly male
    "af_heart": "Kore",        # warm female
    "af_nova": "Aoede",        # bright female
    "af_sky": "Leda",          # youthful female
    "bf_emma": "Zephyr",       # airy female
    "bf_isabella": "Autonoe",  # calm female
}
_DEFAULT_VOICE = "Kore"


class GeminiTTS:
    def __init__(self, api_key: str | None = None, model: str = MODEL,
                 voice: str = "af_heart"):
        self._api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        self._model = model
        self._voice = voice
        self._client = None

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def _ensure_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _synth(self, text: str, voice: str) -> bytes:
        from google.genai import types

        client = self._ensure_client()
        response = client.models.generate_content(
            model=self._model,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                    )
                ),
            ),
        )
        return response.candidates[0].content.parts[0].inline_data.data

    def synthesize(self, text: str, output_path: str, voice: str | None = None) -> str:
        gemini_voice = VOICE_MAP.get(voice or self._voice, _DEFAULT_VOICE)
        pcm = self._synth(text, gemini_voice)
        if not pcm:
            raise RuntimeError(f"gemini tts returned no audio for: {text[:50]!r}")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        # the API returns raw 24kHz mono 16-bit PCM — wrap it in a WAV container
        with wave.open(output_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SAMPLE_RATE)
            w.writeframes(pcm)
        return output_path
