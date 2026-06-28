import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = "llama-3.3-70b-versatile"
    niches: list[str] = field(
        default_factory=lambda: [
            "horror", "tech", "finance", "motivation", "mythology", "comedy", "trending",
        ]
    )
    default_niche: str = "horror"
    default_language: str = "hinglish"
    default_mode: str = "semi_auto"


SETTINGS = Settings()
