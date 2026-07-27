"""Gemini image generation (Nano Banana) — free tier, and it does character consistency.

Why this exists: the free tier of `gemini-2.5-flash-image` allows ~500 images/day with no credit
card, generates natively at 9:16, and — the important part — accepts a **reference image** so a
recurring character keeps the same face across every scene and every part of a series. That is
the single biggest quality gap Pollinations can't close, and it's the reason paid fal.ai was on
the table. This gets it for ₹0.

Verified against the google-genai docs (2026-07-22): `generate_content` with
`response_modalities=["IMAGE"]` + `ImageConfig(aspect_ratio=...)`, image bytes come back on
`response.parts[*].inline_data.data`.

Interface matches FalClient/PollinationsClient so it drops straight into `visuals_node`. Images
are written locally and returned as `file://` URLs — `visuals_node`'s downloader handles those
natively, so nothing downstream changes.
"""
import os
import time
import hashlib
import tempfile
import urllib.request

from config import SETTINGS

MODEL = "gemini-2.5-flash-image"


class GeminiImageClient:
    def __init__(self, api_key: str | None = None, out_dir: str | None = None,
                 model: str = MODEL, pace_sec: float = 0.0):
        self._api_key = api_key if api_key is not None else SETTINGS.gemini_api_key
        self._out_dir = out_dir or os.path.join(tempfile.gettempdir(), "aica_gemini")
        self._model = model
        self._pace_sec = pace_sec  # free tier is rate-limited per minute
        self._client = None

    def is_configured(self) -> bool:
        return bool(self._api_key)

    # --- seams (mocked in tests) -------------------------------------------------

    def _ensure_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _load_reference(self, url: str) -> bytes | None:
        if not url:
            return None
        try:
            if url.startswith("file://"):
                with open(url[len("file://"):], "rb") as f:
                    return f.read()
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (aica)"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception:  # noqa: BLE001 - a missing reference shouldn't kill the scene
            return None

    def _generate(self, model: str, contents: str, aspect_ratio: str,
                  ref_bytes: bytes | None) -> bytes:
        from google.genai import types

        client = self._ensure_client()
        parts = [contents]
        if ref_bytes:
            parts.append(types.Part.from_bytes(data=ref_bytes, mime_type="image/jpeg"))

        response = client.models.generate_content(
            model=model,
            contents=parts,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            ),
        )
        for part in response.parts:
            if getattr(part, "inline_data", None) and part.inline_data.data:
                return part.inline_data.data
        return b""

    # --- public API --------------------------------------------------------------

    def _make(self, prompt: str, reference_image_url: str = "") -> str:
        ref_bytes = self._load_reference(reference_image_url) if reference_image_url else None
        data = self._generate(self._model, prompt, "9:16", ref_bytes)
        if not data or len(data) < 1024:
            raise RuntimeError(f"gemini returned no image for prompt: {prompt[:60]!r}")

        os.makedirs(self._out_dir, exist_ok=True)
        stem = hashlib.md5(f"{prompt}{time.time()}".encode("utf-8")).hexdigest()[:12]
        path = os.path.join(self._out_dir, f"{stem}.jpg")
        with open(path, "wb") as f:
            f.write(data)
        if self._pace_sec:
            time.sleep(self._pace_sec)
        return f"file://{path}"

    def generate_hero_image(self, prompt: str, reference_image_url: str) -> str:
        return self._make(prompt, reference_image_url)

    def generate_broll_image(self, prompt: str) -> str:
        return self._make(prompt)
