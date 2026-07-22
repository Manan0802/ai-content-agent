import json
import uuid
from orchestrator.state import ContentState
from integrations.groq_client import GroqClient
from prompts.series_prompts import series_system_prompt
from config import SETTINGS


def series_writer_node(state: ContentState, groq: GroqClient) -> ContentState:
    try:
        parts = int(state.get("series_parts") or 3)
        fmt = state.get("format_profile") or SETTINGS.default_format
        system = series_system_prompt(
            niche=state["niche"], language=state["language"],
            format_name=fmt, parts=parts,
        )
        user = (
            f"Story idea: {state['topic']}\n"
            f"Break it into exactly {parts} parts now."
        )
        raw = groq.complete(system=system, user=user, json_mode=True)
        series = json.loads(raw)
        series.setdefault("characters", [])
        series.setdefault("parts", [])
        series.setdefault("style_prompt", "")

        if len(series["parts"]) != parts:
            state.setdefault("errors", []).append(
                f"series_writer: expected {parts} parts, got {len(series['parts'])}"
            )

        state["series"] = series
        state["series_id"] = state.get("series_id") or str(uuid.uuid4())[:8]
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"series_writer: {e}")
        state["series"] = {}
    return state
