import json
from orchestrator.state import ContentState
from integrations.groq_client import GroqClient
from prompts.script_prompts import script_system_prompt


def script_writer_node(state: ContentState, groq: GroqClient) -> ContentState:
    try:
        system = script_system_prompt(state["niche"], state["language"], state["format"])
        user = f"Topic: {state['topic']}\nWrite the full script now."
        raw = groq.complete(system=system, user=user, json_mode=True)
        state["script"] = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"script_writer: {e}")
        state["script"] = {}
    return state
