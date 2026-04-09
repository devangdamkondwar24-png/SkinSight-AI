"""
Skin Analyzer Service

Performs comprehensive skin health analysis:
- Acne severity grading (Clear/Mild/Moderate/Severe)
- Lesion detection with YOLOv8 (trained model) + CV fallback
- Facial zone condition assessment
- Hyperpigmentation detection and coverage estimation
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional


# Lesion type color mapping (as per client spec)
LESION_COLORS = {
    "comedonal": {"color": [0, 255, 0], "hex": "#00ff00", "label": "Comedonal"},       # Green
    "inflammatory": {"color": [255, 0, 0], "hex": "#ff0000", "label": "Inflammatory"},  # Red
    "other": {"color": [0, 100, 255], "hex": "#0064ff", "label": "Other"},              # Blue
}

# Acne severity thresholds
SEVERITY_LEVELS = {
    "Clear": {"min": 0, "max": 0, "index": 0},
    "Mild": {"min": 1, "max": 5, "index": 1},
    "Moderate": {"min": 6, "max": 15, "index": 2},
    "Severe": {"min": 16, "max": 999, "index": 3},
}

# Lesion count buckets
COUNT_BUCKETS = ["0-2", "3-5", "5-10", "11-15", "15+"]


class SkinAnalyzer:
    """Comprehensive skin health analysis engine."""

    def __init__(self, model_path: Optional[str] = None):
        self.yolo_model = None
        self._load_model(model_path)

    def _load_model(self, model_path: Optional[str] = None):
        """Load trained YOLOv8 model if available."""
        if model_path is None:
            model_path = str(Path(__file__).parent.parent / "models" / "acne_detector.pt")

        if Path(model_path).exists():
            try:
                from ultralytics import YOLO
                self.yolo_model = YOLO(model_path)
                print(f"  [OK] Loaded trained model: {model_path}")
            except Exception as e:
                print(f"  [WARN] Failed to load YOLO model: {e}")
                self.yolo_model = None
        else:
            print(f"  [INFO] No trained model found at {model_path}. Using CV-based detection.")

    def analyze(self, image: np.ndarray, face_data: dict) -> dict:
        """
        Run full skin analysis on the image.

        Returns dict with: acne_severity, lesions, zone_health, hyperpigmentation
        """
        if not face_data.get("detected"):
            return self._empty_result()

        # Detect lesions (YOLO or CV fallback)
        lesions = self._detect_lesions(image, face_data)

        # Grade acne severity
        acne_severity = self._grade_severity(lesions)

        # Assess zone health
        zone_health = self._assess_zones(image, face_data, lesions)

        # Detect hyperpigmentation
        hyperpigmentation = self._detect_hyperpigmentation(image, face_data)

        # Lesion count bucket
        count = len(lesions)
        if count <= 2:
            count_bucket = "0-2"
        elif count <= 5:
            count_bucket = "3-5"
        elif count <= 10:
            count_bucket = "5-10"
        elif count <= 15:
            count_bucket = "11-15"
        else:
            count_bucket = "15+"

        return {
            "acne_severity": acne_severity,
            "lesions": lesions,
            "lesion_count": count,
            "lesion_count_bucket": count_bucket,
            "zone_health": zone_health,
            "hyperpigmentation": hyperpigmentation,
        }

    def _detect_lesions(self, image: np.ndarray, face_data: dict) -> list:
        """Detect lesions using trained YOLO model or CV fallback."""
        if self.yolo_model is not None:
            return self._detect_lesions_yolo(image)
        return self._detect_lesions_cv(image, face_data)

    def _detect_lesions_yolo(self, image: np.ndarray) -> list:
        """Detect lesions using the trained YOLOv8 model."""
        results = self.yolo_model(image, conf=0.25, verbose=False)
        lesions = []
        lesion_id = 1

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = result.names.get(cls_id, "other").lower()

                # Map class names to our categories
                lesion_type = self._classify_lesion_type(cls_name)
                color_info = LESION_COLORS.get(lesion_type, LESION_COLORS["other"])

                lesions.append({
                    "id": f"L{lesion_id}",
                    "bbox": {"x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)},
                    "confidence": round(conf, 2),
                    "type": lesion_type,
                    "class_name": cls_name,
                    "color": color_info["hex"],
                    "color_rgb": color_info["color"],
                    "label": color_info["label"],
                })
                lesion_id += 1

        return lesions

    def _classify_lesion_type(self, class_name: str) -> str:
        """Map YOLO class names to our lesion categories."""
        comedonal_keywords = ["comedone", "blackhead", "whitehead", "closed", "open"]
        inflammatory_keywords = ["pustule", "papule", "nodule", "cyst", "inflammatory",
                                 "acne", "pimple"]

        name = class_name.lower()
        for kw in comedonal_keywords:
            if kw in name:
                return "comedonal"
        for kw in inflammatory_keywords:
            if kw in name:
                return "inflammatory"
        return "other"

    def _detect_lesions_cv(self, image: np.ndarray, face_data: dict) -> list:
        """
        Fallback: detect lesions using computer vision heuristics.
        Uses color-space analysis, texture variance, and contour detection.
        """
        h, w = image.shape[:2]
        landmarks = face_data.get("landmarks", [])
        if not landmarks:
            return []

        # Create face mask from landmarks
        face_mask = self._create_face_mask(landmarks, w, h)

        # Convert to LAB for better skin analysis
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)

        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        s_ch = hsv[:, :, 1]

        # Skin-only analysis
        skin_l = cv2.bitwise_and(l_ch, l_ch, mask=face_mask)
        skin_a = cv2.bitwise_and(a_ch, a_ch, mask=face_mask)

        # Detect redness (high 'a' channel = red in LAB)
        mean_a = cv2.mean(a_ch, mask=face_mask)[0]
        std_a = np.std(a_ch[face_mask > 0]) if np.any(face_mask > 0) else 1

        # Threshold for inflamed regions (abnormally red)
        red_thresh = mean_a + 1.2 * std_a
        red_mask = cv2.threshold(a_ch, int(red_thresh), 255, cv2.THRESH_BINARY)[1]
        red_mask = cv2.bitwise_and(red_mask, red_mask, mask=face_mask)

        # Detect dark spots (low luminance relative to mean)
        mean_l = cv2.mean(l_ch, mask=face_mask)[0]
        std_l = np.std(l_ch[face_mask > 0]) if np.any(face_mask > 0) else 1
        dark_thresh = mean_l - 1.5 * std_l
        dark_mask = cv2.threshold(l_ch, int(max(dark_thresh, 20)), 255, cv2.THRESH_BINARY_INV)[1]
        dark_mask = cv2.bitwise_and(dark_mask, dark_mask, mask=face_mask)

        # High saturation spots (potential blemishes)
        mean_s = cv2.mean(s_ch, mask=face_mask)[0]
        std_s = np.std(s_ch[face_mask > 0]) if np.any(face_mask > 0) else 1
        sat_thresh = mean_s + 1.5 * std_s
        sat_mask = cv2.threshold(s_ch, int(min(sat_thresh, 200)), 255, cv2.THRESH_BINARY)[1]
        sat_mask = cv2.bitwise_and(sat_mask, sat_mask, mask=face_mask)

        # Combine masks
        combined = cv2.bitwise_or(red_mask, dark_mask)
        combined = cv2.bitwise_or(combined, sat_mask)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel) 
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        lesions = []
        lesion_id = 1
        min_area = (w * h) * 0.0003  # Minimum lesion size
        max_area = (w * h) * 0.05    # Maximum lesion size

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area or area > max_area:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)

            # Classify based on color characteristics in the region
            roi_a = a_ch[y:y+bh, x:x+bw]
            roi_l = l_ch[y:y+bh, x:x+bw]
            roi_s = s_ch[y:y+bh, x:x+bw]

            mean_roi_a = np.mean(roi_a) if roi_a.size > 0 else mean_a
            mean_roi_l = np.mean(roi_l) if roi_l.size > 0 else mean_l
            mean_roi_s = np.mean(roi_s) if roi_s.size > 0 else mean_s

            # Classification logic
            if mean_roi_a > mean_a + std_a and mean_roi_s > mean_s:
                lesion_type = "inflammatory"
            elif mean_roi_l < mean_l - 0.5 * std_l:
                lesion_type = "comedonal"
            else:
                lesion_type = "other"

            color_info = LESION_COLORS[lesion_type]
            confidence = min(0.95, 0.5 + (abs(mean_roi_a - mean_a) / (3 * std_a + 0.01)))

            lesions.append({
                "id": f"L{lesion_id}",
                "bbox": {"x1": int(x), "y1": int(y), "x2": int(x + bw), "y2": int(y + bh)},
                "confidence": round(float(confidence), 2),
                "type": lesion_type,
                "class_name": lesion_type,
                "color": color_info["hex"],
                "color_rgb": color_info["color"],
                "label": color_info["label"],
            })
            lesion_id += 1

        return lesions

    def _create_face_mask(self, landmarks: list, w: int, h: int) -> np.ndarray:
        """Create a binary mask of the face region from landmarks."""
        mask = np.zeros((h, w), dtype=np.uint8)
        # Use the face oval indices
        face_oval = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        
        points = []
        for idx in face_oval:
            if idx < len(landmarks):
                lm = landmarks[idx]
                points.append([int(lm["x"] * w), int(lm["y"] * h)])

        if points:
            pts = np.array(points, dtype=np.int32)
            cv2.fillConvexPoly(mask, pts, 255)

        return mask

    def _grade_severity(self, lesions: list) -> dict:
        """Grade acne severity based on lesion count and types."""
        count = len(lesions)
        inflammatory_count = sum(1 for l in lesions if l["type"] == "inflammatory")

        if count == 0:
            grade = "Clear"
            score = 0
        elif count <= 5 and inflammatory_count <= 2:
            grade = "Mild"
            score = 25 + min(count * 5, 25)
        elif count <= 15 and inflammatory_count <= 8:
            grade = "Moderate"
            score = 50 + min(count * 2, 25)
        else:
            grade = "Severe"
            score = 75 + min(count, 25)

        return {
            "grade": grade,
            "score": min(score, 100),
            "total_lesions": count,
            "inflammatory_count": inflammatory_count,
            "comedonal_count": sum(1 for l in lesions if l["type"] == "comedonal"),
            "other_count": sum(1 for l in lesions if l["type"] == "other"),
        }

    def _assess_zones(self, image: np.ndarray, face_data: dict, lesions: list) -> dict:
        """Assess skin health in each facial zone."""
        h, w = image.shape[:2]
        zones = face_data.get("zones", {})
        zone_health = {}

        for zone_name, zone_info in zones.items():
            points = zone_info.get("points", [])
            if not points:
                zone_health[zone_name] = {
                    "affected": False,
                    "severity": "clear",
                    "lesion_count": 0,
                    "description": "No data",
                }
                continue

            # Create zone polygon
            zone_poly = np.array([[p["x"], p["y"]] for p in points], dtype=np.int32)

            # Count lesions in this zone
            zone_lesions = 0
            for lesion in lesions:
                bbox = lesion["bbox"]
                cx = (bbox["x1"] + bbox["x2"]) // 2
                cy = (bbox["y1"] + bbox["y2"]) // 2
                if cv2.pointPolygonTest(zone_poly, (cx, cy), False) >= 0:
                    zone_lesions += 1

            # Determine zone severity
            if zone_lesions == 0:
                severity = "clear"
                affected = False
            elif zone_lesions <= 2:
                severity = "mild"
                affected = True
            elif zone_lesions <= 5:
                severity = "moderate"
                affected = True
            else:
                severity = "severe"
                affected = True

            zone_health[zone_name] = {
                "affected": affected,
                "severity": severity,
                "lesion_count": zone_lesions,
                "points": points,
                "description": f"{severity.capitalize()} — {zone_lesions} lesion(s) detected",
            }

        return zone_health

    def _detect_hyperpigmentation(self, image: np.ndarray, face_data: dict) -> dict:
        """Detect hyperpigmented regions on the face."""
        h, w = image.shape[:2]
        landmarks = face_data.get("landmarks", [])
        if not landmarks:
            return {"coverage_pct": 0, "coverage_bucket": "0-10%", "regions": [], "mask": None}

        face_mask = self._create_face_mask(landmarks, w, h)

        # Convert to LAB
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_ch = lab[:, :, 0]

        # Get skin luminance stats
        skin_pixels = l_ch[face_mask > 0]
        if len(skin_pixels) == 0:
            return {"coverage_pct": 0, "coverage_bucket": "0-10%", "regions": [], "mask": None}

        mean_l = np.mean(skin_pixels)
        std_l = np.std(skin_pixels)

        # Dark spots = significantly darker than average skin
        dark_threshold = mean_l - 1.0 * std_l
        dark_mask = np.zeros_like(l_ch)
        dark_mask[(l_ch < dark_threshold) & (face_mask > 0)] = 255

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel)

        # Calculate coverage
        face_area = np.sum(face_mask > 0)
        dark_area = np.sum(dark_mask > 0)
        coverage_pct = round((dark_area / face_area * 100) if face_area > 0 else 0, 1)

        # Coverage bucket
        if coverage_pct < 10:
            bucket = "0-10%"
        elif coverage_pct < 20:
            bucket = "10-20%"
        elif coverage_pct < 30:
            bucket = "20-30%"
        else:
            bucket = "30+%"

        # Find region contours
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        regions = []
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area < (w * h) * 0.001:  # Skip tiny regions
                continue
            points = cnt.squeeze().tolist()
            if isinstance(points[0], int):
                points = [points]
            regions.append({
                "id": f"P{i+1}",
                "points": [{"x": int(p[0]), "y": int(p[1])} for p in points if len(p) == 2],
                "area": int(area),
            })

        return {
            "coverage_pct": coverage_pct,
            "coverage_bucket": bucket,
            "regions": regions,
            "region_count": len(regions),
        }

    def _empty_result(self) -> dict:
        """Return empty analysis result when no face detected."""
        return {
            "acne_severity": {"grade": "Unknown", "score": 0, "total_lesions": 0,
                              "inflammatory_count": 0, "comedonal_count": 0, "other_count": 0},
            "lesions": [],
            "lesion_count": 0,
            "lesion_count_bucket": "0-2",
            "zone_health": {},
            "hyperpigmentation": {"coverage_pct": 0, "coverage_bucket": "0-10%",
                                  "regions": [], "region_count": 0},
        }
