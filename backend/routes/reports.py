"""
SAFE SIGHT - Reports & Evidence Routes (backend/routes/reports.py)

Endpoints for accessing evidence image snapshots and downloadable JSON/HTML incident reports.
"""

import os
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/videos/{video_id}", tags=["Reports & Evidence"])


@router.get("/evidence/{filename}")
def get_evidence_image(video_id: str, filename: str):
    """Serve evidence image snapshot safely for a specific video ID."""
    safe_filename = os.path.basename(filename)

    # Check video-specific evidence folder first, then global output/evidence
    filepath = os.path.join("output/evidence", video_id, safe_filename)
    if not os.path.exists(filepath):
        filepath = os.path.join("output/evidence", safe_filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Evidence image '{filename}' not found for {video_id}.")

    return FileResponse(filepath, media_type="image/jpeg")


@router.get("/reports")
def list_reports(video_id: str):
    """List all available report files for a specific video ID."""
    reports_dir = "output/reports"
    if not os.path.exists(reports_dir):
        return []

    reports = []
    prefix = f"{video_id}_"
    for fname in os.listdir(reports_dir):
        if fname.startswith(prefix) and fname.endswith((".json", ".html")):
            reports.append({
                "filename": fname,
                "type": "HTML" if fname.endswith(".html") else "JSON",
                "url": f"/api/videos/{video_id}/reports/{fname}"
            })
    return reports


@router.get("/reports/{filename}")
def get_report_file(video_id: str, filename: str):
    """Serve specific JSON or HTML incident report file for a video ID."""
    safe_filename = os.path.basename(filename)
    filepath = os.path.join("output/reports", safe_filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Report file '{filename}' not found for {video_id}.")

    media_type = "text/html" if filename.endswith(".html") else "application/json"
    return FileResponse(filepath, media_type=media_type)
