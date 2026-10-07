"""
SAFE SIGHT - Video Routes (backend/routes/videos.py)

Endpoints for uploading videos, listing raw CCTV clips, checking processing status,
and fetching video-specific summary data.
"""

import os
import json
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from backend.schemas import VideoItem, ProcessingStatusResponse, SummaryResponse
from backend.services import (
    get_all_videos, get_video_by_id, add_uploaded_video,
    get_processing_status, execute_pipeline_task
)

router = APIRouter(prefix="/api/videos", tags=["Videos"])


@router.post("/upload", response_model=VideoItem)
async def upload_video(file: UploadFile = File(...)):
    """Upload a raw CCTV video (.mp4, .avi, .mov, .mkv)."""
    if not file.filename.endswith((".mp4", ".avi", ".mov", ".mkv")):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: .mp4, .avi, .mov, .mkv")

    raw_dir = "videos/raw"
    os.makedirs(raw_dir, exist_ok=True)
    file_path = os.path.join(raw_dir, file.filename)

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video file: {str(e)}")

    video_item = add_uploaded_video(file.filename, file_path)
    return video_item


@router.get("", response_model=List[VideoItem])
def list_videos():
    """List all registered video clips."""
    return get_all_videos()


@router.get("/{video_id}", response_model=VideoItem)
def get_video(video_id: str):
    """Get metadata for a specific video ID."""
    item = get_video_by_id(video_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Video ID '{video_id}' not found.")
    return item


@router.post("/{video_id}/process")
def start_processing(video_id: str, background_tasks: BackgroundTasks):
    """Launch background AI processing for a specific video ID."""
    item = get_video_by_id(video_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Video ID '{video_id}' not found.")

    status_obj = get_processing_status(video_id)
    if status_obj["status"] == "processing":
        return {"video_id": video_id, "status": "processing", "message": "Pipeline already running."}

    # Queue background processing task
    background_tasks.add_task(execute_pipeline_task, video_id)
    return {"video_id": video_id, "status": "processing", "message": f"SafeSight AI pipeline launched for {video_id}."}


@router.get("/{video_id}/status", response_model=ProcessingStatusResponse)
def check_status(video_id: str):
    """Check processing status and progress percentage."""
    item = get_video_by_id(video_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Video ID '{video_id}' not found.")
    return get_processing_status(video_id)


@router.get("/{video_id}/summary", response_model=SummaryResponse)
def get_summary(video_id: str):
    """Get high-level summary metrics from output/reports/{video_id}_summary.json."""
    summary_path = f"output/reports/{video_id}_summary.json"

    if not os.path.exists(summary_path):
        # Uninitialized / zero state before pipeline run
        item = get_video_by_id(video_id)
        fname = item["filename"] if item else video_id
        return SummaryResponse(
            input_video_name=fname,
            total_tracks=0,
            total_events=0,
            normal_events=0,
            unusual_events=0,
            high_risk_incidents=0,
            critical_incidents=0,
            total_incidents_logged=0,
            average_risk_score=0.0
        )

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read summary data: {e}")


@router.get("/{video_id}/annotated-video")
def get_annotated_video(video_id: str):
    """Stream the annotated output MP4 video generated for a specific video ID."""
    video_path = f"output/annotated/{video_id}_risk.mp4"
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail=f"Annotated video output not found for Video ID '{video_id}'.")
    return FileResponse(video_path, media_type="video/mp4")

