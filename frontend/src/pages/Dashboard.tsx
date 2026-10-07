import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { SummaryCards } from '../components/SummaryCards';
import { VideoUpload } from '../components/VideoUpload';
import { IncidentTable } from '../components/IncidentTable';
import { IncidentDetailModal } from '../components/IncidentDetailModal';
import { TimelineView } from '../components/TimelineView';
import { TrackingTable } from '../components/TrackingTable';
import { VideoPlayer } from '../components/VideoPlayer';
import { RiskChart } from '../components/RiskChart';
import { api } from '../services/api';
import { Zap, TrendingUp, Info } from 'lucide-react';

import {
  VideoItem,
  SummaryResponse,
  IncidentResponse,
  TimelineEvent,
  TrackResponse,
  ProcessingStatusResponse
} from '../types';

export const Dashboard: React.FC = () => {
  const [backendHealthy, setBackendHealthy] = useState(false);
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [selectedVideoId, setSelectedVideoId] = useState<string>('');

  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [incidents, setIncidents] = useState<IncidentResponse[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [tracks, setTracks] = useState<TrackResponse[]>([]);

  const [selectedIncident, setSelectedIncident] = useState<IncidentResponse | null>(null);
  const [selectedTrackFilter, setSelectedTrackFilter] = useState<string | undefined>(undefined);

  const [processing, setProcessing] = useState<boolean>(false);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatusResponse | null>(null);

  const checkHealthAndLoadVideos = useCallback(async () => {
    try {
      const health = await api.getHealth();
      setBackendHealthy(health.status === 'healthy');
      const vList = await api.listVideos();
      setVideos(vList);
      if (vList.length > 0 && !selectedVideoId) {
        setSelectedVideoId(vList[0].video_id);
      }
    } catch {
      setBackendHealthy(false);
    }
  }, [selectedVideoId]);

  const loadDashboardData = useCallback(async (videoId: string) => {
    if (!videoId) return;
    setSummary(null);
    setIncidents([]);
    setTimeline([]);
    setTracks([]);
    setSelectedIncident(null);
    setSelectedTrackFilter(undefined);
    try {
      const [sumData, incData, timeData, trackData, statusData] = await Promise.all([
        api.getSummary(videoId),
        api.getIncidents(videoId),
        api.getTimeline(videoId, selectedTrackFilter),
        api.getTracks(videoId),
        api.getStatus(videoId),
      ]);
      setSummary(sumData);
      setIncidents(incData);
      setTimeline(timeData);
      setTracks(trackData);
      setProcessingStatus(statusData);
      setProcessing(statusData.status === 'processing');
    } catch (err) {
      console.error(`Error loading data for ${videoId}:`, err);
    }
  }, [selectedTrackFilter]);

  useEffect(() => { checkHealthAndLoadVideos(); }, [checkHealthAndLoadVideos]);
  useEffect(() => { if (selectedVideoId) loadDashboardData(selectedVideoId); }, [selectedVideoId, loadDashboardData]);

  useEffect(() => {
    let interval: any = null;
    if (processing && selectedVideoId) {
      interval = setInterval(async () => {
        try {
          const st = await api.getStatus(selectedVideoId);
          setProcessingStatus(st);
          if (st.status === 'completed' || st.status === 'failed') {
            setProcessing(false);
            loadDashboardData(selectedVideoId);
            clearInterval(interval);
          }
        } catch { /* ignore */ }
      }, 2000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [processing, selectedVideoId, loadDashboardData]);

  const handleVideoUploaded = (video: VideoItem) => {
    setVideos((prev) => [...prev, video]);
    setSelectedVideoId(video.video_id);
  };

  const handleStartProcessing = async (videoId: string) => {
    try {
      setProcessing(true);
      await api.startProcessing(videoId);
    } catch (err) {
      alert('Failed to launch pipeline: ' + err);
      setProcessing(false);
    }
  };

  const selectedVideoItem = videos.find((v) => v.video_id === selectedVideoId) || null;
  const isProcessed =
    (processingStatus?.status === 'completed') ||
    (summary !== null && summary.processing_time_sec !== undefined);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--color-bg-deep)' }}>
      <Navbar
        backendHealthy={backendHealthy}
        videos={videos}
        selectedVideoId={selectedVideoId}
        onSelectVideo={setSelectedVideoId}
      />

      <main style={{ flex: 1, maxWidth: '1440px', width: '100%', margin: '0 auto', padding: '20px 24px 40px' }}>

        {/* Control panel */}
        <VideoUpload
          onVideoUploaded={handleVideoUploaded}
          onStartProcessing={handleStartProcessing}
          selectedVideo={selectedVideoItem}
          processing={processing}
        />

        {/* Processing progress */}
        {processingStatus && processingStatus.status === 'processing' && (
          <div
            className="animate-fade-in"
            style={{
              background: 'rgba(14,165,233,0.06)',
              border: '1px solid rgba(14,165,233,0.25)',
              borderRadius: '12px',
              padding: '14px 18px',
              marginBottom: '20px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Zap style={{ width: 14, height: 14, color: '#22d3ee' }} />
                <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#7dd3fc' }}>
                  {processingStatus.message}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '0.7rem', color: '#475569' }}>
                  {processingStatus.elapsed_sec.toFixed(0)}s elapsed
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)', fontSize: '0.8rem',
                  fontWeight: 700, color: '#22d3ee',
                }}>
                  {processingStatus.progress.toFixed(0)}%
                </span>
              </div>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${processingStatus.progress}%` }} />
            </div>
          </div>
        )}

        {/* Summary cards */}
        <SummaryCards summary={summary} />

        {/* Status message — before analysis */}
        {!isProcessed && !processing && (
          <div
            style={{
              display: 'flex', alignItems: 'center', gap: '10px',
              background: 'rgba(13,23,41,0.6)',
              border: '1px solid rgba(56,97,158,0.15)',
              borderRadius: '10px', padding: '12px 16px',
              marginBottom: '20px',
              fontSize: '0.75rem', color: '#475569',
            }}
          >
            <Info style={{ width: 14, height: 14, color: '#334155', flexShrink: 0 }} />
            {selectedVideoId
              ? `Video ${selectedVideoId} is ready. Click "Run SafeSight AI" to begin detection, tracking, and risk analysis.`
              : 'Upload a CCTV video file and click "Run SafeSight AI" to begin analysis.'
            }
          </div>
        )}

        {/* Main grid: 2 columns */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '18px' }}>

          {/* Column 1 */}
          <div>
            <VideoPlayer videoId={selectedVideoId} processed={isProcessed} />
            <IncidentTable incidents={incidents} onSelectIncident={setSelectedIncident} />
          </div>

          {/* Column 2 */}
          <div>
            <RiskChart summary={summary} timeline={timeline} />
            <TimelineView timeline={timeline} />
            <TrackingTable
              tracks={tracks}
              selectedTrackId={selectedTrackFilter}
              onSelectTrackId={(tid) => setSelectedTrackFilter((prev) => (prev === tid ? undefined : tid))}
            />
          </div>
        </div>
      </main>

      {/* Incident modal */}
      {selectedIncident && (
        <IncidentDetailModal
          incident={selectedIncident}
          videoId={selectedVideoId}
          onClose={() => setSelectedIncident(null)}
        />
      )}

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid rgba(56,97,158,0.15)',
        padding: '14px 24px',
        textAlign: 'center',
        fontSize: '0.65rem',
        color: '#334155',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
      }}>
        <TrendingUp style={{ width: 11, height: 11 }} />
        SafeSight CCTV Intelligence Subsystem · Context-Aware Behaviour & Explainable Risk Scoring Engine · Phases 1–8 Complete
      </footer>
    </div>
  );
};
