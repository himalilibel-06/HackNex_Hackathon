import React from 'react';
import { Film, Play, CheckCircle2, BarChart2 } from 'lucide-react';
import { api } from '../services/api';

interface VideoPlayerProps {
  videoId: string;
  processed: boolean;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoId, processed }) => {
  const videoUrl = api.getProcessedVideoUrl(videoId);

  return (
    <div className="glass-card mb-5" style={{ padding: '18px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
          <div className="section-icon" style={{
            background: 'rgba(34,211,238,0.1)',
            borderColor: 'rgba(34,211,238,0.25)',
          }}>
            <Film style={{ width: 15, height: 15, color: '#22d3ee' }} />
          </div>
          <div>
            <div className="section-title">Annotated CCTV Feed</div>
            <div className="section-subtitle">
              {videoId ? `Feed: ${videoId}` : 'No video selected'}
            </div>
          </div>
        </div>

        {/* AI Analyzed badge — only when truly processed */}
        {processed && (
          <div className="ai-analyzed-badge animate-fade-in">
            <div className="ai-badge-dot" />
            AI ANALYZED
          </div>
        )}
      </div>

      {/* Video area */}
      <div className="video-container" style={{ minHeight: 300 }}>
        {processed ? (
          <video
            key={videoId}
            src={videoUrl}
            controls
            autoPlay
            loop
            muted
            style={{
              width: '100%',
              maxHeight: 480,
              objectFit: 'contain',
              display: 'block',
            }}
          />
        ) : (
          <div style={{
            minHeight: 300,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '14px',
            padding: '40px',
          }}>
            <div style={{
              width: 56, height: 56, borderRadius: '14px',
              background: 'rgba(13,23,41,0.9)',
              border: '1px solid rgba(56,97,158,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Play style={{ width: 24, height: 24, color: '#22d3ee', marginLeft: 3 }} />
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
                No Annotated Output Yet
              </div>
              <div style={{ fontSize: '0.72rem', color: '#475569', maxWidth: 220, lineHeight: 1.6 }}>
                Run SafeSight AI on a CCTV video to generate YOLOv8-annotated footage with risk overlays.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer stats row */}
      {processed && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '16px',
          marginTop: '12px', paddingTop: '12px',
          borderTop: '1px solid rgba(56,97,158,0.12)',
        }}>
          <BarChart2 style={{ width: 13, height: 13, color: '#475569', flexShrink: 0 }} />
          <span style={{ fontSize: '0.65rem', color: '#475569' }}>
            YOLOv8 person detection · ByteTrack persistent IDs · Risk score overlays · Evidence snapshots
          </span>
        </div>
      )}
    </div>
  );
};
