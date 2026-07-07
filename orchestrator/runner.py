from config import SETTINGS
from orchestrator.state import new_state
from orchestrator.graph import build_graph
from integrations.groq_client import GroqClient
from integrations.fal_client import FalClient
from integrations.hyperframes_tts import HyperFramesTTS
from integrations.hyperframes_cli import HyperFramesCLI
from agents.idea_generator import SeedTrendsProvider
from modules.notifier import CLINotifier, AutoApproveNotifier
from modules.job_store import save_job


def run_job(niche=None, mode=None, fmt="short", auto=False):
    niche = niche or SETTINGS.default_niche
    mode = mode or SETTINGS.default_mode
    state = new_state(niche, mode, SETTINGS.default_language, fmt,
                      ["topic", "script", "render"])
    project_dir = f"{SETTINGS.outputs_dir}/{state['job_id']}"

    groq = GroqClient()
    notifier = AutoApproveNotifier() if auto else CLINotifier()
    app = build_graph(
        groq=groq,
        trends=SeedTrendsProvider(),
        notifier=notifier,
        fal=FalClient(),
        tts=HyperFramesTTS(voice=SETTINGS.kokoro_voice),
        hf_cli=HyperFramesCLI(),
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
