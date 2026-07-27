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
    default_format: str = os.getenv("DEFAULT_FORMAT", "drama_50s")
    music_dir: str = os.getenv("MUSIC_DIR", "assets/music")
    # "silent": render music-mode videos with no audio track — you add trending audio in the
    #   Instagram / YouTube app at upload time (more reach; trending audio can't be set via API).
    # "baked": mix a track from assets/music/<mood>/ into the video (fully automated).
    bgm_mode: str = os.getenv("BGM_MODE", "silent")
    bgm_volume: float = 0.25
    supported_languages: list[str] = field(
        default_factory=lambda: ["hindi", "hinglish", "haryanvi", "punjabi"]
    )
    fal_api_key: str | None = os.getenv("FAL_KEY")
    image_provider: str = os.getenv("IMAGE_PROVIDER", "fal")  # fal | pollinations | gemini
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    character_ref_image_url: str = os.getenv("CHARACTER_REF_IMAGE_URL", "")
    kokoro_voice: str = "af_heart"
    video_width: int = 1080
    video_height: int = 1920
    outputs_dir: str = "outputs"
    ai_disclosure_text: str = "This video was made using AI-generated voice and visuals."
    ai_disclosure_duration_sec: float = 3.0
    youtube_client_id: str | None = os.getenv("YOUTUBE_CLIENT_ID")
    youtube_client_secret: str | None = os.getenv("YOUTUBE_CLIENT_SECRET")
    youtube_refresh_token: str | None = os.getenv("YOUTUBE_REFRESH_TOKEN")
    youtube_privacy: str = os.getenv("YOUTUBE_PRIVACY", "unlisted")
    publish_platform: str = os.getenv("PUBLISH_PLATFORM", "youtube")


SETTINGS = Settings()
