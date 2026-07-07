import os
import glob
import json
from orchestrator.state import ContentState


def save_job(state: ContentState, outputs_dir: str) -> str:
    job_dir = os.path.join(outputs_dir, state["job_id"])
    os.makedirs(job_dir, exist_ok=True)
    path = os.path.join(job_dir, "state.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return path


def get_job(job_id: str, outputs_dir: str) -> dict | None:
    path = os.path.join(outputs_dir, job_id, "state.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _has_video(outputs_dir: str, job_id: str) -> bool:
    mp4 = os.path.join(outputs_dir, job_id, "render", "final.mp4")
    return os.path.exists(mp4) and os.path.getsize(mp4) > 0


def list_jobs(outputs_dir: str) -> list[dict]:
    if not os.path.isdir(outputs_dir):
        return []
    summaries = []
    for state_path in glob.glob(os.path.join(outputs_dir, "*", "state.json")):
        try:
            with open(state_path, encoding="utf-8") as f:
                state = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        job_id = state.get("job_id", "")
        summaries.append({
            "job_id": job_id,
            "status": state.get("status", ""),
            "niche": state.get("niche", ""),
            "topic": state.get("topic", ""),
            "created_at": state.get("created_at", ""),
            "has_video": _has_video(outputs_dir, job_id),
        })
    summaries.sort(key=lambda j: j["created_at"], reverse=True)
    return summaries
