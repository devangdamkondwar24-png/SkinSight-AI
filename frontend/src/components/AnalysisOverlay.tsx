"use client";

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ZoomIn } from "lucide-react";

interface AnalysisOverlayProps {
  data: any;
  showLesions?: boolean;
  showDarkSpots?: boolean;
  showZones?: boolean;
  showMesh?: boolean;
  showPigmentation?: boolean;
  showHeatmap?: boolean;
}

export function AnalysisOverlay({
  data,
  showLesions = true,
  showDarkSpots = true,
  showZones = false,
  showMesh = false,
  showPigmentation = false,
  showHeatmap = false,
}: AnalysisOverlayProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!data || !data.image) return null;

  const { width, height, base64 } = data.image;

  // ViewBox allows SVG to scale responsively exactly over the base image
  const viewBox = `0 0 ${width} ${height}`;

  const wrapperClasses = isExpanded
    ? "fixed inset-0 z-[100] bg-black/90 flex flex-col items-center justify-center cursor-zoom-out transition-all duration-300"
    : "group relative w-full aspect-[3/4] max-h-[60vh] bg-charcoal/5 rounded-[32px] overflow-hidden shadow-inner cursor-zoom-in transition-all duration-300";

  const imageClasses = isExpanded
    ? "absolute inset-0 w-full h-full object-contain p-4"
    : "absolute inset-0 w-full h-full object-cover rounded-[32px]";

  const svgAspect = isExpanded ? "xMidYMid meet" : "xMidYMid slice";

  return (
    <div className={wrapperClasses} onClick={() => setIsExpanded(!isExpanded)}>
      {/* Scanline Animation Effect */}
      <motion.div 
        animate={{ top: ["0%", "100%", "0%"] }}
        transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-mint to-transparent z-10 opacity-40 shadow-[0_0_15px_rgba(209,232,226,0.5)]"
      />
      {!isExpanded && (
        <div className="absolute top-4 right-4 z-20 w-8 h-8 rounded-full bg-white/40 backdrop-blur flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
           <ZoomIn className="w-4 h-4 text-charcoal" />
        </div>
      )}
      {isExpanded && (
        <div className="absolute top-6 right-6 z-20 w-12 h-12 rounded-full bg-white/10 backdrop-blur flex items-center justify-center hover:bg-white/20 transition-colors">
           <X className="w-6 h-6 text-white" />
        </div>
      )}

      {/* Base Image */}
      <img
        src={`data:image/jpeg;base64,${base64}`}
        alt="Analyzed Skin"
        className={imageClasses}
      />

      {/* Heatmap Overlay */}
      <AnimatePresence>
        {showHeatmap && data.heatmap && (
          <motion.img
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.6 }}
            exit={{ opacity: 0 }}
            src={data.heatmap.base64 ? `data:image/jpeg;base64,${data.heatmap.base64}` : `data:image/png;base64,${data.heatmap}`}
            className={`${imageClasses} mix-blend-screen opacity-60`}
          />
        )}
      </AnimatePresence>

      {/* SVG Overlay Layer */}
      <svg
        viewBox={viewBox}
        className={`absolute inset-0 w-full h-full pointer-events-none ${isExpanded ? 'p-4' : ''}`}
        preserveAspectRatio={svgAspect}
      >
        <AnimatePresence>
          {/* Face Mesh Map */}
          {showMesh && data.face_mesh?.connections && (
            <motion.g
              key="mesh-layer"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.3 }}
              exit={{ opacity: 0 }}
            >
              {data.face_mesh.connections.map((conn: any, i: number) => {
                const p1 = data.face_mesh.landmarks[conn[0]];
                const p2 = data.face_mesh.landmarks[conn[1]];
                return (
                  <line
                    key={`mesh-${i}`}
                    x1={p1.x * width}
                    y1={p1.y * height}
                    x2={p2.x * width}
                    y2={p2.y * height}
                    stroke="#D1E8E2"
                    strokeWidth="0.5"
                    strokeOpacity="0.4"
                  />
                );
              })}
            </motion.g>
          )}

          {/* Feature Mask Definition */}
          <defs>
            <mask id="feature-mask">
              <rect x="0" y="0" width="100%" height="100%" fill="white" />
              {/* Left Eye Cutout */}
              {data.face_mesh?.feature_masks?.eye_left && (
                <polygon 
                  points={data.face_mesh.feature_masks.eye_left.map((p: any) => `${p.x * width},${p.y * height}`).join(" ")} 
                  fill="black" 
                />
              )}
              {/* Right Eye Cutout */}
              {data.face_mesh?.feature_masks?.eye_right && (
                <polygon 
                  points={data.face_mesh.feature_masks.eye_right.map((p: any) => `${p.x * width},${p.y * height}`).join(" ")} 
                  fill="black" 
                />
              )}
              {/* Lips Cutout */}
              {data.face_mesh?.feature_masks?.lips && (
                <polygon 
                   points={data.face_mesh.feature_masks.lips.map((p: any) => `${p.x * width},${p.y * height}`).join(" ")} 
                   fill="black" 
                />
              )}
            </mask>
          </defs>

          {/* Zones Overlay with Anatomical Shielding */}
          {showZones && data.analysis?.zone_health && (
            <motion.g
              key="zones-layer"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              mask="url(#feature-mask)"
            >
              {Object.entries(data.analysis.zone_health).map(([zoneName, zone]: [string, any], i: number) => {
                if (!zone.points || zone.points.length === 0) return null;
                const pointsStr = zone.points.map((p: any) => `${p.x},${p.y}`).join(" ");
                
                let strokeColor = "rgba(209, 232, 226, 0.5)"; 
                if (zone.severity === "moderate") strokeColor = "rgba(255, 165, 0, 0.6)"; 
                if (zone.severity === "severe") strokeColor = "rgba(255, 0, 0, 0.6)"; 

                return (
                  <g key={`zone-group-${zoneName}`}>
                    <polygon
                      points={pointsStr}
                      fill={strokeColor.replace("0.6", "0.1").replace("0.5", "0.1")}
                      stroke={strokeColor}
                      strokeWidth="4"
                      strokeLinejoin="round"
                      strokeDasharray="8,4"
                      className="transition-all duration-700"
                    />
                    {/* On-Image Clinical Label */}
                    {zone.centroid && (
                      <g transform={`translate(${zone.centroid.x}, ${zone.centroid.y})`}>
                        <rect
                          x="-35"
                          y="-8"
                          width="70"
                          height="16"
                          rx="4"
                          fill="rgba(25, 28, 28, 0.7)"
                          className="backdrop-blur-sm"
                        />
                        <text
                          fill="white"
                          fontSize="7"
                          fontWeight="900"
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fontFamily="Inter, sans-serif"
                          className="uppercase tracking-[0.1em]"
                        >
                          {zone.display_name || zoneName}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}
            </motion.g>
          )}

          {/* Hyperpigmentation Overlay */}
          {showPigmentation && data.analysis?.hyperpigmentation?.regions && (
            <motion.g
              key="pigment-layer"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {data.analysis.hyperpigmentation.regions.map((region: any, i: number) => {
                if (!region.points || region.points.length === 0) return null;
                const pointsStr = region.points.map((p: any) => `${p.x},${p.y}`).join(" ");
                return (
                  <polygon
                    key={`pigment-${i}`}
                    points={pointsStr}
                    fill="none"
                    stroke="#8B4513" // Brownish
                    strokeWidth="2"
                  />
                );
              })}
            </motion.g>
          )}

          {/* Lesions Bounding Boxes (excluding dark spots) */}
          {showLesions && data.analysis?.lesions && (
            <motion.g
              key="lesions-layer"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {data.analysis.lesions
                .filter((lesion: any) => lesion.type !== 'dark_spot')
                .map((lesion: any) => {
                const { id, bbox, color, label } = lesion;
                const x = bbox.x1;
                const y = bbox.y1;
                const wBox = bbox.x2 - bbox.x1;
                const hBox = bbox.y2 - bbox.y1;

                return (
                  <g key={`lesion-${id}`}>
                    <rect
                      x={x - 2}
                      y={y - 2}
                      width={wBox + 4}
                      height={hBox + 4}
                      fill="none"
                      stroke={color}
                      strokeWidth="2"
                      strokeOpacity="0.8"
                      className="drop-shadow-sm"
                    />
                    <rect
                      x={x - 2}
                      y={y - 14}
                      width={22}
                      height={12}
                      fill={color}
                      fillOpacity="0.8"
                      rx="2"
                    />
                    <text
                      x={x + 3}
                      y={y - 4}
                      fill="#fff"
                      fontSize="8"
                      fontFamily="Inter, sans-serif"
                      fontWeight="black"
                      className="tracking-tighter"
                    >
                      {id}
                    </text>
                  </g>
                );
              })}
            </motion.g>
          )}

          {/* Dark Spots — purple dashed circles */}
          {showDarkSpots && data.analysis?.lesions && (
            <motion.g
              key="darkspots-layer"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {data.analysis.lesions
                .filter((lesion: any) => lesion.type === 'dark_spot')
                .map((lesion: any) => {
                const { id, bbox } = lesion;
                const cx = (bbox.x1 + bbox.x2) / 2;
                const cy = (bbox.y1 + bbox.y2) / 2;
                const rx = (bbox.x2 - bbox.x1) / 2 + 3;
                const ry = (bbox.y2 - bbox.y1) / 2 + 3;

                return (
                  <g key={`darkspot-${id}`}>
                    <ellipse
                      cx={cx}
                      cy={cy}
                      rx={rx}
                      ry={ry}
                      fill="rgba(180, 0, 255, 0.08)"
                      stroke="#b400ff"
                      strokeWidth="2"
                      strokeDasharray="4,3"
                      strokeOpacity="0.85"
                    />
                    <rect
                      x={cx - 11}
                      y={cy - ry - 14}
                      width={22}
                      height={12}
                      fill="#b400ff"
                      fillOpacity="0.85"
                      rx="2"
                    />
                    <text
                      x={cx - 6}
                      y={cy - ry - 4}
                      fill="#fff"
                      fontSize="7"
                      fontFamily="Inter, sans-serif"
                      fontWeight="bold"
                    >
                      {id}
                    </text>
                  </g>
                );
              })}
            </motion.g>
          )}
        </AnimatePresence>
      </svg>
    </div>
  );
}
