from groq import Groq
from config import SETTINGS


class GroqClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self._api_key = api_key or SETTINGS.groq_api_key
        self._model = model or SETTINGS.groq_model
        self._client = None  # lazy — never constructed in unit tests

    def _ensure_client(self) -> Groq:
        if self._client is None:
            if not self._api_key:
                raise RuntimeError("GROQ_API_KEY not set")
            self._client = Groq(api_key=self._api_key)
        return self._client

    def _chat(self, messages: list[dict], json_mode: bool) -> str:
        client = self._ensure_client()
        kwargs = {"model": self._model, "messages": messages, "temperature": 0.8}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content

    def complete(self, system: str, user: str, json_mode: bool = False) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        return self._chat(messages, json_mode)
