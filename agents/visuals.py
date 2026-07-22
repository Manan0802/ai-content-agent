from orchestrator.state import ContentState
from integrations.fal_client import FalClient


def _build_prompt(seg: dict, style_prompt: str, appearances: dict) -> str:
    """Compose the image prompt: locked art style + scene + (for hero shots) who is in it.

    The locked style_prompt is what makes every part of a series look like one show — it is
    generated once by series_writer and pasted into every single image prompt.
    """
    parts = []
    if style_prompt:
        parts.append(style_prompt.rstrip(". "))
    parts.append(seg.get("visual_direction", ""))
    if seg.get("character_visible"):
        look = appearances.get(seg.get("speaker"))
        if look:
            parts.append(look)
    return ". ".join(p for p in parts if p)


def visuals_node(state: ContentState, fal: FalClient, character_ref_url: str,
                 style_prompt: str = "") -> ContentState:
    try:
        # a series locks its art direction + character looks once and reuses them everywhere
        series = state.get("series", {}) or {}
        style_prompt = style_prompt or series.get("style_prompt", "")
        appearances = {
            c.get("id"): c.get("appearance", "")
            for c in series.get("characters", []) or []
        }

        assets = []
        for seg in state["script"]["segments"]:
            prompt = _build_prompt(seg, style_prompt, appearances)
            use_hero = bool(seg.get("character_visible")) and bool(character_ref_url)
            if use_hero:
                url = fal.generate_hero_image(prompt, character_ref_url)
                tier = "hero"
            else:
                url = fal.generate_broll_image(prompt)
                tier = "broll"
            assets.append({"scene_number": seg["scene_number"], "image_url": url, "tier": tier})
        state["visual_assets"] = assets
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"visuals: {e}")
        state["visual_assets"] = []
    return state
