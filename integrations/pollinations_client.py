import hashlib
import urllib.parse


class PollinationsClient:
    """Free, no-API-key image generation via pollinations.ai.

    Drop-in for FalClient (same generate_hero_image/generate_broll_image
    interface) for zero-cost testing. Pollinations has no character-reference
    conditioning, so hero scenes ignore the reference image and generate from
    the prompt alone. A deterministic per-prompt seed makes each image stable,
    so HyperFrames' validate-then-render double fetch hits the cache.
    """

    BASE = "https://image.pollinations.ai/prompt/"

    def __init__(self, width: int = 1080, height: int = 1920, model: str = "flux"):
        self._width = width
        self._height = height
        self._model = model

    def _url(self, prompt: str) -> str:
        seed = int(hashlib.md5(prompt.encode("utf-8")).hexdigest()[:6], 16)
        query = urllib.parse.urlencode({
            "width": self._width,
            "height": self._height,
            "nologo": "true",
            "model": self._model,
            "seed": seed,
        })
        return f"{self.BASE}{urllib.parse.quote(prompt)}?{query}"

    def generate_hero_image(self, prompt: str, reference_image_url: str) -> str:
        return self._url(prompt)

    def generate_broll_image(self, prompt: str) -> str:
        return self._url(prompt)
