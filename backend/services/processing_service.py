"""
SAFE SIGHT - Background AI Processing Service (backend/services/processing_service.py)

Manages video registration, per-video isolation, status polling, and background execution of the
end-to-end SafeSight AI pipeline.
"""

import os
import time
import json
import traceback
from typing import Dict, Any, List, Optional
from core.video import get_video_info
import pipeline


# In-memory databases for state management
videos_db: Dict[str, Dict[str, Any]] = {}
processing_status_db: Dict[str, Dict[str, Any]] = {}


def register_existing_videos():
    """Scan videos/raw and register existing CCTV videos on startup."""
    raw_dir = "videos/raw"
    if not os.path.exists(raw_dir):
        return

    vid_idx = 1
    for fname in sorted(os.listdir(raw_dir)):
        if fname.endswith((".mp4", ".avi", ".mov", ".mkv")):
            vid_id = f"VID-{vid_idx:03d}"
            fpath = os.path.join(raw_dir, fname)
            info = get_video_info(fpath, verify_frames=False)

            summary_file = f"output/reports/{vid_id}_summary.json"
            is_done = os.path.exists(summary_file)

            videos_db[vid_id] = {
                "video_id": vid_id,
                "filename": fname,
                "file_path": fpath,
                "status": "completed" if is_done else "uploaded",
                "resolution": info.get("resolution", "1280 x 720"),
                "fps": info.get("fps", 6.0),
                "total_frames": info.get("total_frames", 102),
                "duration_sec": info.get("duration_seconds", 17.0)
            }

            processing_status_db[vid_id] = {
                "video_id": vid_id,
                "status": "completed" if is_done else "uploaded",
                "progress": 100.0 if is_done else 0.0,
                "message": "Processing completed successfully" if is_done else "Ready to process",
                "elapsed_sec": 10.0 if is_done else 0.0
            }
            vid_idx += 1


# Auto-register existing raw videos on startup
register_existing_videos()


def get_all_videos() -> List[Dict[str, Any]]:
    """Return list of all registered video items."""
    return list(videos_db.values())


def get_video_by_id(video_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve video metadata by video ID."""
    return videos_db.get(video_id)


def add_uploaded_video(filename: str, file_path: str) -> Dict[str, Any]:
    """Register a newly uploaded raw video and initialize blank state."""
    vid_id = f"VID-{len(videos_db) + 1:03d}"
    info = get_video_info(file_path, verify_frames=True)

    item = {
        "video_id": vid_id,
        "filename": filename,
        "file_path": file_path,
        "status": "uploaded",
        "resolution": info.get("resolution", "1280 x 720"),
        "fps": info.get("fps", 6.0),
        "total_frames": info.get("total_frames", 102),
        "duration_sec": info.get("duration_seconds", 17.0)
    }

    videos_db[vid_id] = item
    processing_status_db[vid_id] = {
        "video_id": vid_id,
        "status": "uploaded",
        "progress": 0.0,
        "message": "Uploaded successfully. Ready for AI analysis.",
        "elapsed_sec": 0.0
    }
    return item


def get_processing_status(video_id: str) -> Dict[str, Any]:
    """Retrieve processing status for video ID."""
    if video_id in processing_status_db:
        return processing_status_db[video_id]
    return {
        "video_id": video_id,
        "status": "uploaded",
        "progress": 0.0,
        "message": "Video uploaded",
        "elapsed_sec": 0.0
    }


def execute_pipeline_task(video_id: str):
    """
    Background worker executing pipeline.run_pipeline for a specific video_id.
    """
    video_item = videos_db.get(video_id)
    if not video_item:
        print(f"[ERROR] Cannot process unknown video ID: {video_id}")
        return

    fpath = video_item["file_path"]

    # Update status to processing
    video_item["status"] = "processing"
    processing_status_db[video_id] = {
        "video_id": video_id,
        "status": "processing",
        "progress": 25.0,
        "message": "Executing YOLOv8 Person Detection & ByteTrack Persistent Tracking...",
        "elapsed_sec": 2.0
    }

    start_t = time.time()

    def update_progress(current_frame, total_frames, pct):
        elapsed_cur = round(time.time() - start_t, 1)
        processing_status_db[video_id] = {
            "video_id": video_id,
            "status": "processing",
            "progress": pct,
            "message": f"Analyzing frame {current_frame}/{total_frames} ({pct:.0f}%)...",
            "elapsed_sec": elapsed_cur
        }

    try:
        # Run AI Pipeline with explicit video_id isolation
        summary = pipeline.run_pipeline(
            input_video_path=fpath,
            video_id=video_id,
            progress_callback=update_progress
        )

        elapsed = round(time.time() - start_t, 2)
        video_item["status"] = "completed"
        processing_status_db[video_id] = {
            "video_id": video_id,
            "status": "completed",
            "progress": 100.0,
            "message": f"SafeSight AI Pipeline completed! Found {summary['total_tracks']} people.",
            "elapsed_sec": elapsed
        }
    except Exception as e:
        elapsed = round(time.time() - start_t, 2)
        err_msg = str(e)
        print(f"[ERROR] Pipeline failed for {video_id}: {err_msg}")
        traceback.print_exc()

        video_item["status"] = "failed"
        processing_status_db[video_id] = {
            "video_id": video_id,
            "status": "failed",
            "progress": 0.0,
            "message": f"Pipeline processing error: {err_msg}",
            "elapsed_sec": elapsed
        }
