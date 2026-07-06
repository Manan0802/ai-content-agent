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
    fal_api_key: str | None = os.getenv("FAL_KEY")
    character_ref_image_url: str = os.getenv("CHARACTER_REF_IMAGE_URL", "")
    kokoro_voice: str = "af_heart"
    video_width: int = 1080
    video_height: int = 1920
    outputs_dir: str = "outputs"
    ai_disclosure_text: str = "This video was made using AI-generated voice and visuals."
    ai_disclosure_duration_sec: float = 3.0


SETTINGS = Settings()
