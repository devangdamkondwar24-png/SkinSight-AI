"""
Face Mesh Service — MediaPipe Tasks API (FaceLandmarker)

Extracts 478 3D facial landmarks for:
- Face mesh grid overlay rendering
- Facial zone boundary definition
- Analysis coverage area visualization
"""

import cv2
import numpy as np
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    FaceLandmarksConnections,
    RunningMode,
)


# Standard clinical facial zone landmark indices
# These are grouped by anatomical regions for dermatology
FOREHEAD_INDICES = [103, 67, 109, 10, 338, 297, 332, 284, 251, 21, 54, 103, 
                    10, 338, 297, 332, 9, 284, 251, 68, 104, 69, 108, 151, 337, 299, 333]

LEFT_CHEEK_INDICES = [116, 117, 118, 101, 123, 111, 147, 213, 192, 214, 210, 211, 208, 142]

RIGHT_CHEEK_INDICES = [345, 346, 347, 330, 352, 340, 376, 433, 416, 434, 430, 431, 428, 371]

NOSE_INDICES = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 164, 0, 48, 278, 219, 439]

CHIN_INDICES = [152, 377, 400, 378, 379, 365, 397, 148, 176, 149, 150, 136, 172, 152]

JAWLINE_INDICES = [58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 234, 127, 454, 356, 10]

FACE_OVAL_INDICES = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

EYE_LEFT_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
EYE_RIGHT_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
LIPS_OUTER_INDICES = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]


class FaceMeshService:
    """Extract facial landmarks using MediaPipe Tasks FaceLandmarker."""

    def __init__(self):
        model_path = str(Path(__file__).parent.parent / "models" / "face_landmarker.task")

        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Face landmarker model not found at {model_path}. "
                "Download it from: https://storage.googleapis.com/mediapipe-models/"
                "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            )

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.15,
            min_face_presence_confidence=0.15,
            min_tracking_confidence=0.15,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )

        self.landmarker = FaceLandmarker.create_from_options(options)

        # Build tessellation connections list
        self.connections = []
        for conn in FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION:
            self.connections.append([conn.start, conn.end])

    def process(self, image: np.ndarray) -> dict:
        """
        Extract face mesh landmarks from an image.
        """
        h, w = image.shape[:2]
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self.landmarker.detect(mp_image)

        if not result.face_landmarks or len(result.face_landmarks) == 0:
            return {"landmarks": [], "connections": [], "zones": {}, "detected": False}

        face = result.face_landmarks[0]
        landmarks = []
        for lm in face:
            landmarks.append({
                "x": round(lm.x, 6),
                "y": round(lm.y, 6),
                "z": round(lm.z, 6),
            })

        # Extract zone polygons
        zones = self._extract_zones(landmarks, w, h)

        # Specialized masking regions (Eyes/Lips)
        feature_masks = {
            "eye_left": [landmarks[i] for i in EYE_LEFT_INDICES if i < len(landmarks)],
            "eye_right": [landmarks[i] for i in EYE_RIGHT_INDICES if i < len(landmarks)],
            "lips": [landmarks[i] for i in LIPS_OUTER_INDICES if i < len(landmarks)]
        }

        return {
            "landmarks": landmarks,
            "connections": self.connections,
            "zones": zones,
            "feature_masks": feature_masks,
            "detected": True,
            "image_width": w,
            "image_height": h,
        }

    def _extract_zones(self, landmarks: list, w: int, h: int) -> dict:
        """
        Extract facial zone polygon boundaries.
        Uses Convex Hull to ensure smooth, clinical geometry.
        """
        zone_defs = {
            "forehead": {"indices": FOREHEAD_INDICES, "label": "Forehead"},
            "left_cheek": {"indices": LEFT_CHEEK_INDICES, "label": "Left Cheek"},
            "right_cheek": {"indices": RIGHT_CHEEK_INDICES, "label": "Right Cheek"},
            "nose": {"indices": NOSE_INDICES, "label": "Nose"},
            "chin": {"indices": CHIN_INDICES, "label": "Chin"},
            "jawline": {"indices": JAWLINE_INDICES, "label": "Jawline"},
        }

        zones = {}
        for name, config in zone_defs.items():
            raw_points = []
            for idx in config["indices"]:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    raw_points.append([round(lm["x"] * w), round(lm["y"] * h)])
            
            if not raw_points:
                continue
            
            # CONVEX HULL SMOOTHING: Transform jagged points into a clean, solid block
            pts_arr = np.array(raw_points, dtype=np.int32)
            hull = cv2.convexHull(pts_arr)
            
            smooth_points = []
            for pt in hull:
                smooth_points.append({
                    "x": int(pt[0][0]),
                    "y": int(pt[0][1]),
                })

            zones[name] = {
                "display_name": config["label"],
                "points": smooth_points,
                "affected": False,
                "severity": "clear",
            }

        # Side-Profile Filter
        if "left_cheek" in zones and "right_cheek" in zones:
            l_pts = np.array([[p["x"], p["y"]] for p in zones["left_cheek"]["points"]], dtype=np.float32)
            r_pts = np.array([[p["x"], p["y"]] for p in zones["right_cheek"]["points"]], dtype=np.float32)
            
            l_area = cv2.contourArea(l_pts)
            r_area = cv2.contourArea(r_pts)
            
            if l_area > 0 and r_area > 0:
                if l_area < r_area * 0.20:
                    del zones["left_cheek"]
                elif r_area < l_area * 0.20:
                    del zones["right_cheek"]

        return zones

    def get_face_mask(self, landmarks: list, w: int, h: int) -> np.ndarray:
        """Create a binary mask of the face region."""
        mask = np.zeros((h, w), dtype=np.uint8)
        points = []
        for idx in FACE_OVAL_INDICES:
            if idx < len(landmarks):
                lm = landmarks[idx]
                points.append([int(lm["x"] * w), int(lm["y"] * h)])

        if points:
            pts = np.array(points, dtype=np.int32)
            cv2.fillConvexPoly(mask, pts, 255)

        return mask
