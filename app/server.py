"""CareerPilot profile server — implementation step 9 of claude.md.

Serves the career-profile site and two endpoints backed by the
deterministic profile builder (no LLM):

  GET /api/profile          assembled profile as JSON (render button)
  GET /api/profile/download the same profile as a Markdown attachment

Run:
    python -m uvicorn app.server:app --port 8300
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.profile_builder import build_profile, profile_markdown

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="CareerPilot")


@app.get("/api/profile")
def api_profile() -> dict:
    return build_profile()


@app.get("/api/profile/download")
def api_profile_download() -> PlainTextResponse:
    markdown = profile_markdown(build_profile())
    return PlainTextResponse(
        markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="cam-morreale-career-profile.md"'},
    )


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
