export default function Recommendations({ recommendations }) {
  if (!recommendations) return null;

  return (
    <div className="recommendations-section">
      <h3 className="section-title">
        <span className="icon">💊</span>
        AI Skincare Recommendations
      </h3>

      {/* Summary Banner */}
      <div className="summary-banner">
        {recommendations.summary}
      </div>

      {/* AM/PM Routines */}
      <div className="recommendations-grid">
        {/* Morning Routine */}
        <div className="routine-card glass-card">
          <div className="routine-header">
            <span className="routine-icon">☀️</span>
            <span className="routine-title">Morning Routine (AM)</span>
          </div>
          <div className="routine-steps">
            {recommendations.am_routine?.map((step) => (
              <div className="routine-step" key={step.step}>
                <div className="step-number">{step.step}</div>
                <div className="step-content">
                  <h4>{step.action}</h4>
                  <p>{step.detail}</p>
                  {step.ingredients && (
                    <div className="step-ingredients">
                      {step.ingredients.map((ing, i) => (
                        <span className="ingredient-tag" key={i}>{ing}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Evening Routine */}
        <div className="routine-card glass-card">
          <div className="routine-header">
            <span className="routine-icon">🌙</span>
            <span className="routine-title">Evening Routine (PM)</span>
          </div>
          <div className="routine-steps">
            {recommendations.pm_routine?.map((step) => (
              <div className="routine-step" key={step.step}>
                <div className="step-number">{step.step}</div>
                <div className="step-content">
                  <h4>{step.action}</h4>
                  <p>{step.detail}</p>
                  {step.ingredients && (
                    <div className="step-ingredients">
                      {step.ingredients.map((ing, i) => (
                        <span className="ingredient-tag" key={i}>{ing}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Key Ingredients */}
      {recommendations.key_ingredients?.length > 0 && (
        <div className="ingredients-section">
          <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>
            🧪 Key Ingredients to Look For
          </h4>
          <div className="ingredients-grid">
            {recommendations.key_ingredients.map((ing, i) => (
              <div className="ingredient-card" key={i}>
                <h4>{ing.name}</h4>
                <p>{ing.purpose}</p>
                <span className={`priority-badge ${ing.priority}`}>
                  {ing.priority}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Lifestyle Tips */}
      {recommendations.lifestyle?.length > 0 && (
        <div className="lifestyle-section glass-card">
          <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>
            Lifestyle Recommendations
          </h4>
          <div className="lifestyle-tips">
            {recommendations.lifestyle.map((tip, i) => (
              <div className="lifestyle-tip" key={i}>{tip}</div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings */}
      {recommendations.warnings?.length > 0 && (
        <div className="warnings-section">
          {recommendations.warnings.map((warn, i) => (
            <div className="warning-item" key={i}>{warn}</div>
          ))}
        </div>
      )}
    </div>
  );
}
