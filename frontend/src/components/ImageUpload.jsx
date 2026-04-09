import { useState, useRef, useCallback } from 'react';

export default function ImageUpload({ onAnalyze, isLoading }) {
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleFile = useCallback((selectedFile) => {
    if (!selectedFile) return;
    if (!selectedFile.type.startsWith('image/')) {
      alert('Please upload an image file (JPG, PNG, WEBP)');
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('Image too large. Max 10MB.');
      return;
    }
    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(selectedFile);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFile(droppedFile);
  }, [handleFile]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleRemove = useCallback(() => {
    setFile(null);
    setPreview(null);
    if (inputRef.current) inputRef.current.value = '';
  }, []);

  const handleSubmit = useCallback(() => {
    if (file && onAnalyze) {
      onAnalyze(file);
    }
  }, [file, onAnalyze]);

  return (
    <div className="upload-section">
      <div
        className={`upload-zone glass-card ${dragOver ? 'drag-over' : ''}`}
        onClick={() => !preview && inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        id="upload-zone"
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={(e) => handleFile(e.target.files[0])}
          style={{ display: 'none' }}
          id="file-input"
        />

        {!preview ? (
          <>
            <span className="upload-icon">📸</span>
            <h3>Upload Your Face Photo</h3>
            <p>Drag & drop a clear, front-facing photograph for AI analysis</p>
            <button className="browse-btn" type="button">Browse Files</button>
            <p style={{ marginTop: '12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Supports JPG, PNG, WEBP • Max 10MB
            </p>
          </>
        ) : (
          <div className="upload-preview" onClick={(e) => e.stopPropagation()}>
            <button className="remove-btn" onClick={handleRemove} title="Remove image">✕</button>
            <img src={preview} alt="Preview" />
          </div>
        )}
      </div>

      {preview && (
        <button
          className="analyze-btn"
          onClick={handleSubmit}
          disabled={isLoading}
          id="analyze-btn"
        >
          {isLoading ? '🔬 Analyzing...' : '🔬 Analyze Skin Health'}
        </button>
      )}
    </div>
  );
}
