import React from 'react';
import { X, ShieldAlert, FileText, Camera, AlertOctagon, MapPin, Clock, Zap, Target } from 'lucide-react';
import { IncidentResponse } from '../types';
import { api } from '../services/api';

interface IncidentDetailModalProps {
  incident: IncidentResponse | null;
  videoId: string;
  onClose: () => void;
}

function getRiskColor(level: string) {
  switch (level) {
    case 'CRITICAL': return { bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.4)', text: '#f87171', solid: '#ef4444' };
    case 'HIGH':     return { bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.35)', text: '#fb923c', solid: '#f97316' };
    case 'MEDIUM':   return { bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.3)', text: '#fbbf24', solid: '#f59e0b' };
    default:         return { bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.25)', text: '#34d399', solid: '#10b981' };
  }
}

export const IncidentDetailModal: React.FC<IncidentDetailModalProps> = ({ incident, videoId, onClose }) => {
  if (!incident) return null;

  const htmlReportUrl = api.getReportHtmlUrl(videoId, incident.incident_id);
  const riskColor = getRiskColor(incident.risk_level);

  return (
    <div
      className="animate-fade-in"
      style={{
        position: 'fixed', inset: 0, zIndex: 50,
        background: 'rgba(6,12,26,0.85)',
        backdropFilter: 'blur(12px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '20px',
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="animate-fade-in-up"
        style={{
          width: '100%', maxWidth: '700px',
          maxHeight: '90vh', overflowY: 'auto',
          background: '#0d1729',
          border: '1px solid rgba(56,97,158,0.25)',
          borderRadius: '16px',
          boxShadow: '0 24px 80px rgba(0,0,0,0.7)',
          position: 'relative',
        }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute', top: '16px', right: '16px',
            background: 'rgba(22,32,53,0.9)', border: '1px solid rgba(56,97,158,0.2)',
            borderRadius: '8px', padding: '6px', cursor: 'pointer',
            color: '#64748b', transition: 'all 0.2s',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
          onMouseEnter={e => { e.currentTarget.style.color = '#e2e8f0'; e.currentTarget.style.background = 'rgba(30,44,70,0.9)'; }}
          onMouseLeave={e => { e.currentTarget.style.color = '#64748b'; e.currentTarget.style.background = 'rgba(22,32,53,0.9)'; }}
        >
          <X style={{ width: 16, height: 16 }} />
        </button>

        {/* Severity header band */}
        <div style={{
          background: riskColor.bg,
          borderBottom: `1px solid ${riskColor.border}`,
          borderRadius: '16px 16px 0 0',
          padding: '20px 24px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              background: riskColor.bg, border: `1px solid ${riskColor.border}`,
              borderRadius: '10px', padding: '10px',
            }}>
              <ShieldAlert style={{ width: 22, height: 22, color: riskColor.text }} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#f8fafc', margin: 0, letterSpacing: '-0.02em' }}>
                  {incident.incident_id}
                </h2>
                <span style={{
                  fontSize: '0.65rem', fontWeight: 800, letterSpacing: '0.1em',
                  textTransform: 'uppercase', color: riskColor.text,
                  background: riskColor.bg, border: `1px solid ${riskColor.border}`,
                  padding: '3px 10px', borderRadius: '6px',
                }}>
                  {incident.risk_level}
                </span>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: riskColor.text }}>
                  {incident.risk_score}/100
                </span>
              </div>
              <p style={{ fontSize: '0.72rem', color: '#64748b', margin: 0 }}>
                {incident.track_id} · {incident.zone} · {incident.cctv_time}
              </p>
            </div>
          </div>
        </div>

        {/* Body */}
        <div style={{ padding: '20px 24px' }}>

          {/* Meta grid */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '10px', marginBottom: '20px',
          }}>
            {[
              { icon: Clock, label: 'CCTV Time', value: incident.cctv_time },
              { icon: Target, label: 'Timestamp', value: `${incident.start_time.toFixed(1)}s – ${incident.end_time.toFixed(1)}s` },
              { icon: Zap, label: 'Behaviour', value: incident.behaviour },
              { icon: MapPin, label: 'Zone', value: incident.zone },
            ].map((item, i) => {
              const Icon = item.icon;
              return (
                <div key={i} style={{
                  background: 'rgba(13,23,41,0.7)', border: '1px solid rgba(56,97,158,0.15)',
                  borderRadius: '9px', padding: '10px 12px',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '4px' }}>
                    <Icon style={{ width: 11, height: 11, color: '#475569' }} />
                    <span style={{ fontSize: '0.6rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#475569' }}>
                      {item.label}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#e2e8f0' }}>{item.value}</div>
                </div>
              );
            })}
          </div>

          {/* Explanation */}
          <div style={{ marginBottom: '18px' }}>
            <h4 style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#475569', marginBottom: '8px' }}>
              Explainable Alert
            </h4>
            <div style={{
              background: 'rgba(34,211,238,0.05)', borderLeft: '3px solid rgba(34,211,238,0.5)',
              borderRadius: '0 9px 9px 0', padding: '12px 16px',
              fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.6,
              border: '1px solid rgba(34,211,238,0.12)',
            }}>
              {incident.explanation}
            </div>
          </div>

          {/* Risk reasons */}
          {incident.risk_reasons && incident.risk_reasons.length > 0 && (
            <div style={{ marginBottom: '18px' }}>
              <h4 style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#475569', marginBottom: '8px' }}>
                Risk Factors
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {incident.risk_reasons.map((reason, idx) => (
                  <div key={idx} style={{
                    display: 'flex', alignItems: 'flex-start', gap: '8px',
                    background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)',
                    borderRadius: '8px', padding: '8px 12px',
                    fontSize: '0.75rem', color: '#94a3b8',
                  }}>
                    <AlertOctagon style={{ width: 13, height: 13, color: '#f59e0b', marginTop: 1, flexShrink: 0 }} />
                    {reason}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Evidence snapshots */}
          {incident.evidence && incident.evidence.length > 0 && (
            <div style={{ marginBottom: '18px' }}>
              <h4 style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#475569', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Camera style={{ width: 12, height: 12 }} />
                CCTV Evidence Snapshots
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                {incident.evidence.map((evPath, idx) => (
                  <div key={idx} style={{
                    background: '#020408', border: '1px solid rgba(56,97,158,0.2)',
                    borderRadius: '10px', overflow: 'hidden',
                  }}>
                    <img
                      src={api.getEvidenceUrl(videoId, evPath)}
                      alt={`Evidence ${idx + 1}`}
                      style={{ width: '100%', height: 'auto', display: 'block', objectFit: 'cover' }}
                    />
                    <div style={{ padding: '6px 10px', fontSize: '0.62rem', color: '#475569' }}>
                      Snapshot #{idx + 1} — {evPath.split(/[/\\]/).pop()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            paddingTop: '16px', borderTop: '1px solid rgba(56,97,158,0.15)',
          }}>
            <a
              href={htmlReportUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
            >
              <FileText style={{ width: 14, height: 14 }} />
              Open HTML Report
            </a>
            <button className="btn-ghost" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
