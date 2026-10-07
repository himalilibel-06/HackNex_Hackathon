import React from 'react';
import { ShieldAlert, ExternalLink, AlertTriangle, Clock, MapPin, Zap } from 'lucide-react';
import { IncidentResponse } from '../types';

interface IncidentTableProps {
  incidents: IncidentResponse[];
  onSelectIncident: (incident: IncidentResponse) => void;
}

function getRiskStyle(level: string) {
  switch (level) {
    case 'CRITICAL': return { badgeClass: 'badge badge-critical', borderColor: 'rgba(239,68,68,0.25)', bg: 'rgba(239,68,68,0.04)', dotColor: '#ef4444' };
    case 'HIGH':     return { badgeClass: 'badge badge-high',     borderColor: 'rgba(249,115,22,0.22)', bg: 'rgba(249,115,22,0.04)', dotColor: '#f97316' };
    case 'MEDIUM':   return { badgeClass: 'badge badge-medium',   borderColor: 'rgba(245,158,11,0.2)',  bg: 'rgba(245,158,11,0.03)', dotColor: '#f59e0b' };
    default:         return { badgeClass: 'badge badge-low',      borderColor: 'rgba(16,185,129,0.2)',  bg: 'rgba(16,185,129,0.03)', dotColor: '#10b981' };
  }
}

export const IncidentTable: React.FC<IncidentTableProps> = ({ incidents, onSelectIncident }) => {
  return (
    <div className="glass-card mb-5" style={{ padding: '18px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
          <div className="section-icon" style={{
            background: 'rgba(239,68,68,0.1)',
            borderColor: 'rgba(239,68,68,0.25)',
          }}>
            <ShieldAlert style={{ width: 15, height: 15, color: '#f87171' }} />
          </div>
          <div>
            <div className="section-title">Safety Incidents</div>
            <div className="section-subtitle">High & critical risk events requiring attention</div>
          </div>
        </div>
        {incidents.length > 0 && (
          <span style={{
            fontSize: '0.65rem', fontWeight: 700, color: '#f87171',
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
            padding: '3px 9px', borderRadius: '6px',
          }}>
            {incidents.length} logged
          </span>
        )}
      </div>

      {incidents.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon" style={{ background: 'rgba(16,185,129,0.08)', borderColor: 'rgba(16,185,129,0.2)' }}>
            <ShieldAlert style={{ width: 22, height: 22, color: '#10b981' }} />
          </div>
          <div className="empty-title" style={{ color: '#10b981' }}>No high-risk incidents detected</div>
          <div className="empty-subtitle">
            All analysed activity is currently within configured safety thresholds.
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: 400, overflowY: 'auto', paddingRight: '4px' }}>
          {incidents.map((inc) => {
            const riskStyle = getRiskStyle(inc.risk_level);
            return (
              <div
                key={inc.incident_id}
                className="animate-fade-in"
                style={{
                  background: riskStyle.bg,
                  border: `1px solid ${riskStyle.borderColor}`,
                  borderRadius: '10px',
                  padding: '12px 14px',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = riskStyle.bg.replace('0.04', '0.08').replace('0.03', '0.06'))}
                onMouseLeave={e => (e.currentTarget.style.background = riskStyle.bg)}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px' }}>
                  {/* Left content */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    {/* Top row: incident ID + badges */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '7px', marginBottom: '7px', flexWrap: 'wrap' }}>
                      <span className="mono" style={{
                        fontSize: '0.7rem', fontWeight: 700, color: '#94a3b8',
                      }}>
                        {inc.incident_id}
                      </span>
                      <span className="track-id-badge">{inc.track_id}</span>
                      <span className={riskStyle.badgeClass}>{inc.risk_level}</span>
                      <span style={{
                        fontSize: '0.68rem', fontWeight: 700, color: riskStyle.dotColor,
                      }}>
                        {inc.risk_score}/100
                      </span>
                    </div>

                    {/* Meta row */}
                    <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                      <MetaItem icon={MapPin} value={inc.zone} />
                      <MetaItem icon={Zap} value={inc.behaviour} />
                      <MetaItem icon={Clock} value={`${inc.cctv_time} (${inc.start_time.toFixed(1)}s)`} />
                    </div>

                    {/* Explanation snippet */}
                    {inc.explanation && (
                      <p style={{
                        fontSize: '0.68rem', color: '#64748b', marginTop: '7px',
                        lineHeight: 1.5,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      } as React.CSSProperties}>
                        {inc.explanation}
                      </p>
                    )}
                  </div>

                  {/* Right: view details button */}
                  <button
                    onClick={() => onSelectIncident(inc)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '5px',
                      fontSize: '0.68rem', fontWeight: 600,
                      background: 'rgba(13,23,41,0.8)',
                      border: '1px solid rgba(56,97,158,0.25)',
                      color: '#94a3b8', padding: '6px 12px',
                      borderRadius: '7px', cursor: 'pointer',
                      transition: 'all 0.2s', flexShrink: 0,
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.background = 'rgba(22,32,53,0.9)';
                      e.currentTarget.style.color = '#e2e8f0';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.background = 'rgba(13,23,41,0.8)';
                      e.currentTarget.style.color = '#94a3b8';
                    }}
                  >
                    Details
                    <ExternalLink style={{ width: 11, height: 11 }} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

const MetaItem: React.FC<{ icon: React.ElementType; value: string }> = ({ icon: Icon, value }) => (
  <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.66rem', color: '#64748b' }}>
    <Icon style={{ width: 10, height: 10 }} />
    {value}
  </span>
);
