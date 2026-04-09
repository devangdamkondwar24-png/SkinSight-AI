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


# Refined zone landmark indices for segmentation
FOREHEAD_INDICES = [10, 338, 297, 332, 284, 251, 389, 356, 454,
                    323, 361, 288, 278, 344, 340, 261, 446, 255,
                    339, 254, 253, 252, 256, 341, 463, 414, 286,
                    258, 257, 259, 260, 467, 299, 296, 336, 9,
                    107, 66, 69, 104, 68, 71, 21, 54, 103, 67, 109]

LEFT_CHEEK_INDICES = [93, 132, 58, 172, 136, 150, 149, 176, 148, 152]

RIGHT_CHEEK_INDICES = [323, 361, 288, 397, 365, 379, 378, 400, 377, 152]

NOSE_INDICES = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 164, 0, 11,
                12, 13, 14, 15, 16, 17, 18, 200, 199, 175]

CHIN_INDICES = [152, 377, 400, 378, 379, 365, 397, 288, 361, 323,
                454, 356, 389, 251, 284, 332, 297, 338, 10, 109,
                67, 103, 54, 21, 162, 127, 234, 93, 132, 58, 172,
                136, 150, 149, 176, 148]

FACE_OVAL_INDICES = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]


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
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
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

        Args:
            image: BGR numpy array from OpenCV

        Returns:
            dict with 'landmarks', 'connections', 'zones', and 'detected'
        """
        h, w = image.shape[:2]

        # Convert BGR to RGB for MediaPipe
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self.landmarker.detect(mp_image)

        if not result.face_landmarks or len(result.face_landmarks) == 0:
            return {"landmarks": [], "connections": [], "zones": {}, "detected": False}

        face = result.face_landmarks[0]

        # Normalize landmarks
        landmarks = []
        for lm in face:
            landmarks.append({
                "x": round(lm.x, 6),
                "y": round(lm.y, 6),
                "z": round(lm.z, 6),
            })

        # Extract zone polygons
        zones = self._extract_zones(landmarks, w, h)

        return {
            "landmarks": landmarks,
            "connections": self.connections,
            "zones": zones,
            "detected": True,
            "image_width": w,
            "image_height": h,
        }

    def _extract_zones(self, landmarks: list, w: int, h: int) -> dict:
        """Extract facial zone polygon boundaries from landmarks."""
        zone_defs = {
            "forehead": FOREHEAD_INDICES,
            "left_cheek": LEFT_CHEEK_INDICES,
            "right_cheek": RIGHT_CHEEK_INDICES,
            "nose": NOSE_INDICES,
            "chin_jawline": CHIN_INDICES,
        }

        zones = {}
        for name, indices in zone_defs.items():
            points = []
            for idx in indices:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    points.append({
                        "x": round(lm["x"] * w),
                        "y": round(lm["y"] * h),
                    })
            zones[name] = {
                "points": points,
                "affected": False,
                "severity": "clear",
            }

        return zones

    def get_face_mask(self, landmarks: list, w: int, h: int) -> np.ndarray:
        """Create a binary mask of the face region from landmarks."""
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
