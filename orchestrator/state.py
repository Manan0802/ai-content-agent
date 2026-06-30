import uuid
from datetime import datetime, timezone
from typing import TypedDict


class ContentState(TypedDict, total=False):
    job_id: str
    created_at: str
    status: str          # idle | running | paused_for_human | complete | failed
    mode: str            # full_auto | semi_auto | script_only | manual
    niche: str
    language: str
    format: str          # short | long
    topic: str
    topic_candidates: list[dict]
    script: dict
    hitl_checkpoints: list[str]
    human_approved: dict
    errors: list[str]


def new_state(niche: str, mode: str, language: str, format: str,
              hitl_checkpoints: list[str]) -> ContentState:
    return ContentState(
        job_id=str(uuid.uuid4())[:8],
        created_at=datetime.now(timezone.utc).isoformat(),
        status="idle",
        mode=mode,
        niche=niche,
        language=language,
        format=format,
        topic="",
        topic_candidates=[],
        script={},
        hitl_checkpoints=hitl_checkpoints,
        human_approved={},
        errors=[],
    )
