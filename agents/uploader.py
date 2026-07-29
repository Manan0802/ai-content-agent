from orchestrator.state import ContentState
from config import SETTINGS
from modules.caption import build_caption


def _build_metadata(state: ContentState):
    script = state.get("script", {})
    title = (script.get("title") or state.get("topic") or "Untitled").strip()
    part = state.get("part_number", 0)
    total = len(state.get("series", {}).get("parts", []) or [])
    if part:
        title = f"{title} | Part {part}"
    title = title[:100]

    # engagement CTAs + #Shorts, per the measured caption research (modules/caption.py)
    caption = build_caption(script, part_number=part, total_parts=total,
                                platform="youtube")
    description = f"{caption}\n\n{SETTINGS.ai_disclosure_text}"
    tags = [t.lstrip("#") for t in (script.get("hashtags", []) or [])]
    return title, description, tags


def uploader_node(state: ContentState, youtube, notifier) -> ContentState:
    if state.get("status") == "failed":
        return state
    if not state.get("render_output_path"):
        state.setdefault("errors", []).append("uploader: no rendered video to upload — skipped")
        return state
    if youtube is None or not youtube.is_configured():
        state.setdefault("errors", []).append("uploader: youtube not configured — skipped upload")
        return state

    title, description, tags = _build_metadata(state)

    if "publish" in state.get("hitl_checkpoints", []) and state["mode"] != "full_auto":
        decision = notifier.ask_approval(
            "Publish to YouTube?",
            f"Title: {title}\nPrivacy: {SETTINGS.youtube_privacy}\n\n{description[:500]}",
        )
        if decision != "approve":
            state.setdefault("errors", []).append("uploader: publish rejected by human — kept unpublished")
            return state

    try:
        video_id = youtube.upload_video(
            file_path=state["render_output_path"],
            title=title,
            description=description,
            tags=tags,
            privacy=SETTINGS.youtube_privacy,
        )
        state["youtube_video_id"] = video_id
        state["youtube_url"] = f"https://youtu.be/{video_id}"
        state["status"] = "published"
    except Exception as e:  # noqa: BLE001 - don't lose the rendered video over an upload error
        state.setdefault("errors", []).append(f"uploader: {e}")
    return state
