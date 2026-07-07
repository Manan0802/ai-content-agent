from fastapi.testclient import TestClient
from orchestrator.state import new_state
from modules.job_store import save_job
from dashboard.app import create_app


def _seed(tmp_path, topic="Cursed Village", status="media_complete"):
    s = new_state("horror", "semi_auto", "hinglish", "short", ["topic"])
    s["topic"] = topic
    s["status"] = status
    save_job(s, str(tmp_path))
    return s


def test_api_jobs_lists_seeded_job(tmp_path):
    s = _seed(tmp_path)
    client = TestClient(create_app(str(tmp_path)))
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) == 1
    assert jobs[0]["job_id"] == s["job_id"]
    assert jobs[0]["topic"] == "Cursed Village"


def test_api_job_detail_and_404(tmp_path):
    s = _seed(tmp_path)
    client = TestClient(create_app(str(tmp_path)))
    ok = client.get(f"/api/jobs/{s['job_id']}")
    assert ok.status_code == 200
    assert ok.json()["topic"] == "Cursed Village"
    missing = client.get("/api/jobs/nope")
    assert missing.status_code == 404


def test_video_404_when_no_mp4(tmp_path):
    s = _seed(tmp_path)
    client = TestClient(create_app(str(tmp_path)))
    resp = client.get(f"/video/{s['job_id']}")
    assert resp.status_code == 404


def test_video_served_when_present(tmp_path):
    s = _seed(tmp_path)
    render_dir = tmp_path / s["job_id"] / "render"
    render_dir.mkdir(parents=True)
    (render_dir / "final.mp4").write_bytes(b"\x00" * 20)
    client = TestClient(create_app(str(tmp_path)))
    resp = client.get(f"/video/{s['job_id']}")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("video/")


def test_index_page_renders(tmp_path):
    client = TestClient(create_app(str(tmp_path)))
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AI Content Agent" in resp.text
    assert "/api/jobs" in resp.text  # the page fetches the jobs API
