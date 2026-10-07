"""
SAFE SIGHT - Incidents Routes (backend/routes/incidents.py)

Endpoints for querying video-specific safety incidents and details.
"""

import os
import json
from typing import List
from fastapi import APIRouter, HTTPException
from backend.schemas import IncidentResponse

router = APIRouter(prefix="/api/videos/{video_id}/incidents", tags=["Incidents"])


@router.get("", response_model=List[IncidentResponse])
def get_incidents(video_id: str):
    """Retrieve all safety incidents logged for a specific video ID."""
    incidents_json = f"output/reports/{video_id}_incidents.json"

    if not os.path.exists(incidents_json):
        return []

    try:
        with open(incidents_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading incidents data: {e}")


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(video_id: str, incident_id: str):
    """Retrieve single incident details by incident ID for a specific video ID."""
    incidents_json = f"output/reports/{video_id}_incidents.json"

    if not os.path.exists(incidents_json):
        raise HTTPException(status_code=404, detail=f"Incident ID '{incident_id}' not found.")

    try:
        with open(incidents_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            for inc in data:
                if inc["incident_id"].upper() == incident_id.upper():
                    return inc
        raise HTTPException(status_code=404, detail=f"Incident ID '{incident_id}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading incident details: {e}")
