import { useState } from 'react';

const STAGE_ICONS = {
  now: '📍',
  short_term: '📈',
  long_term: '🌟',
};

const STAGE_CLASSES = {
  now: 'now',
  short_term: 'short',
  long_term: 'long',
};

export default function ProgressTracker({ progress }) {
  const [activeStage, setActiveStage] = useState('now');

  if (!progress) return null;

  const stages = [
    { key: 'now', data: progress.now },
    { key: 'short_term', data: progress.short_term },
    { key: 'long_term', data: progress.long_term },
  ];

  const activeData = stages.find(s => s.key === activeStage)?.data;

  return (
    <div className="progress-section">
      <h3 className="section-title">
        <span className="icon">🔄</span>
        Treatment Progress Journey
      </h3>

      <div className="progress-timeline">
        {stages.map((stage) => (
          <div
            key={stage.key}
            className={`progress-stage ${STAGE_CLASSES[stage.key]} ${activeStage === stage.key ? 'active' : ''}`}
            onClick={() => setActiveStage(stage.key)}
          >
            <div className="stage-indicator">
              {STAGE_ICONS[stage.key]}
            </div>
            <div className="stage-label">{stage.data.label}</div>
            <div className="stage-timeframe">{stage.data.timeframe}</div>
          </div>
        ))}
      </div>

      {activeData && (
        <div className="progress-detail glass-card" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '16px',
          }}>
            <div>
              <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 700 }}>
                {activeData.label} — {activeData.subtitle}
              </h4>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Timeframe: {activeData.timeframe}
              </span>
            </div>
            {activeData.severity && (
              <span className={`zone-badge ${activeData.severity.toLowerCase()}`} style={{ fontSize: '0.8rem', padding: '4px 14px' }}>
                {activeData.severity}
              </span>
            )}
          </div>

          {/* Metrics */}
          {activeData.metrics && (
            <div style={{
              display: 'flex',
              gap: '16px',
              marginBottom: '16px',
              flexWrap: 'wrap',
            }}>
              <div style={{
                padding: '8px 16px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-glass)',
                border: '1px solid var(--border-subtle)',
                fontSize: '0.8rem',
              }}>
                <span style={{ color: 'var(--text-muted)' }}>Grade: </span>
                <strong>{activeData.metrics.acne_grade}</strong>
              </div>
              <div style={{
                padding: '8px 16px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-glass)',
                border: '1px solid var(--border-subtle)',
                fontSize: '0.8rem',
              }}>
                <span style={{ color: 'var(--text-muted)' }}>Lesions: </span>
                <strong>{activeData.metrics.lesion_count}</strong>
              </div>
              <div style={{
                padding: '8px 16px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-glass)',
                border: '1px solid var(--border-subtle)',
                fontSize: '0.8rem',
              }}>
                <span style={{ color: 'var(--text-muted)' }}>Pigmentation: </span>
                <strong>{activeData.metrics.pigmentation_pct}%</strong>
              </div>
            </div>
          )}

          {/* Conditions */}
          <ul className="progress-conditions">
            {activeData.conditions.map((cond, i) => (
              <li key={i}>{cond}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
