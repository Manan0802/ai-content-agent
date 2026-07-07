from orchestrator.state import new_state
from modules.job_store import save_job, list_jobs, get_job


def _job(niche, topic, created_at, status="media_complete"):
    s = new_state(niche, "semi_auto", "hinglish", "short", ["topic"])
    s["topic"] = topic
    s["status"] = status
    s["created_at"] = created_at
    return s


def test_save_and_get_round_trips(tmp_path):
    s = _job("horror", "Cursed Village", "2026-07-07T10:00:00+00:00")
    path = save_job(s, str(tmp_path))
    assert path.endswith("state.json")
    loaded = get_job(s["job_id"], str(tmp_path))
    assert loaded["topic"] == "Cursed Village"
    assert loaded["niche"] == "horror"


def test_get_job_missing_returns_none(tmp_path):
    assert get_job("nope", str(tmp_path)) is None


def test_list_jobs_newest_first_and_video_flag(tmp_path):
    older = _job("horror", "Old", "2026-07-07T09:00:00+00:00")
    newer = _job("finance", "New", "2026-07-07T11:00:00+00:00")
    save_job(older, str(tmp_path))
    save_job(newer, str(tmp_path))
    # give the newer job a real video file
    render_dir = tmp_path / newer["job_id"] / "render"
    render_dir.mkdir(parents=True)
    (render_dir / "final.mp4").write_bytes(b"\x00" * 10)

    jobs = list_jobs(str(tmp_path))
    assert [j["topic"] for j in jobs] == ["New", "Old"]
    assert jobs[0]["has_video"] is True
    assert jobs[1]["has_video"] is False
    assert jobs[0]["niche"] == "finance"


def test_list_jobs_missing_dir_returns_empty():
    assert list_jobs("/tmp/does-not-exist-aica-xyz") == []
