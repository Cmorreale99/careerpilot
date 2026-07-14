"""CareerPilot profile server — implementation step 9 of claude.md.

Serves the career-profile site. The renderable document is the
LLM-organized summary profile (v2 step 3); the original complete
corpus is preserved separately at its own endpoints:

  GET /api/profile           summary profile as JSON (render button)
  GET /api/profile/download  summary profile as a .docx attachment
  GET /api/corpus            complete sourced corpus profile as JSON
  GET /api/corpus/download   complete corpus as a .docx attachment

Run:
    python -m uvicorn app.server:app --port 8300
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.profile_builder import (
    build_profile,
    build_summary_profile,
    profile_docx,
    summary_docx,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

app = FastAPI(title="CareerPilot")


@app.get("/api/profile")
def api_profile() -> dict:
    return build_summary_profile()


@app.get("/api/profile/download")
def api_profile_download() -> Response:
    document = summary_docx(build_summary_profile())
    return Response(
        document,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="cam-morreale-career-profile.docx"'},
    )


@app.get("/api/corpus")
def api_corpus() -> dict:
    return build_profile()


@app.get("/api/corpus/download")
def api_corpus_download() -> Response:
    document = profile_docx(build_profile())
    return Response(
        document,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="cam-morreale-complete-corpus.docx"'},
    )


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
