import {
  VideoItem,
  ProcessingStatusResponse,
  SummaryResponse,
  TrackResponse,
  BehaviourEventResponse,
  IncidentResponse,
  TimelineEvent
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = {
  async getHealth(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return res.json();
  },

  async listVideos(): Promise<VideoItem[]> {
    const res = await fetch(`${API_BASE_URL}/api/videos`);
    if (!res.ok) throw new Error('Failed to fetch videos list');
    return res.json();
  },

  async uploadVideo(file: File): Promise<VideoItem> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/api/videos/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Video upload failed');
    }
    return res.json();
  },

  async startProcessing(videoId: string): Promise<{ video_id: string; status: string; message: string }> {
    const res = await fetch(`${API_BASE_URL}/api/videos/${videoId}/process`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to launch AI processing pipeline');
    return res.json();
  },

  async getStatus(videoId: string): Promise<ProcessingStatusResponse> {
    const res = await fetch(`${API_BASE_URL}/api/videos/${videoId}/status`);
    if (!res.ok) throw new Error('Failed to fetch processing status');
    return res.json();
  },

  async getSummary(videoId: string): Promise<SummaryResponse> {
    const res = await fetch(`${API_BASE_URL}/api/videos/${videoId}/summary`);
    if (!res.ok) throw new Error('Failed to fetch summary metrics');
    return res.json();
  },

  async getEvents(videoId: string, riskLevel?: string): Promise<BehaviourEventResponse[]> {
    const url = riskLevel
      ? `${API_BASE_URL}/api/videos/${videoId}/events?risk_level=${riskLevel}`
      : `${API_BASE_URL}/api/videos/${videoId}/events`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch events');
    return res.json();
  },

  async getTracks(videoId: string): Promise<TrackResponse[]> {
    const res = await fetch(`${API_BASE_URL}/api/videos/${videoId}/tracks`);
    if (!res.ok) throw new Error('Failed to fetch tracks');
    return res.json();
  },

  async getIncidents(videoId: string): Promise<IncidentResponse[]> {
    const res = await fetch(`${API_BASE_URL}/api/videos/${videoId}/incidents`);
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  async getIncident(videoId: string, incidentId: string): Promise<IncidentResponse> {
    const res = await fetch(`${API_BASE_URL}/api/videos/${videoId}/incidents/${incidentId}`);
    if (!res.ok) throw new Error('Failed to fetch incident details');
    return res.json();
  },

  async getTimeline(videoId: string, trackId?: string): Promise<TimelineEvent[]> {
    const url = trackId
      ? `${API_BASE_URL}/api/videos/${videoId}/timeline?track_id=${trackId}`
      : `${API_BASE_URL}/api/videos/${videoId}/timeline`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch timeline');
    return res.json();
  },

  getEvidenceUrl(videoId: string, filename: string): string {
    const cleanFilename = filename.split(/[/\\]/).pop() || filename;
    return `${API_BASE_URL}/api/videos/${videoId}/evidence/${cleanFilename}`;
  },

  getReportHtmlUrl(videoId: string, incidentId: string): string {
    return `${API_BASE_URL}/api/videos/${videoId}/reports/${videoId}_incident_${incidentId}.html`;
  },

  getProcessedVideoUrl(videoId: string): string {
    return `${API_BASE_URL}/api/videos/${videoId}/annotated-video`;
  }
};
