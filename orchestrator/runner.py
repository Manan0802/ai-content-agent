from config import SETTINGS
from orchestrator.state import new_state
from orchestrator.graph import build_graph
from integrations.groq_client import GroqClient
from integrations.fal_client import FalClient
from integrations.pollinations_client import PollinationsClient
from integrations.gemini_client import GeminiImageClient
from integrations.hyperframes_tts import HyperFramesTTS
from integrations.gemini_tts import GeminiTTS
from integrations.edge_tts_client import EdgeTTS
from integrations.hyperframes_cli import HyperFramesCLI
from integrations.youtube_client import YouTubeClient
from agents.idea_generator import SeedTrendsProvider
from modules.notifier import CLINotifier, AutoApproveNotifier
from modules.job_store import save_job


def _tts_client():
    """kokoro = free + local but English-trained; gemini = native Hindi on the free tier."""
    if SETTINGS.tts_provider == "edge":
        return EdgeTTS(voice=SETTINGS.kokoro_voice)
    if SETTINGS.tts_provider == "gemini":
        return GeminiTTS(voice=SETTINGS.kokoro_voice)
    return HyperFramesTTS(voice=SETTINGS.kokoro_voice)


def _image_client():
    """Pick the image backend. gemini = free tier + reference-image character lock."""
    if SETTINGS.image_provider == "gemini":
        return GeminiImageClient(pace_sec=4.0)   # free tier is rate-limited per minute
    if SETTINGS.image_provider == "pollinations":
        return PollinationsClient(width=SETTINGS.video_width, height=SETTINGS.video_height)
    return FalClient()


def run_job(niche=None, mode=None, fmt="short", auto=False,
            format_profile=None, language=None):
    niche = niche or SETTINGS.default_niche
    mode = mode or SETTINGS.default_mode
    language = language or SETTINGS.default_language
    format_profile = format_profile or SETTINGS.default_format
    state = new_state(niche, mode, language, fmt,
                      ["topic", "script", "render", "publish"],
                      format_profile=format_profile)
    project_dir = f"{SETTINGS.outputs_dir}/{state['job_id']}"

    groq = GroqClient()
    notifier = AutoApproveNotifier() if auto else CLINotifier()
    app = build_graph(
        groq=groq,
        trends=SeedTrendsProvider(),
        notifier=notifier,
        fal=_image_client(),
        tts=_tts_client(),
        hf_cli=HyperFramesCLI(),
        youtube=YouTubeClient(),
        project_dir=project_dir,
    )
    result = app.invoke(state)
    save_job(result, SETTINGS.outputs_dir)
    return result


if __name__ == "__main__":
    result = run_job()
    title = result.get("script", {}).get("title", "(no script)")
    segs = len(result.get("script", {}).get("segments", []))
    print(f"\nStatus: {result['status']} | Title: {title} | Segments: {segs}")
    if result.get("render_output_path"):
        print(f"Video: {result['render_output_path']}")
    if result.get("errors"):
        print("Errors:", result["errors"])
