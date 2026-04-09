export default function AnalysisDashboard({ data }) {
  if (!data?.analysis) return null;

  const { acne_severity, lesion_count, lesion_count_bucket, zone_health, hyperpigmentation } = data.analysis;

  const severityGradients = {
    Clear: 'var(--gradient-severity-clear)',
    Mild: 'var(--gradient-severity-mild)',
    Moderate: 'var(--gradient-severity-moderate)',
    Severe: 'var(--gradient-severity-severe)',
  };

  const severityScores = {
    Clear: 0,
    Mild: 25,
    Moderate: 60,
    Severe: 90,
  };

  return (
    <div className="dashboard-panel glass-card">
      <h3 className="section-title">
        <span className="icon">📊</span>
        Analysis Results
      </h3>

      <div className="metric-cards">
        {/* Acne Severity Card */}
        <div className={`metric-card severity ${acne_severity.grade.toLowerCase()}`}>
          <div className="metric-label">Acne Severity</div>
          <div className="metric-value" style={{
            background: severityGradients[acne_severity.grade] || 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}>
            {acne_severity.grade}
          </div>
          <div className="severity-gauge">
            <div
              className="severity-gauge-fill"
              style={{
                width: `${acne_severity.score || severityScores[acne_severity.grade] || 0}%`,
                background: severityGradients[acne_severity.grade] || 'var(--gradient-primary)',
              }}
            />
          </div>
          <div className="severity-scale">
            <span>Clear</span>
            <span>Mild</span>
            <span>Moderate</span>
            <span>Severe</span>
          </div>
        </div>

        {/* Lesion Count Card */}
        <div className="metric-card lesions">
          <div className="metric-label">Lesion Count</div>
          <div className="metric-value">{lesion_count}</div>
          <div className="metric-sub">Bucket: {lesion_count_bucket}</div>
          {acne_severity.inflammatory_count > 0 && (
            <div className="metric-sub" style={{ color: '#ff4757' }}>
              🔥 {acne_severity.inflammatory_count} inflammatory
            </div>
          )}
          {acne_severity.comedonal_count > 0 && (
            <div className="metric-sub" style={{ color: '#00ff00' }}>
              ⚪ {acne_severity.comedonal_count} comedonal
            </div>
          )}
        </div>

        {/* Hyperpigmentation Card */}
        <div className="metric-card pigmentation">
          <div className="metric-label">Hyperpigmentation</div>
          <div className="metric-value">{hyperpigmentation.coverage_pct}%</div>
          <div className="metric-sub">Coverage: {hyperpigmentation.coverage_bucket}</div>
          <div className="metric-sub">{hyperpigmentation.region_count} region(s) detected</div>
        </div>

        {/* Zones Overview Card */}
        <div className="metric-card zones">
          <div className="metric-label">Zones Affected</div>
          <div className="metric-value">
            {Object.values(zone_health).filter(z => z.affected).length}
            <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>
              {' '}/ {Object.keys(zone_health).length}
            </span>
          </div>
          <div className="metric-sub">
            {Object.values(zone_health).filter(z => z.affected).length === 0
              ? 'All zones are clear'
              : 'Tap zones below for details'}
          </div>
        </div>
      </div>

      {/* Zone Health Details */}
      <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '12px', color: 'var(--text-secondary)' }}>
        🗺️ Facial Zone Health
      </h4>
      <div className="zone-list">
        {Object.entries(zone_health).map(([name, zone]) => (
          <div className="zone-item" key={name}>
            <span className="zone-name">{name.replace('_', ' ')}</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {zone.lesion_count} lesion(s)
              </span>
              <span className={`zone-badge ${zone.severity}`}>
                {zone.severity}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
