import os
import time
import urllib.request
from orchestrator.state import ContentState
from integrations.fal_client import FalClient
from modules.style import style_for_niche
from modules.prompt_terms import disambiguate


def _http_fetch(url: str, dest: str, timeout: int = 180) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (aica)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    if len(data) < 1024:
        raise RuntimeError(f"image too small ({len(data)} bytes) — likely an error page")
    with open(dest, "wb") as f:
        f.write(data)


def _build_prompt(seg: dict, style_prompt: str, appearances: dict) -> str:
    """Compose the image prompt: locked art style + scene + (for hero shots) who is in it.

    The locked style_prompt is what makes every part of a series look like one show — it is
    generated once by series_writer and pasted into every single image prompt.
    """
    parts = []
    if style_prompt:
        parts.append(style_prompt.rstrip(". "))
    parts.append(disambiguate(seg.get("visual_direction", "")))
    if seg.get("character_visible"):
        look = appearances.get(seg.get("speaker"))
        if look:
            parts.append(look)
    return ". ".join(p for p in parts if p)


def visuals_node(state: ContentState, fal: FalClient, character_ref_url: str,
                 style_prompt: str = "", project_dir: str = "",
                 fetch=_http_fetch, pace_sec: float = 2.0) -> ContentState:
    try:
        # a series locks its art direction + character looks once and reuses them everywhere
        series = state.get("series", {}) or {}
        # A one-off job has no series style, which left every scene looking like a different
        # production. Fall back to the niche's locked look so at least one video is coherent.
        style_prompt = (style_prompt or series.get("style_prompt", "")
                        or style_for_niche(state.get("niche", "")))
        appearances = {
            c.get("id"): c.get("appearance", "")
            for c in series.get("characters", []) or []
        }

        images_dir = os.path.join(project_dir, "images") if project_dir else ""
        if images_dir:
            os.makedirs(images_dir, exist_ok=True)

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

            image_ref = url
            if images_dir:
                # Download to a SHORT local filename. HyperFrames derives its cache filename from
                # the URL, and a URL-encoded Hindi prompt (हर अक्षर -> %E0%A4%..) blows past the
                # 255-byte OS limit -> ENAMETOOLONG -> the image silently never loads.
                name = f"scene_{seg['scene_number']}.jpg"
                dest = os.path.join(images_dir, name)
                try:
                    fetch(url, dest)
                    image_ref = f"images/{name}"
                    if pace_sec:
                        time.sleep(pace_sec)   # pace so the free image API doesn't rate-limit us
                except Exception as e:  # noqa: BLE001 - keep the remote URL as a fallback
                    state.setdefault("errors", []).append(
                        f"visuals: image download failed for scene {seg['scene_number']}: {e}"
                    )

            assets.append({"scene_number": seg["scene_number"],
                           "image_url": image_ref, "tier": tier})
        state["visual_assets"] = assets
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"visuals: {e}")
        state["visual_assets"] = []
    return state
