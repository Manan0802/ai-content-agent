"""Run a multi-part series: one story -> N videos that look and feel like one show.

Serialisation is the most repeatedly-confirmed finding in the reference research — later parts
outperform Part 1 because the audience becomes invested (shadow_files0: 64 comments on Part 1,
552 on Part 4). Two things make it work and both are decided ONCE, here, then reused by every
part: the locked `style_prompt` and the fixed character `appearance`s.

Each part runs through the same per-video pipeline as `run_job`, but entering at `script_writer`
(the topic is already known from the series plan, so there is nothing to ideate).
"""
from config import SETTINGS
from orchestrator.state import new_state
from orchestrator.graph import build_graph
from integrations.groq_client import GroqClient
from integrations.fal_client import FalClient
from integrations.pollinations_client import PollinationsClient
from integrations.gemini_client import GeminiImageClient
from integrations.hyperframes_tts import HyperFramesTTS
from integrations.hyperframes_cli import HyperFramesCLI
from integrations.youtube_client import YouTubeClient
from agents.idea_generator import SeedTrendsProvider
from agents.series_writer import series_writer_node
from modules.notifier import CLINotifier, AutoApproveNotifier
from modules.job_store import save_job


def _image_client():
    """Pick the image backend. gemini = free tier + reference-image character lock."""
    if SETTINGS.image_provider == "gemini":
        return GeminiImageClient(pace_sec=4.0)   # free tier is rate-limited per minute
    if SETTINGS.image_provider == "pollinations":
        return PollinationsClient(width=SETTINGS.video_width, height=SETTINGS.video_height)
    return FalClient()


def _part_brief(series: dict, part: dict, prev_cliffhanger: str, total: int) -> str:
    """The 'topic' handed to script_writer for one part — its beat plus what it must pay off."""
    lines = [
        f"SERIES: {series.get('series_title', '')} — {series.get('logline', '')}",
        f"PART {part['part_number']} of {total}",
        f"THIS PART'S BEAT: {part.get('beat_summary', '')}",
    ]
    if prev_cliffhanger:
        lines.append(
            f"OPEN BY PAYING OFF THE PREVIOUS PART'S CLIFFHANGER: {prev_cliffhanger}"
        )
    lines.append(f"END THIS PART ON THIS CLIFFHANGER: {part.get('cliffhanger', '')}")
    chars = series.get("characters", []) or []
    if chars:
        who = "; ".join(f"{c.get('name')} ({c.get('id')}): {c.get('appearance','')}" for c in chars)
        lines.append(f"RECURRING CHARACTERS (keep them identical across parts): {who}")
    return "\n".join(lines)


def run_series(topic: str, niche: str | None = None, format_profile: str | None = None,
               language: str | None = None, parts: int = 3, mode: str | None = None,
               auto: bool = False, outputs_dir: str | None = None) -> dict:
    niche = niche or SETTINGS.default_niche
    mode = mode or SETTINGS.default_mode
    language = language or SETTINGS.default_language
    format_profile = format_profile or SETTINGS.default_format
    outputs_dir = outputs_dir or SETTINGS.outputs_dir

    groq = GroqClient()
    notifier = AutoApproveNotifier() if auto else CLINotifier()

    # 1. plan the whole series once
    plan_state = new_state(niche, mode, language, "short", ["series"],
                           format_profile=format_profile)
    plan_state["topic"] = topic
    plan_state["series_parts"] = parts
    plan_state = series_writer_node(plan_state, groq=groq)

    series = plan_state.get("series") or {}
    if not series.get("parts"):
        return {"series": series, "series_id": plan_state.get("series_id", ""),
                "parts": [], "errors": plan_state.get("errors", [])}

    series_id = plan_state["series_id"]
    style_prompt = series.get("style_prompt", "")
    total = len(series["parts"])

    # 2. render each part through the normal per-video pipeline
    fal = _image_client()
    tts = HyperFramesTTS(voice=SETTINGS.kokoro_voice)
    hf_cli = HyperFramesCLI()
    youtube = YouTubeClient()

    part_states, errors, prev_cliffhanger = [], list(plan_state.get("errors", [])), ""
    for part in series["parts"]:
        st = new_state(niche, mode, language, "short",
                       ["script", "render", "publish"], format_profile=format_profile)
        st["series_id"] = series_id
        st["part_number"] = part["part_number"]
        st["series"] = series
        st["topic"] = _part_brief(series, part, prev_cliffhanger, total)

        project_dir = f"{outputs_dir}/{series_id}/part_{part['part_number']}"
        app = build_graph(
            groq=groq, trends=SeedTrendsProvider(), notifier=notifier,
            fal=fal, tts=tts, hf_cli=hf_cli, youtube=youtube,
            project_dir=project_dir, entry="script_writer",
        )
        result = app.invoke(st)
        # the series plan's own cliffhanger is authoritative; the script may reword it
        prev_cliffhanger = result.get("script", {}).get("cliffhanger") or part.get("cliffhanger", "")
        save_job(result, outputs_dir)
        part_states.append(result)
        errors.extend(result.get("errors", []))

    return {"series": series, "series_id": series_id, "parts": part_states, "errors": errors}


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "एक अमीर आदमी जो गरीब बनकर सच ढूँढता है"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = run_series(topic=topic, parts=n)
    print(f"\nSeries: {out['series'].get('series_title','(none)')} [{out['series_id']}]")
    for s in out["parts"]:
        print(f"  Part {s.get('part_number')}: {s.get('status')} -> {s.get('render_output_path','')}")
    if out["errors"]:
        print("Errors:", out["errors"][:5])
