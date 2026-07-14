"""CareerPilot profile server — implementation step 9 of claude.md.

Serves the career-profile site and two endpoints backed by the
deterministic profile builder (no LLM):

  GET /api/profile          assembled profile as JSON (render button)
  GET /api/profile/download the same profile as a .docx attachment

Run:
    python -m uvicorn app.server:app --port 8300
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.profile_builder import build_profile, profile_docx

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="CareerPilot")


@app.get("/api/profile")
def api_profile() -> dict:
    return build_profile()


@app.get("/api/profile/download")
def api_profile_download() -> Response:
    document = profile_docx(build_profile())
    return Response(
        document,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="cam-morreale-career-profile.docx"'},
    )


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
