import React from 'react';
import {
  PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer,
  Legend
} from 'recharts';
import { BarChart2 } from 'lucide-react';
import { SummaryResponse, TimelineEvent } from '../types';

interface RiskChartProps {
  summary: SummaryResponse | null;
  timeline: TimelineEvent[];
}

const SEVERITY_COLORS = {
  Normal:   '#10b981',
  Medium:   '#f59e0b',
  High:     '#f97316',
  Critical: '#ef4444',
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#0d1729', border: '1px solid rgba(56,97,158,0.3)',
        borderRadius: '9px', padding: '10px 14px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
        fontSize: '0.75rem',
      }}>
        {label && <div style={{ color: '#94a3b8', marginBottom: '6px', fontWeight: 600 }}>{label}</div>}
        {payload.map((p: any, i: number) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '7px', color: p.color || '#e2e8f0' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color }} />
            <span>{p.name}: <strong>{p.value}</strong></span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export const RiskChart: React.FC<RiskChartProps> = ({ summary, timeline }) => {
  const isReady = summary !== null && summary.processing_time_sec !== undefined;
  const hasData = isReady && summary!.total_events > 0;

  // Build pie data from REAL summary response
  const pieData = hasData ? [
    { name: 'Normal', value: summary!.normal_events, color: SEVERITY_COLORS.Normal },
    {
      name: 'Unusual',
      value: summary!.unusual_events - summary!.high_risk_incidents - summary!.critical_incidents,
      color: SEVERITY_COLORS.Medium,
    },
    { name: 'High Risk', value: summary!.high_risk_incidents, color: SEVERITY_COLORS.High },
    { name: 'Critical',  value: summary!.critical_incidents,  color: SEVERITY_COLORS.Critical },
  ].filter(d => d.value > 0) : [];

  // Build timeline bar data: bucket events per second from REAL timeline data
  const barData = React.useMemo(() => {
    if (!timeline || timeline.length === 0) return [];
    const maxT = Math.max(...timeline.map(e => e.timestamp));
    const bucketSec = Math.max(1, Math.floor(maxT / 12)); // ~12 bars max
    const buckets: Record<number, { normal: number; unusual: number }> = {};
    timeline.forEach(e => {
      const bucket = Math.floor(e.timestamp / bucketSec) * bucketSec;
      if (!buckets[bucket]) buckets[bucket] = { normal: 0, unusual: 0 };
      if (e.status === 'potentially_unusual') buckets[bucket].unusual++;
      else buckets[bucket].normal++;
    });
    return Object.entries(buckets).map(([t, v]) => ({
      time: `${t}s`,
      Normal: v.normal,
      Unusual: v.unusual,
    })).sort((a, b) => parseFloat(a.time) - parseFloat(b.time));
  }, [timeline]);

  return (
    <div className="glass-card mb-5" style={{ padding: '18px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
          <div className="section-icon" style={{
            background: 'rgba(245,158,11,0.1)',
            borderColor: 'rgba(245,158,11,0.25)',
          }}>
            <BarChart2 style={{ width: 15, height: 15, color: '#fbbf24' }} />
          </div>
          <div>
            <div className="section-title">Risk Distribution & Activity</div>
            <div className="section-subtitle">Real-time computed from AI pipeline output</div>
          </div>
        </div>
        {hasData && (
          <span style={{
            fontSize: '0.65rem', fontWeight: 600, color: '#fbbf24',
            background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)',
            padding: '3px 9px', borderRadius: '6px',
          }}>
            {summary!.total_events} total events
          </span>
        )}
      </div>

      {!hasData ? (
        <div className="empty-state">
          <div className="empty-icon">
            <BarChart2 style={{ width: 22, height: 22, color: '#334155' }} />
          </div>
          <div className="empty-title">Insufficient event data</div>
          <div className="empty-subtitle">
            Risk visualization will appear when behaviour events are detected in the processed video.
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.8fr', gap: '16px', alignItems: 'center' }}>

          {/* Donut chart — severity breakdown */}
          <div>
            <div style={{ fontSize: '0.65rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px', textAlign: 'center' }}>
              Event Severity
            </div>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={46}
                  outerRadius={72}
                  paddingAngle={2}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} opacity={0.9} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            {/* Legend */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '4px' }}>
              {pieData.map((d, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <div style={{ width: 8, height: 8, borderRadius: '2px', background: d.color }} />
                    <span style={{ fontSize: '0.65rem', color: '#64748b' }}>{d.name}</span>
                  </div>
                  <span style={{ fontSize: '0.68rem', fontWeight: 700, color: d.color }}>{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Bar chart — timeline activity */}
          <div>
            <div style={{ fontSize: '0.65rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px', textAlign: 'center' }}>
              Activity Over Time
            </div>
            {barData.length > 0 ? (
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={barData} barGap={2} barSize={12}>
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 9, fill: '#475569' }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 9, fill: '#475569' }}
                    axisLine={false}
                    tickLine={false}
                    width={24}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="Normal" fill={SEVERITY_COLORS.Normal} radius={[3,3,0,0]} opacity={0.85} />
                  <Bar dataKey="Unusual" fill={SEVERITY_COLORS.High} radius={[3,3,0,0]} opacity={0.85} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.72rem', color: '#475569' }}>
                No timeline data available
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
