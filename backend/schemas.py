"""
SAFE SIGHT - Pydantic API Schemas (backend/schemas.py)

Defines clean data models for FastAPI request and response endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "healthy"


class VideoItem(BaseModel):
    video_id: str
    filename: str
    status: str  # 'uploaded', 'processing', 'completed', 'failed'
    file_path: str
    resolution: Optional[str] = "1280 x 720"
    fps: Optional[float] = 6.0
    total_frames: Optional[int] = 0
    duration_sec: Optional[float] = 0.0


class ProcessingStatusResponse(BaseModel):
    video_id: str
    status: str  # 'uploaded', 'processing', 'completed', 'failed'
    progress: float  # 0.0 to 100.0
    message: str
    elapsed_sec: float = 0.0


class SummaryResponse(BaseModel):
    total_tracks: int = 0
    total_events: int = 0
    normal_events: int = 0
    unusual_events: int = 0
    high_risk_incidents: int = 0
    critical_incidents: int = 0
    total_incidents_logged: int = 0
    average_risk_score: float = 0.0
    input_video_name: str = ""
    processing_time_sec: float = 0.0


class TrackResponse(BaseModel):
    track_id: str
    raw_id: int
    first_seen_sec: float
    last_seen_sec: float
    active_frames: int
    zones_visited: List[str]
    behaviours_observed: List[str]


class BehaviourEventResponse(BaseModel):
    event_id: str
    track_id: str
    timestamp: float
    frame: int
    behaviour: str
    zone: str
    context_status: str
    risk_score: int
    risk_level: str
    risk_reasons: List[str]
    explanation: str
    incident_id: Optional[str] = None
    evidence: List[str] = []


class IncidentResponse(BaseModel):
    incident_id: str
    track_id: str
    cctv_time: str
    start_time: float
    end_time: float
    zone: str
    behaviour: str
    risk_score: int
    risk_level: str
    risk_reasons: List[str]
    explanation: str
    status: str = "OPEN"
    evidence: List[str] = []


class TimelineEvent(BaseModel):
    timestamp: float
    cctv_time: str
    event_type: str
    behaviour: str
    zone: str
    status: str
    description: str
