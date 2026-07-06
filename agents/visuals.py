from orchestrator.state import ContentState
from integrations.fal_client import FalClient


def visuals_node(state: ContentState, fal: FalClient, character_ref_url: str) -> ContentState:
    try:
        assets = []
        for seg in state["script"]["segments"]:
            use_hero = bool(seg.get("character_visible")) and bool(character_ref_url)
            if use_hero:
                url = fal.generate_hero_image(seg["visual_direction"], character_ref_url)
                tier = "hero"
            else:
                url = fal.generate_broll_image(seg["visual_direction"])
                tier = "broll"
            assets.append({"scene_number": seg["scene_number"], "image_url": url, "tier": tier})
        state["visual_assets"] = assets
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"visuals: {e}")
        state["visual_assets"] = []
    return state
