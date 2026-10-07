import React from 'react';
import { Clock, MapPin, Activity, ShieldAlert, User } from 'lucide-react';
import { TimelineEvent } from '../types';

interface TimelineViewProps {
  timeline: TimelineEvent[];
}

function getSeverityStyle(status: string) {
  if (status === 'potentially_unusual') {
    return {
      dotBg: '#f97316',
      dotBorder: '#f97316',
      dotShadow: 'rgba(249,115,22,0.5)',
      cardBg: 'rgba(249,115,22,0.06)',
      cardBorder: 'rgba(249,115,22,0.2)',
      badgeClass: 'badge badge-high',
      icon: ShieldAlert,
      iconColor: '#f97316',
    };
  }
  return {
    dotBg: 'transparent',
    dotBorder: '#22d3ee',
    dotShadow: 'rgba(34,211,238,0.3)',
    cardBg: 'rgba(13,23,41,0.5)',
    cardBorder: 'rgba(56,97,158,0.15)',
    badgeClass: 'badge badge-low',
    icon: Activity,
    iconColor: '#22d3ee',
  };
}

export const TimelineView: React.FC<TimelineViewProps> = ({ timeline }) => {
  // Show max 40 events to avoid overwhelming the UI
  const displayTimeline = timeline.slice(0, 40);

  return (
    <div className="glass-card mb-5" style={{ padding: '18px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
          <div className="section-icon" style={{
            background: 'rgba(99,102,241,0.1)',
            borderColor: 'rgba(99,102,241,0.25)',
          }}>
            <Clock style={{ width: 15, height: 15, color: '#818cf8' }} />
          </div>
          <div>
            <div className="section-title">Person Activity Timeline</div>
            <div className="section-subtitle">Chronological behaviour events from AI analysis</div>
          </div>
        </div>
        {timeline.length > 0 && (
          <span style={{
            fontSize: '0.65rem', fontWeight: 600, color: '#475569',
            background: 'rgba(13,23,41,0.7)', border: '1px solid rgba(56,97,158,0.18)',
            padding: '3px 9px', borderRadius: '6px',
          }}>
            {timeline.length} event{timeline.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Content */}
      {timeline.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <Clock style={{ width: 22, height: 22, color: '#334155' }} />
          </div>
          <div className="empty-title">No behaviour events detected</div>
          <div className="empty-subtitle">
            Behaviour insights will appear when the AI identifies activity in the uploaded CCTV footage.
          </div>
        </div>
      ) : (
        <div style={{ maxHeight: 420, overflowY: 'auto', paddingRight: '4px' }}>
          {displayTimeline.map((item, idx) => {
            const style = getSeverityStyle(item.status);
            const Icon = style.icon;
            return (
              <div key={idx} className="timeline-item animate-fade-in-up" style={{ animationDelay: `${Math.min(idx * 30, 300)}ms` }}>
                {/* Dot */}
                <div
                  className="timeline-dot"
                  style={{
                    background: style.dotBg,
                    borderColor: style.dotBorder,
                    boxShadow: `0 0 6px ${style.dotShadow}`,
                    width: 14, height: 14,
                  }}
                >
                  <div style={{
                    width: 5, height: 5, borderRadius: '50%',
                    background: style.dotBorder,
                  }} />
                </div>

                {/* Card */}
                <div style={{
                  background: style.cardBg,
                  border: `1px solid ${style.cardBorder}`,
                  borderRadius: '10px',
                  padding: '10px 13px',
                  transition: 'all 0.2s',
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                    {/* Left */}
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                        <Icon style={{ width: 12, height: 12, color: style.iconColor, flexShrink: 0 }} />
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e2e8f0' }}>
                          {item.description}
                        </span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '3px', fontSize: '0.65rem', color: '#64748b' }}>
                          <MapPin style={{ width: 10, height: 10 }} />
                          {item.zone}
                        </span>
                        <span style={{ fontSize: '0.65rem', color: '#64748b' }}>
                          {item.behaviour}
                        </span>
                        <span style={{
                          fontSize: '0.6rem', fontWeight: 600,
                          background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.25)',
                          color: '#a5b4fc', padding: '1px 6px', borderRadius: '4px',
                        }}>
                          {item.event_type.replace('_', ' ')}
                        </span>
                      </div>
                    </div>

                    {/* Right: time + severity */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px', flexShrink: 0 }}>
                      <span className="mono" style={{
                        fontSize: '0.68rem', fontWeight: 600, color: '#94a3b8',
                        background: 'rgba(13,23,41,0.8)', border: '1px solid rgba(56,97,158,0.18)',
                        padding: '2px 8px', borderRadius: '5px',
                      }}>
                        {item.cctv_time} · {item.timestamp.toFixed(1)}s
                      </span>
                      {item.status === 'potentially_unusual' && (
                        <span className="badge badge-high" style={{ fontSize: '0.58rem' }}>UNUSUAL</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
          {timeline.length > 40 && (
            <div style={{ textAlign: 'center', padding: '10px', fontSize: '0.7rem', color: '#475569' }}>
              Showing 40 of {timeline.length} events
            </div>
          )}
        </div>
      )}
    </div>
  );
};
