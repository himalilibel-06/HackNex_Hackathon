import React from 'react';
import { Users, Eye, ShieldAlert, AlertTriangle, Gauge, TrendingUp, Activity } from 'lucide-react';
import { SummaryResponse } from '../types';

interface SummaryCardsProps {
  summary: SummaryResponse | null;
}

interface CardDef {
  title: string;
  value: string | number;
  sub: string;
  icon: React.ElementType;
  accentColor: string;
  borderColor: string;
  bgGradient: string;
  textColor: string;
  isEmpty: boolean;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ summary }) => {
  const isReady = summary !== null && summary.processing_time_sec !== undefined;

  const cards: CardDef[] = [
    {
      title: 'People Tracked',
      value: isReady ? summary!.total_tracks : '—',
      sub: isReady ? 'Unique ByteTrack IDs' : 'Awaiting analysis',
      icon: Users,
      accentColor: '#22d3ee',
      borderColor: 'rgba(34,211,238,0.2)',
      bgGradient: 'linear-gradient(135deg, rgba(34,211,238,0.06) 0%, transparent 70%)',
      textColor: '#22d3ee',
      isEmpty: !isReady,
    },
    {
      title: 'Total Events',
      value: isReady ? summary!.total_events : '—',
      sub: isReady ? 'Frame evaluations' : 'Awaiting analysis',
      icon: Activity,
      accentColor: '#6366f1',
      borderColor: 'rgba(99,102,241,0.2)',
      bgGradient: 'linear-gradient(135deg, rgba(99,102,241,0.06) 0%, transparent 70%)',
      textColor: '#818cf8',
      isEmpty: !isReady,
    },
    {
      title: 'Normal Events',
      value: isReady ? summary!.normal_events : '—',
      sub: isReady ? 'Low-risk activities' : 'Awaiting analysis',
      icon: Eye,
      accentColor: '#10b981',
      borderColor: 'rgba(16,185,129,0.2)',
      bgGradient: 'linear-gradient(135deg, rgba(16,185,129,0.06) 0%, transparent 70%)',
      textColor: '#34d399',
      isEmpty: !isReady,
    },
    {
      title: 'Unusual Events',
      value: isReady ? summary!.unusual_events : '—',
      sub: isReady ? 'Policy deviations' : 'Awaiting analysis',
      icon: AlertTriangle,
      accentColor: '#f59e0b',
      borderColor: isReady && summary!.unusual_events > 0 ? 'rgba(245,158,11,0.3)' : 'rgba(245,158,11,0.15)',
      bgGradient: 'linear-gradient(135deg, rgba(245,158,11,0.06) 0%, transparent 70%)',
      textColor: isReady && summary!.unusual_events > 0 ? '#fbbf24' : '#92400e',
      isEmpty: !isReady,
    },
    {
      title: 'Incidents Logged',
      value: isReady ? summary!.total_incidents_logged : '—',
      sub: isReady
        ? `${summary!.high_risk_incidents} high · ${summary!.critical_incidents} critical`
        : 'Awaiting analysis',
      icon: ShieldAlert,
      accentColor: '#ef4444',
      borderColor: isReady && summary!.total_incidents_logged > 0 ? 'rgba(239,68,68,0.35)' : 'rgba(239,68,68,0.15)',
      bgGradient: 'linear-gradient(135deg, rgba(239,68,68,0.07) 0%, transparent 70%)',
      textColor: isReady && summary!.total_incidents_logged > 0 ? '#f87171' : '#7f1d1d',
      isEmpty: !isReady,
    },
    {
      title: 'Avg Risk Score',
      value: isReady ? `${summary!.average_risk_score}` : 'N/A',
      sub: isReady ? 'Out of 100 · Interpretable' : 'No risk events',
      icon: Gauge,
      accentColor: isReady && summary!.average_risk_score > 60 ? '#ef4444' : '#f59e0b',
      borderColor: isReady && summary!.average_risk_score > 60
        ? 'rgba(239,68,68,0.3)' : 'rgba(245,158,11,0.2)',
      bgGradient: isReady && summary!.average_risk_score > 60
        ? 'linear-gradient(135deg, rgba(239,68,68,0.07) 0%, transparent 70%)'
        : 'linear-gradient(135deg, rgba(245,158,11,0.06) 0%, transparent 70%)',
      textColor: isReady && summary!.average_risk_score > 60 ? '#f87171' : '#fbbf24',
      isEmpty: !isReady,
    },
  ];

  return (
    <div
      className="stagger"
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(6, 1fr)',
        gap: '12px',
        marginBottom: '20px',
      }}
    >
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="metric-card animate-fade-in-up"
            style={{
              padding: '16px',
              background: `${card.bgGradient}, rgba(13,23,41,0.9)`,
              borderColor: card.borderColor,
              '--accent-color': card.accentColor,
            } as React.CSSProperties}
          >
            {/* Icon + label */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span className="metric-label">{card.title}</span>
              <div style={{
                width: 28, height: 28,
                borderRadius: '7px',
                background: `rgba(${hexToRgb(card.accentColor)}, 0.12)`,
                border: `1px solid rgba(${hexToRgb(card.accentColor)}, 0.25)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon style={{ width: 13, height: 13, color: card.accentColor }} />
              </div>
            </div>

            {/* Value */}
            <div
              className="metric-value"
              style={{ color: card.isEmpty ? '#334155' : '#f8fafc', fontSize: card.isEmpty ? '1.75rem' : '2rem' }}
            >
              {card.value}
            </div>

            {/* Sub */}
            <div className="metric-sub" style={{ marginTop: '4px' }}>
              {isReady && !card.isEmpty ? (
                <span style={{ color: card.textColor, fontSize: '0.68rem', fontWeight: 500 }}>
                  {card.sub}
                </span>
              ) : (
                <span style={{ color: '#334155', fontSize: '0.65rem' }}>{card.sub}</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Helper to convert hex to rgb triplet string
function hexToRgb(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return '255,255,255';
  return `${parseInt(result[1], 16)},${parseInt(result[2], 16)},${parseInt(result[3], 16)}`;
}
