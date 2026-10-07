import React from 'react';
import { Shield, Wifi, WifiOff, ChevronDown, Activity } from 'lucide-react';
import { VideoItem } from '../types';

interface NavbarProps {
  backendHealthy: boolean;
  videos: VideoItem[];
  selectedVideoId: string;
  onSelectVideo: (videoId: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  backendHealthy,
  videos,
  selectedVideoId,
  onSelectVideo
}) => {
  const selectedVideo = videos.find(v => v.video_id === selectedVideoId);

  return (
    <header
      style={{
        background: 'rgba(6, 12, 26, 0.95)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(56, 97, 158, 0.2)',
        position: 'sticky',
        top: 0,
        zIndex: 40,
      }}
      className="px-6 py-3"
    >
      <div className="max-w-screen-2xl mx-auto flex items-center justify-between gap-4">

        {/* Brand */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <div style={{
            background: 'linear-gradient(135deg, rgba(34,211,238,0.15) 0%, rgba(59,130,246,0.1) 100%)',
            border: '1px solid rgba(34,211,238,0.25)',
            borderRadius: '10px',
            padding: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Shield style={{ width: 22, height: 22, color: '#22d3ee' }} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em', margin: 0 }}>
                SafeSight
              </h1>
              <span style={{
                fontSize: '0.6rem', fontWeight: 700, letterSpacing: '0.1em',
                textTransform: 'uppercase', color: '#22d3ee',
                background: 'rgba(34,211,238,0.1)', border: '1px solid rgba(34,211,238,0.25)',
                padding: '2px 7px', borderRadius: '5px'
              }}>
                CCTV AI
              </span>
            </div>
            <p style={{ fontSize: '0.65rem', color: '#64748b', margin: 0, marginTop: '1px' }}>
              Context-Aware Behaviour Intelligence & Risk Scoring Engine
            </p>
          </div>
        </div>

        {/* Right controls */}
        <div className="flex items-center gap-3">

          {/* System activity indicator */}
          <div className="hidden md:flex items-center gap-1.5" style={{ padding: '6px 12px', borderRadius: '8px', background: 'rgba(13,23,41,0.8)', border: '1px solid rgba(56,97,158,0.18)' }}>
            <Activity style={{ width: 12, height: 12, color: '#475569' }} />
            <span style={{ fontSize: '0.65rem', color: '#475569', fontWeight: 500 }}>
              {videos.length} video{videos.length !== 1 ? 's' : ''} registered
            </span>
          </div>

          {/* Video selector */}
          {videos.length > 0 && (
            <div style={{ position: 'relative' }}>
              <div style={{
                background: 'rgba(13,23,41,0.9)',
                border: '1px solid rgba(56,97,158,0.25)',
                borderRadius: '9px',
                padding: '6px 10px 6px 12px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                minWidth: '220px',
              }}>
                <div style={{ flex: 1, overflow: 'hidden' }}>
                  <div style={{ fontSize: '0.6rem', color: '#475569', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1px' }}>
                    Active Feed
                  </div>
                  <select
                    value={selectedVideoId}
                    onChange={(e) => onSelectVideo(e.target.value)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      outline: 'none',
                      color: '#e2e8f0',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      width: '100%',
                      cursor: 'pointer',
                    }}
                  >
                    {videos.map((v) => (
                      <option key={v.video_id} value={v.video_id} style={{ background: '#0d1729' }}>
                        {v.filename.length > 28 ? v.filename.slice(0, 25) + '…' : v.filename} ({v.video_id})
                      </option>
                    ))}
                  </select>
                </div>
                <ChevronDown style={{ width: 14, height: 14, color: '#475569', flexShrink: 0 }} />
              </div>
            </div>
          )}

          {/* Backend status */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: '7px',
            padding: '7px 13px', borderRadius: '9px',
            background: backendHealthy ? 'rgba(16,185,129,0.08)' : 'rgba(245,158,11,0.08)',
            border: `1px solid ${backendHealthy ? 'rgba(16,185,129,0.25)' : 'rgba(245,158,11,0.25)'}`,
          }}>
            <div
              className={backendHealthy ? 'status-dot status-dot-healthy' : 'status-dot status-dot-error'}
            />
            {backendHealthy
              ? <Wifi style={{ width: 13, height: 13, color: '#10b981' }} />
              : <WifiOff style={{ width: 13, height: 13, color: '#f59e0b' }} />
            }
            <span style={{
              fontSize: '0.7rem', fontWeight: 600,
              color: backendHealthy ? '#10b981' : '#f59e0b',
            }}>
              {backendHealthy ? 'AI Engine Online' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
