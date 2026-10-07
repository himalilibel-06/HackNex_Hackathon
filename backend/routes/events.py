"""
SAFE SIGHT - Events, Tracks & Timeline Routes (backend/routes/events.py)

Endpoints for querying video-specific behaviour events, track details, and chronological timelines.
"""

import os
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.schemas import BehaviourEventResponse, TrackResponse, TimelineEvent

router = APIRouter(prefix="/api/videos/{video_id}", tags=["Events & Tracks"])


@router.get("/events", response_model=List[BehaviourEventResponse])
def get_events(video_id: str,
               risk_level: Optional[str] = Query(None),
               track_id: Optional[str] = Query(None),
               zone: Optional[str] = Query(None)):
    """Retrieve full behaviour event records for a specific video ID."""
    events_json = f"output/annotated/{video_id}_full_events.json"

    if not os.path.exists(events_json):
        return []

    try:
        with open(events_json, "r", encoding="utf-8") as f:
            events = json.load(f)

        filtered = events
        if risk_level:
            filtered = [e for e in filtered if e.get("risk_level", "").upper() == risk_level.upper()]
        if track_id:
            filtered = [e for e in filtered if e.get("track_id", "").upper() == track_id.upper()]
        if zone:
            filtered = [e for e in filtered if zone.lower() in e.get("zone", "").lower()]

        return filtered
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading events data: {e}")


@router.get("/tracks", response_model=List[TrackResponse])
def get_tracks(video_id: str):
    """Retrieve per-person track details and lifespan summaries for a specific video ID."""
    json_path = f"output/annotated/{video_id}_behaviour_data.json"

    if not os.path.exists(json_path):
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            raw_tracks = json.load(f)

        track_list = []
        for pid, records in raw_tracks.items():
            if not records:
                continue
            first_seen = records[0]["timestamp"]
            last_seen = records[-1]["timestamp"]
            active_frames = len(records)
            raw_id = records[0]["raw_id"]
            zones_visited = list(dict.fromkeys([r["zone"] for r in records]))
            behaviours_observed = list(dict.fromkeys([r["behaviour"] for r in records]))

            track_list.append({
                "track_id": pid,
                "raw_id": raw_id,
                "first_seen_sec": first_seen,
                "last_seen_sec": last_seen,
                "active_frames": active_frames,
                "zones_visited": zones_visited,
                "behaviours_observed": behaviours_observed
            })

        return track_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading tracks data: {e}")


@router.get("/timeline", response_model=List[TimelineEvent])
def get_timeline(video_id: str, track_id: Optional[str] = Query(None)):
    """Retrieve chronological activity timelines for a specific video ID."""
    timelines_json = f"output/annotated/{video_id}_person_timelines.json"

    if not os.path.exists(timelines_json):
        return []

    try:
        with open(timelines_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        events_flat = []
        if track_id:
            raw_events = data.get(track_id, [])
            for e in raw_events:
                events_flat.append({
                    "timestamp": e["timestamp"],
                    "cctv_time": e.get("cctv_time", "22:14"),
                    "event_type": e["event_type"],
                    "behaviour": e["behaviour"],
                    "zone": e["zone"],
                    "status": e.get("status", "normal"),
                    "description": e.get("description", f"{e['behaviour']} in {e['zone']}")
                })
        else:
            for pid, raw_events in data.items():
                for e in raw_events:
                    events_flat.append({
                        "timestamp": e["timestamp"],
                        "cctv_time": e.get("cctv_time", "22:14"),
                        "event_type": e["event_type"],
                        "behaviour": e["behaviour"],
                        "zone": e["zone"],
                        "status": e.get("status", "normal"),
                        "description": f"[{pid}] {e['behaviour']} in {e['zone']}"
                    })
            events_flat.sort(key=lambda x: x["timestamp"])

        return events_flat
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading timeline data: {e}")
