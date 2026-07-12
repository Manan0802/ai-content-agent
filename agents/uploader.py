from orchestrator.state import ContentState
from config import SETTINGS


def _build_metadata(state: ContentState):
    script = state.get("script", {})
    title = (script.get("title") or state.get("topic") or "Untitled")[:100]
    hook = script.get("hook", "")
    hashtags = script.get("hashtags", [])
    # #Shorts in the description is what marks the upload as a YouTube Short.
    tag_line = " ".join(hashtags + ["#Shorts"])
    description = f"{hook}\n\n{SETTINGS.ai_disclosure_text}\n\n{tag_line}".strip()
    tags = [t.lstrip("#") for t in hashtags]
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
