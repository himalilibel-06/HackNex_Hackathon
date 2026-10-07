import React from 'react';
import { Users, MapPin, Clock, Activity } from 'lucide-react';
import { TrackResponse } from '../types';

interface TrackingTableProps {
  tracks: TrackResponse[];
  selectedTrackId?: string;
  onSelectTrackId: (trackId: string) => void;
}

export const TrackingTable: React.FC<TrackingTableProps> = ({
  tracks,
  selectedTrackId,
  onSelectTrackId
}) => {
  return (
    <div className="glass-card mb-5" style={{ padding: '18px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
          <div className="section-icon" style={{
            background: 'rgba(34,211,238,0.1)',
            borderColor: 'rgba(34,211,238,0.25)',
          }}>
            <Users style={{ width: 15, height: 15, color: '#22d3ee' }} />
          </div>
          <div>
            <div className="section-title">Tracked Workers Directory</div>
            <div className="section-subtitle">Per-person ByteTrack persistent ID records</div>
          </div>
        </div>
        {tracks.length > 0 && (
          <span style={{
            fontSize: '0.65rem', fontWeight: 600, color: '#22d3ee',
            background: 'rgba(34,211,238,0.08)', border: '1px solid rgba(34,211,238,0.2)',
            padding: '3px 9px', borderRadius: '6px',
          }}>
            {tracks.length} person{tracks.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {tracks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <Users style={{ width: 22, height: 22, color: '#334155' }} />
          </div>
          <div className="empty-title">No people detected</div>
          <div className="empty-subtitle">
            Run SafeSight AI on a CCTV video to begin tracking workers and generating behaviour records.
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: 320, overflowY: 'auto', paddingRight: '4px' }}>
          {tracks.map((t) => {
            const isSelected = selectedTrackId === t.track_id;
            const duration = (t.last_seen_sec - t.first_seen_sec).toFixed(1);

            return (
              <div
                key={t.track_id}
                onClick={() => onSelectTrackId(t.track_id)}
                className="animate-fade-in"
                style={{
                  background: isSelected
                    ? 'rgba(34,211,238,0.07)'
                    : 'rgba(13,23,41,0.6)',
                  border: `1px solid ${isSelected ? 'rgba(34,211,238,0.35)' : 'rgba(56,97,158,0.15)'}`,
                  borderRadius: '10px',
                  padding: '12px 14px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  boxShadow: isSelected ? '0 0 16px rgba(34,211,238,0.08)' : 'none',
                }}
                onMouseEnter={e => {
                  if (!isSelected) {
                    e.currentTarget.style.background = 'rgba(22,32,53,0.8)';
                    e.currentTarget.style.borderColor = 'rgba(56,97,158,0.3)';
                  }
                }}
                onMouseLeave={e => {
                  if (!isSelected) {
                    e.currentTarget.style.background = 'rgba(13,23,41,0.6)';
                    e.currentTarget.style.borderColor = 'rgba(56,97,158,0.15)';
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px' }}>
                  {/* Left: ID + stats */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '7px' }}>
                      <span className="track-id-badge">{t.track_id}</span>
                      {isSelected && (
                        <span style={{
                          fontSize: '0.58rem', fontWeight: 700, color: '#22d3ee',
                          letterSpacing: '0.08em', textTransform: 'uppercase',
                        }}>
                          ↓ Filtering timeline
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
                      <StatItem icon={Clock} label="Duration" value={`${duration}s`} color="#64748b" />
                      <StatItem icon={Activity} label="Frames" value={`${t.active_frames}`} color="#64748b" />
                      <StatItem icon={MapPin} label="Zones" value={`${t.zones_visited.length}`} color="#64748b" />
                    </div>

                    {/* Behaviours */}
                    {t.behaviours_observed.length > 0 && (
                      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '8px' }}>
                        {t.behaviours_observed.map((b, i) => (
                          <span key={i} style={{
                            fontSize: '0.62rem', fontWeight: 500,
                            background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
                            color: '#a5b4fc', padding: '2px 7px', borderRadius: '4px',
                          }}>
                            {b}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Zone chips */}
                    {t.zones_visited.length > 0 && (
                      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '5px' }}>
                        {t.zones_visited.map((z, i) => (
                          <span key={i} className="zone-chip">{z}</span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Right: Time range + filter button */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px', flexShrink: 0 }}>
                    <div style={{ textAlign: 'right' }}>
                      <div className="mono" style={{ fontSize: '0.65rem', color: '#475569' }}>
                        {t.first_seen_sec.toFixed(1)}s → {t.last_seen_sec.toFixed(1)}s
                      </div>
                    </div>
                    <button
                      style={{
                        fontSize: '0.65rem', fontWeight: 600, padding: '4px 10px',
                        borderRadius: '6px', border: '1px solid',
                        cursor: 'pointer', transition: 'all 0.2s',
                        background: isSelected ? 'rgba(34,211,238,0.15)' : 'rgba(22,32,53,0.8)',
                        borderColor: isSelected ? 'rgba(34,211,238,0.4)' : 'rgba(56,97,158,0.25)',
                        color: isSelected ? '#22d3ee' : '#64748b',
                      }}
                      onClick={(e) => { e.stopPropagation(); onSelectTrackId(t.track_id); }}
                    >
                      {isSelected ? 'Clear Filter' : 'Filter Timeline'}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

const StatItem: React.FC<{ icon: React.ElementType; label: string; value: string; color: string }> = ({ icon: Icon, label, value, color }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
    <Icon style={{ width: 11, height: 11, color }} />
    <span style={{ fontSize: '0.65rem', color: '#475569' }}>{label}:</span>
    <span style={{ fontSize: '0.68rem', fontWeight: 600, color: '#94a3b8' }}>{value}</span>
  </div>
);
