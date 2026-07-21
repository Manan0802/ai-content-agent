import json
from orchestrator.state import ContentState
from integrations.groq_client import GroqClient
from prompts.script_prompts import script_system_prompt
from modules.formats import get_format


def script_writer_node(state: ContentState, groq: GroqClient) -> ContentState:
    try:
        profile = get_format(state["format_profile"]) if state.get("format_profile") else None
        system = script_system_prompt(
            state["niche"], state["language"], profile=profile, fmt=state.get("format"),
        )
        user = f"Topic: {state['topic']}\nWrite the full script now."
        raw = groq.complete(system=system, user=user, json_mode=True)
        script = json.loads(raw)
        script.setdefault("characters", [])
        state["script"] = script
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"script_writer: {e}")
        state["script"] = {}
    return state
