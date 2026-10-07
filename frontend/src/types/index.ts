export interface VideoItem {
  video_id: string;
  filename: string;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  file_path: string;
  resolution?: string;
  fps?: number;
  total_frames?: number;
  duration_sec?: number;
}

export interface ProcessingStatusResponse {
  video_id: string;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  elapsed_sec: number;
}

export interface SummaryResponse {
  total_tracks: number;
  total_events: number;
  normal_events: number;
  unusual_events: number;
  high_risk_incidents: number;
  critical_incidents: number;
  total_incidents_logged: number;
  average_risk_score: number;
  input_video_name: string;
  processing_time_sec: number;
}

export interface TrackResponse {
  track_id: string;
  raw_id: number;
  first_seen_sec: number;
  last_seen_sec: number;
  active_frames: number;
  zones_visited: string[];
  behaviours_observed: string[];
}

export interface BehaviourEventResponse {
  event_id: string;
  track_id: string;
  timestamp: number;
  frame: number;
  behaviour: string;
  zone: string;
  context_status: 'normal' | 'potentially_unusual' | 'potential_safety_concern';
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_reasons: string[];
  explanation: string;
  incident_id?: string;
  evidence: string[];
}

export interface IncidentResponse {
  incident_id: string;
  track_id: string;
  cctv_time: string;
  start_time: number;
  end_time: number;
  zone: string;
  behaviour: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_reasons: string[];
  explanation: string;
  status: string;
  evidence: string[];
}

export interface TimelineEvent {
  timestamp: number;
  cctv_time: string;
  event_type: string;
  behaviour: string;
  zone: string;
  status: string;
  description: string;
}
