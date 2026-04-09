import { useRef, useEffect, useState, useCallback } from 'react';

const OVERLAY_LAYERS = [
  { id: 'mesh', label: 'Face Mesh', icon: '🕸️', color: '#7c5cfc' },
  { id: 'boxes', label: 'Lesion Boxes', icon: '🔲', color: '#ff6b9d' },
  { id: 'zones', label: 'Zone Map', icon: '🗺️', color: '#00d4aa' },
  { id: 'pigmentation', label: 'Pigmentation', icon: '🟤', color: '#d2691e' },
  { id: 'heatmap', label: 'Heatmap', icon: '🌡️', color: '#ff4757' },
];

const ZONE_COLORS = {
  forehead: 'rgba(124, 92, 252, 0.15)',
  left_cheek: 'rgba(0, 212, 170, 0.15)',
  right_cheek: 'rgba(78, 205, 196, 0.15)',
  nose: 'rgba(255, 179, 71, 0.15)',
  chin_jawline: 'rgba(255, 107, 157, 0.15)',
};

const ZONE_STROKE = {
  forehead: '#7c5cfc',
  left_cheek: '#00d4aa',
  right_cheek: '#4ecdc4',
  nose: '#ffb347',
  chin_jawline: '#ff6b9d',
};

export default function CanvasOverlay({ data }) {
  const canvasRef = useRef(null);
  const heatmapImgRef = useRef(null);
  const [activeLayers, setActiveLayers] = useState(new Set(['mesh', 'boxes']));
  const [imgLoaded, setImgLoaded] = useState(false);
  const imgRef = useRef(null);

  const toggleLayer = useCallback((layerId) => {
    setActiveLayers((prev) => {
      const next = new Set(prev);
      if (next.has(layerId)) next.delete(layerId);
      else next.add(layerId);
      return next;
    });
  }, []);

  // Load base image
  useEffect(() => {
    if (!data?.image?.base64) return;
    const img = new Image();
    img.onload = () => {
      imgRef.current = img;
      setImgLoaded(true);
    };
    img.src = `data:image/jpeg;base64,${data.image.base64}`;
  }, [data?.image?.base64]);

  // Load heatmap image
  useEffect(() => {
    if (!data?.heatmap?.image_base64) return;
    const img = new Image();
    img.onload = () => { heatmapImgRef.current = img; };
    img.src = `data:image/png;base64,${data.heatmap.image_base64}`;
  }, [data?.heatmap?.image_base64]);

  // Draw canvas
  useEffect(() => {
    if (!imgLoaded || !canvasRef.current || !imgRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = imgRef.current;

    // Set canvas size to match container while maintaining aspect ratio
    const maxWidth = canvas.parentElement?.clientWidth || 600;
    const scale = Math.min(maxWidth / img.width, 1);
    canvas.width = img.width * scale;
    canvas.height = img.height * scale;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw base image
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    const w = data.image.width;
    const h = data.image.height;
    const sx = canvas.width / w;
    const sy = canvas.height / h;

    // Draw heatmap overlay
    if (activeLayers.has('heatmap') && heatmapImgRef.current) {
      ctx.globalAlpha = 0.5;
      ctx.drawImage(heatmapImgRef.current, 0, 0, canvas.width, canvas.height);
      ctx.globalAlpha = 1.0;
    }

    // Draw zone segmentation
    if (activeLayers.has('zones') && data.analysis?.zone_health) {
      Object.entries(data.analysis.zone_health).forEach(([name, zone]) => {
        const points = zone.points;
        if (!points || points.length < 3) return;

        ctx.beginPath();
        ctx.moveTo(points[0].x * sx, points[0].y * sy);
        for (let i = 1; i < points.length; i++) {
          ctx.lineTo(points[i].x * sx, points[i].y * sy);
        }
        ctx.closePath();

        ctx.fillStyle = ZONE_COLORS[name] || 'rgba(255,255,255,0.1)';
        ctx.fill();

        ctx.strokeStyle = ZONE_STROKE[name] || '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Zone label
        const cx = points.reduce((s, p) => s + p.x, 0) / points.length * sx;
        const cy = points.reduce((s, p) => s + p.y, 0) / points.length * sy;
        ctx.font = `bold ${Math.max(10, 11 * scale)}px Inter, sans-serif`;
        ctx.fillStyle = ZONE_STROKE[name] || '#ffffff';
        ctx.textAlign = 'center';
        ctx.fillText(name.replace('_', ' ').toUpperCase(), cx, cy);
      });
    }

    // Draw hyperpigmentation outlines
    if (activeLayers.has('pigmentation') && data.analysis?.hyperpigmentation?.regions) {
      data.analysis.hyperpigmentation.regions.forEach((region) => {
        const pts = region.points;
        if (!pts || pts.length < 3) return;

        ctx.beginPath();
        ctx.moveTo(pts[0].x * sx, pts[0].y * sy);
        for (let i = 1; i < pts.length; i++) {
          ctx.lineTo(pts[i].x * sx, pts[i].y * sy);
        }
        ctx.closePath();

        ctx.fillStyle = 'rgba(210, 105, 30, 0.2)';
        ctx.fill();
        ctx.strokeStyle = '#d2691e';
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 3]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Label
        const cx = pts.reduce((s, p) => s + p.x, 0) / pts.length * sx;
        const cy = pts.reduce((s, p) => s + p.y, 0) / pts.length * sy;
        ctx.font = `bold ${Math.max(9, 10 * scale)}px Inter, sans-serif`;
        ctx.fillStyle = '#d2691e';
        ctx.textAlign = 'center';
        ctx.fillText(region.id, cx, cy);
      });
    }

    // Draw face mesh
    if (activeLayers.has('mesh') && data.face_mesh?.landmarks?.length) {
      const landmarks = data.face_mesh.landmarks;
      const connections = data.face_mesh.connections;

      // Draw mesh lines
      ctx.strokeStyle = 'rgba(124, 92, 252, 0.15)';
      ctx.lineWidth = 0.5;
      if (connections) {
        connections.forEach(([a, b]) => {
          if (a < landmarks.length && b < landmarks.length) {
            ctx.beginPath();
            ctx.moveTo(landmarks[a].x * w * sx, landmarks[a].y * h * sy);
            ctx.lineTo(landmarks[b].x * w * sx, landmarks[b].y * h * sy);
            ctx.stroke();
          }
        });
      }

      // Draw landmark dots
      ctx.fillStyle = 'rgba(124, 92, 252, 0.4)';
      landmarks.forEach((lm) => {
        ctx.beginPath();
        ctx.arc(lm.x * w * sx, lm.y * h * sy, 1, 0, Math.PI * 2);
        ctx.fill();
      });
    }

    // Draw lesion bounding boxes
    if (activeLayers.has('boxes') && data.analysis?.lesions?.length) {
      data.analysis.lesions.forEach((lesion) => {
        const { x1, y1, x2, y2 } = lesion.bbox;
        const lx = x1 * sx;
        const ly = y1 * sy;
        const lw = (x2 - x1) * sx;
        const lh = (y2 - y1) * sy;

        // Box
        ctx.strokeStyle = lesion.color;
        ctx.lineWidth = 2;
        ctx.strokeRect(lx, ly, lw, lh);

        // Semi-transparent fill
        const [r, g, b] = lesion.color_rgb;
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.1)`;
        ctx.fillRect(lx, ly, lw, lh);

        // Label background
        const labelText = `${lesion.id} ${lesion.label}`;
        ctx.font = `bold ${Math.max(9, 10 * scale)}px Inter, sans-serif`;
        const textWidth = ctx.measureText(labelText).width;
        const labelH = 16 * scale;

        ctx.fillStyle = lesion.color;
        ctx.fillRect(lx, ly - labelH, textWidth + 8 * scale, labelH);

        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'left';
        ctx.fillText(labelText, lx + 4 * scale, ly - 4 * scale);

        // Confidence
        const confText = `${Math.round(lesion.confidence * 100)}%`;
        ctx.font = `${Math.max(8, 9 * scale)}px Inter, sans-serif`;
        ctx.fillStyle = 'rgba(255,255,255,0.7)';
        ctx.fillText(confText, lx + 4 * scale, ly + 12 * scale);
      });
    }

  }, [imgLoaded, activeLayers, data]);

  if (!data) return null;

  return (
    <div className="overlay-panel glass-card">
      <h3 className="section-title">
        <span className="icon">🔬</span>
        Visual Analysis Overlays
      </h3>

      <div className="overlay-controls">
        {OVERLAY_LAYERS.map((layer) => (
          <button
            key={layer.id}
            className={`overlay-toggle ${activeLayers.has(layer.id) ? 'active' : ''}`}
            onClick={() => toggleLayer(layer.id)}
            id={`toggle-${layer.id}`}
          >
            <span className="dot" style={{ background: layer.color }}></span>
            {layer.icon} {layer.label}
          </button>
        ))}
      </div>

      <div className="canvas-container">
        <canvas ref={canvasRef} id="analysis-canvas" />
      </div>

      {data.analysis?.lesions?.length > 0 && (
        <div className="lesion-legend">
          <div className="legend-item">
            <span className="legend-dot comedonal"></span>
            Comedonal (Green)
          </div>
          <div className="legend-item">
            <span className="legend-dot inflammatory"></span>
            Inflammatory (Red)
          </div>
          <div className="legend-item">
            <span className="legend-dot other"></span>
            Other (Blue)
          </div>
        </div>
      )}
    </div>
  );
}
