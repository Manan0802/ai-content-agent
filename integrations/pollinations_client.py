import time
import hashlib
import urllib.parse
import urllib.request


def _http_fetch(url: str, timeout: int = 90) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "aica-bot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()


class PollinationsClient:
    """Free, no-API-key image generation via pollinations.ai.

    Drop-in for FalClient (same generate_hero_image/generate_broll_image
    interface) for zero-cost testing. Pollinations has no character-reference
    conditioning, so hero scenes ignore the reference image and generate from
    the prompt alone.

    A deterministic per-prompt seed makes each image stable. Before returning a
    URL, the client "warms" it — fetches it once (with retry/backoff on HTTP 429
    and a pause between images) so the image is generated and server-side cached.
    That way HyperFrames' render-time download hits a fast cached response
    instead of the burst rate limit that a cold, all-at-once fetch triggers.
    """

    BASE = "https://image.pollinations.ai/prompt/"

    def __init__(self, width: int = 1080, height: int = 1920, model: str = "flux",
                 warm: bool = True, fetch=_http_fetch, sleeper=time.sleep,
                 max_retries: int = 5, pace_sec: float = 2.0):
        self._width = width
        self._height = height
        self._model = model
        self._warm = warm
        self._fetch = fetch
        self._sleep = sleeper
        self._max_retries = max_retries
        self._pace_sec = pace_sec

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

    def _warm_url(self, url: str) -> None:
        if not self._warm:
            return
        delay = self._pace_sec
        for attempt in range(self._max_retries):
            try:
                self._fetch(url)
                self._sleep(self._pace_sec)  # pace between images to avoid bursts
                return
            except Exception as e:  # noqa: BLE001 - retry on 429, else give up quietly
                if attempt < self._max_retries - 1:
                    self._sleep(delay)
                    delay *= 2
                    continue
                return  # render still has the URL as a fallback

    def _generate(self, prompt: str) -> str:
        url = self._url(prompt)
        self._warm_url(url)
        return url

    def generate_hero_image(self, prompt: str, reference_image_url: str) -> str:
        return self._generate(prompt)

    def generate_broll_image(self, prompt: str) -> str:
        return self._generate(prompt)
