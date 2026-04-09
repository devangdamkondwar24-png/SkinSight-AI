import { useState, useCallback } from 'react';
import ImageUpload from './components/ImageUpload';
import CanvasOverlay from './components/CanvasOverlay';
import AnalysisDashboard from './components/AnalysisDashboard';
import ProgressTracker from './components/ProgressTracker';
import Recommendations from './components/Recommendations';
import './App.css';

const API_URL = 'http://localhost:8000';

const LOADING_STEPS = [
  'Detecting facial landmarks...',
  'Analyzing skin texture & lesions...',
  'Mapping facial zones...',
  'Detecting hyperpigmentation...',
  'Generating heatmap overlay...',
  'Building recommendations...',
  'Projecting treatment progress...',
];

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loadingStep, setLoadingStep] = useState(0);

  const handleAnalyze = useCallback(async (file) => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    setLoadingStep(0);

    // Animate loading steps
    const interval = setInterval(() => {
      setLoadingStep((prev) => Math.min(prev + 1, LOADING_STEPS.length - 1));
    }, 600);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Analysis failed');
      }

      if (!data.success) {
        throw new Error(data.error || 'No face detected');
      }

      setResults(data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to connect to the analysis server');
    } finally {
      clearInterval(interval);
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="app">
      <div className="app-bg" />

      {/* Header */}
      <header className="header">
        <div className="logo">
          <div className="logo-icon">🧬</div>
          <div className="logo-text">
            <h1>SkinSight AI</h1>
            <span>Facial Skin Health Screening</span>
          </div>
        </div>
        <span className="header-badge">✦ AI-Powered Analysis</span>
      </header>

      {/* Hero */}
      {!results && (
        <section className="hero">
          <h2>
            Advanced <span className="gradient-text">AI Skin Analysis</span>
            <br />at Your Fingertips
          </h2>
          <p>
            Upload a clear photo of your face and receive an instant, comprehensive 
            skin health report powered by computer vision and machine learning.
          </p>
        </section>
      )}

      {/* Main Content */}
      <main className="main-content">
        {/* Upload */}
        {!results && (
          <ImageUpload onAnalyze={handleAnalyze} isLoading={isLoading} />
        )}

        {/* Error */}
        {error && (
          <div className="error-banner">
            <p>⚠️ {error}</p>
            <button
              className="analyze-btn"
              style={{ maxWidth: '200px', margin: '16px auto 0', fontSize: '0.9rem', padding: '10px 20px' }}
              onClick={() => { setError(null); setResults(null); }}
            >
              Try Again
            </button>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="results-container">
            {/* Processing Badge */}
            <div style={{ textAlign: 'center' }}>
              <span className="processing-badge">
                ⚡ Analyzed in {results.processing_time}s
              </span>
            </div>

            {/* New Analysis Button */}
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <button
                className="analyze-btn"
                style={{ maxWidth: '250px', margin: '0 auto', fontSize: '0.9rem', padding: '10px 20px' }}
                onClick={() => { setResults(null); setError(null); }}
              >
                📸 New Analysis
              </button>
            </div>

            {/* Overlays + Dashboard Grid */}
            <div className="results-grid">
              <CanvasOverlay data={results} />
              <AnalysisDashboard data={results} />
            </div>

            {/* Progress Tracker */}
            <ProgressTracker progress={results.progress} />

            {/* Recommendations */}
            <Recommendations recommendations={results.recommendations} />
          </div>
        )}
      </main>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <h3>Analyzing Your Skin...</h3>
          <div className="loading-steps">
            {LOADING_STEPS.map((step, i) => (
              <div
                key={i}
                className={`step ${i === loadingStep ? 'active' : i < loadingStep ? 'done' : ''}`}
              >
                {i < loadingStep ? '✅' : i === loadingStep ? '🔄' : '⏳'} {step}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Disclaimer Footer */}
      <footer className="disclaimer">
        <p>
          ⚕️ <strong>Medical Disclaimer:</strong> SkinSight AI is an AI-powered screening tool 
          and does NOT constitute medical diagnosis. Results are for informational purposes only. 
          Always consult a qualified dermatologist for medical advice and treatment.
        </p>
      </footer>
    </div>
  );
}

export default App;
