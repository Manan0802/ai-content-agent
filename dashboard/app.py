import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from config import SETTINGS
from modules.job_store import list_jobs, get_job

_INDEX_HTML = os.path.join(os.path.dirname(__file__), "index.html")


def create_app(outputs_dir: str | None = None) -> FastAPI:
    outputs_dir = outputs_dir or SETTINGS.outputs_dir
    app = FastAPI(title="AI Content Agent — Dashboard")

    @app.get("/api/jobs")
    def api_jobs():
        return list_jobs(outputs_dir)

    @app.get("/api/jobs/{job_id}")
    def api_job(job_id: str):
        job = get_job(job_id, outputs_dir)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        return job

    @app.get("/video/{job_id}")
    def video(job_id: str):
        mp4 = os.path.join(outputs_dir, job_id, "render", "final.mp4")
        if not os.path.exists(mp4) or os.path.getsize(mp4) == 0:
            raise HTTPException(status_code=404, detail="video not found")
        return FileResponse(mp4, media_type="video/mp4")

    @app.get("/", response_class=HTMLResponse)
    def index():
        with open(_INDEX_HTML, encoding="utf-8") as f:
            return f.read()

    return app
