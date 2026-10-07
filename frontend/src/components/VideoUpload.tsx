import React, { useState } from 'react';
import { Upload, Play, Loader2, FileVideo, CheckCircle, ChevronRight, Cpu } from 'lucide-react';
import { api } from '../services/api';
import { VideoItem } from '../types';

interface VideoUploadProps {
  onVideoUploaded: (video: VideoItem) => void;
  onStartProcessing: (videoId: string) => void;
  selectedVideo: VideoItem | null;
  processing: boolean;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({
  onVideoUploaded,
  onStartProcessing,
  selectedVideo,
  processing
}) => {
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploaded, setUploaded] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError(null);
      setUploaded(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setError(null);
    try {
      const videoItem = await api.uploadVideo(selectedFile);
      onVideoUploaded(videoItem);
      setUploaded(true);
      setSelectedFile(null);
    } catch (err: any) {
      setError(err.message || 'Failed to upload video');
    } finally {
      setUploading(false);
    }
  };

  const canProcess = selectedVideo && !processing;
  const isCompleted = selectedVideo?.status === 'completed';

  return (
    <div className="glass-card mb-6" style={{ padding: '20px 24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '18px' }}>
        <div className="section-icon" style={{
          background: 'rgba(34,211,238,0.1)',
          borderColor: 'rgba(34,211,238,0.25)',
          color: '#22d3ee',
        }}>
          <Cpu style={{ width: 16, height: 16 }} />
        </div>
        <div>
          <div className="section-title">Video Analysis Control Panel</div>
          <div className="section-subtitle">Upload raw CCTV footage and execute the full SafeSight AI pipeline</div>
        </div>

        {/* Status breadcrumb */}
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <StepDot label="Upload" active={!selectedVideo} done={!!selectedVideo} />
          <ChevronRight style={{ width: 12, height: 12, color: '#334155' }} />
          <StepDot label="Analyze" active={!!selectedVideo && !isCompleted} done={isCompleted} />
          <ChevronRight style={{ width: 12, height: 12, color: '#334155' }} />
          <StepDot label="Results" active={false} done={isCompleted} />
        </div>
      </div>

      {/* Controls row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>

        {/* File picker */}
        <label style={{
          display: 'flex', alignItems: 'center', gap: '8px',
          background: 'rgba(22,32,53,0.7)',
          border: '1px solid rgba(56,97,158,0.25)',
          borderRadius: '9px', padding: '9px 16px',
          cursor: 'pointer', transition: 'all 0.2s',
          fontSize: '0.78rem', fontWeight: 500,
          color: selectedFile ? '#e2e8f0' : '#64748b',
          flex: '1', minWidth: '200px', maxWidth: '320px',
        }}
          onMouseEnter={e => (e.currentTarget.style.borderColor = 'rgba(34,211,238,0.35)')}
          onMouseLeave={e => (e.currentTarget.style.borderColor = 'rgba(56,97,158,0.25)')}
        >
          <FileVideo style={{ width: 15, height: 15, color: selectedFile ? '#22d3ee' : '#475569', flexShrink: 0 }} />
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {selectedFile ? selectedFile.name : 'Choose CCTV Video File'}
          </span>
          <input
            type="file"
            accept="video/mp4,video/avi,video/mov,video/mkv"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>

        {/* Upload button */}
        {selectedFile && (
          <button
            className="btn-primary"
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading
              ? <Loader2 style={{ width: 14, height: 14 }} className="animate-spin" />
              : <Upload style={{ width: 14, height: 14 }} />
            }
            {uploading ? 'Uploading...' : 'Upload Video'}
          </button>
        )}

        {/* Upload success indicator */}
        {uploaded && !selectedFile && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            fontSize: '0.75rem', fontWeight: 600, color: '#10b981',
            background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)',
            padding: '8px 14px', borderRadius: '9px',
          }}>
            <CheckCircle style={{ width: 14, height: 14 }} />
            Video uploaded — select it from the dropdown above
          </div>
        )}

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* Selected video info */}
        {selectedVideo && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '8px 14px', borderRadius: '9px',
            background: 'rgba(13,23,41,0.6)',
            border: '1px solid rgba(56,97,158,0.18)',
          }}>
            <div style={{ fontSize: '0.65rem', color: '#475569', lineHeight: 1.8 }}>
              <div style={{ color: '#64748b', marginBottom: '1px' }}>
                <span className="track-id-badge" style={{ fontSize: '0.62rem' }}>{selectedVideo.video_id}</span>
                {' '}{selectedVideo.filename.length > 30 ? selectedVideo.filename.slice(0, 27) + '…' : selectedVideo.filename}
              </div>
              <div style={{ color: '#475569' }}>
                {selectedVideo.resolution} · {selectedVideo.fps.toFixed(1)} fps · {selectedVideo.total_frames} frames · {selectedVideo.duration_sec.toFixed(1)}s
              </div>
            </div>
          </div>
        )}

        {/* Run AI button */}
        {selectedVideo && (
          <button
            className="btn-run-ai"
            onClick={() => onStartProcessing(selectedVideo.video_id)}
            disabled={processing}
          >
            {processing
              ? <Loader2 style={{ width: 15, height: 15 }} className="animate-spin" />
              : <Play style={{ width: 15, height: 15 }} />
            }
            {processing ? 'Pipeline Running...' : 'Run SafeSight AI'}
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div style={{
          marginTop: '12px', fontSize: '0.75rem', color: '#f87171',
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
          padding: '8px 14px', borderRadius: '8px',
        }}>
          {error}
        </div>
      )}
    </div>
  );
};

const StepDot: React.FC<{ label: string; active: boolean; done: boolean }> = ({ label, active, done }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
    <div style={{
      width: 7, height: 7, borderRadius: '50%',
      background: done ? '#10b981' : active ? '#22d3ee' : '#1e2d45',
      border: `1.5px solid ${done ? '#10b981' : active ? '#22d3ee' : '#334155'}`,
      boxShadow: active ? '0 0 6px rgba(34,211,238,0.5)' : done ? '0 0 6px rgba(16,185,129,0.4)' : 'none',
    }} />
    <span style={{
      fontSize: '0.6rem', fontWeight: 600,
      color: done ? '#10b981' : active ? '#94a3b8' : '#334155',
      letterSpacing: '0.04em',
    }}>{label}</span>
  </div>
);
