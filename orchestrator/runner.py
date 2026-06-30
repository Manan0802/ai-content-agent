from config import SETTINGS
from orchestrator.state import new_state
from orchestrator.graph import build_graph
from integrations.groq_client import GroqClient
from agents.idea_generator import SeedTrendsProvider
from modules.notifier import CLINotifier, AutoApproveNotifier


def run_job(niche=None, mode=None, fmt="short", auto=False):
    niche = niche or SETTINGS.default_niche
    mode = mode or SETTINGS.default_mode
    groq = GroqClient()
    notifier = AutoApproveNotifier() if auto else CLINotifier()
    app = build_graph(groq=groq, trends=SeedTrendsProvider(), notifier=notifier)
    state = new_state(niche, mode, SETTINGS.default_language, fmt, ["topic", "script"])
    return app.invoke(state)


if __name__ == "__main__":
    result = run_job()
    title = result.get("script", {}).get("title", "(no script)")
    segs = len(result.get("script", {}).get("segments", []))
    print(f"\nStatus: {result['status']} | Title: {title} | Segments: {segs}")
    if result.get("errors"):
        print("Errors:", result["errors"])
