import os
import fal_client as _fal


class FalClient:
    FLUX2_DEV = "fal-ai/flux-2/edit"
    FLUX_SCHNELL = "fal-ai/flux/schnell"

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.getenv("FAL_KEY")

    def _submit(self, model: str, arguments: dict) -> dict:
        if self._api_key:
            os.environ.setdefault("FAL_KEY", self._api_key)
        return _fal.subscribe(model, arguments=arguments)

    def generate_hero_image(self, prompt: str, reference_image_url: str) -> str:
        result = self._submit(self.FLUX2_DEV, {
            "prompt": prompt,
            "image_urls": [reference_image_url],
        })
        return result["images"][0]["url"]

    def generate_broll_image(self, prompt: str) -> str:
        result = self._submit(self.FLUX_SCHNELL, {"prompt": prompt})
        return result["images"][0]["url"]
