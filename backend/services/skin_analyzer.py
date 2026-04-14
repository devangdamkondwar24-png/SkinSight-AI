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


# ─── Anatomical Exclusion Zones (MediaPipe landmark indices) ───
# These regions are naturally red/dark and should NOT be flagged as lesions.

# Outer lips contour
LIP_OUTER_INDICES = [
    61, 146, 91, 181, 84, 17, 314, 405, 321, 375,
    291, 409, 270, 269, 267, 0, 37, 39, 40, 185,
]

# Inner lips contour
LIP_INNER_INDICES = [
    78, 95, 88, 178, 87, 14, 317, 402, 318, 324,
    308, 415, 310, 311, 312, 13, 82, 81, 80, 191,
]

# Eye regions (naturally dark/shadowed)
LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133,
                    173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249,
                     263, 466, 388, 387, 386, 385, 384, 398]

# Eyebrows
LEFT_EYEBROW_INDICES = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
RIGHT_EYEBROW_INDICES = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]

# Nose region (tip + nostrils — naturally red/shadowed)
NOSE_TIP_INDICES = [1, 2, 3, 4, 5, 6, 168, 197, 195, 5, 4, 1, 19, 94, 2, 164, 0, 11, 12]

# Additional exclusion: Philtrum/Mustache area
MUSTACHE_INDICES = [164, 0, 11, 12, 13, 14, 15, 16, 17, 18, 200, 199, 175, 2, 326, 327, 278, 48, 97, 98]

# High-precision "Mustache Shield" indices for the nuclear eraser
MUSTACHE_SANCTUARY_INDICES = [164, 2, 0, 61, 291, 37, 267, 39, 269, 186, 410]

# Additional exclusion: Hairline and Temple edges
HAIRLINE_INDICES = [10, 338, 297, 332, 284, 103, 54, 21, 162, 127, 234, 93, 132, 58, 172, 152, 377, 400]


# Lesion type color mapping (as per client spec)
LESION_COLORS = {
    "comedonal": {"color": [0, 255, 0], "hex": "#00ff00", "label": "Comedonal"},       # Green
    "inflammatory": {"color": [255, 0, 0], "hex": "#ff0000", "label": "Inflammatory"},  # Red
    "dark_spot": {"color": [180, 0, 255], "hex": "#b400ff", "label": "Dark Spot"},      # Purple
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
                import torch
                
                # PyTorch 2.6 defaults to weights_only=True which breaks YOLOv8 model unpickling.
                # We temporarily override torch.load to force weights_only=False
                _original_load = torch.load
                def _safe_load(*args, **kwargs):
                    kwargs['weights_only'] = False
                    return _original_load(*args, **kwargs)
                torch.load = _safe_load
                
                from ultralytics import YOLO
                self.yolo_model = YOLO(model_path)
                
                torch.load = _original_load # Restore functionality
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

        # Build anatomical exclusion mask (lips, eyes) with tight padding to preserve nearby skin
        h, w = image.shape[:2]
        landmarks = face_data.get("landmarks", [])
        exclusion_mask = self._build_exclusion_mask(landmarks, w, h, tight=True)
        
        # Build the "Sanctuary Mask": Face Mesh Oval INTERSECT Clinical Zones
        # This prevents detection in hair, background, or clothing.
        face_oval_mask = self._create_face_mask(landmarks, w, h)
        zones_mask = self._create_zones_mask(face_data, w, h)
        sanctuary_mask = cv2.bitwise_and(face_oval_mask, zones_mask)
        # Build hair mask (beard, mustache) restricted to the sanctuary
        hair_mask = self._build_hair_mask(image, sanctuary_mask)
        
        # Combined exclusions: Merge generated hair mask with landmark mask.
        hair_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        hair_mask_dilated = cv2.dilate(hair_mask, hair_kernel)
        
        # PROTECT EYES: Prevent hair mask from "swallowing" under-eye dark circles.
        eye_protection = self._build_exclusion_mask(landmarks, w, h, tight=False)
        hair_mask_dilated[eye_protection > 0] = 0
        
        full_exclusion = cv2.bitwise_or(exclusion_mask, hair_mask_dilated)
        
        # Detect lesions (YOLO or CV fallback)
        lesions = self._detect_lesions(image, face_data, full_exclusion)

        # FINAL SAFETY: Filter out any lesions falling outside the Sanctuary Mask
        lesions = [l for l in lesions if sanctuary_mask[
            min(h-1, max(0, (l["bbox"]["y1"] + l["bbox"]["y2"]) // 2)),
            min(w-1, max(0, (l["bbox"]["x1"] + l["bbox"]["x2"]) // 2))
        ] > 0]

        # Filter out false positives in exclusion zones and hair
        pre_filter_count = len(lesions)
        lesions = self._filter_exclusion_zones(lesions, full_exclusion)
        if len(lesions) != pre_filter_count:
            print(f"  [DEBUG] Filtered {pre_filter_count - len(lesions)} overlapping anatomical/hair exclusions")

        # Finalize lesion metadata (Color and Client-Required Labeling)
        # Green = comedonal, Red = inflammatory, Blue = other
        for l in lesions:
            if l["type"] == "inflammatory":
                l["color"] = "Red"
                l["type_label"] = "Inflammatory"
            elif l["type"] in ["comedonal", "dark_spot"]:
                l["type"] = "comedonal"  # Standardize for client requirement
                l["color"] = "Green"
                l["type_label"] = "Comedonal"
            else:
                l["color"] = "Blue"
                l["type_label"] = "Other"

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

    def _detect_lesions(self, image: np.ndarray, face_data: dict, full_exclusion: np.ndarray = None) -> list:
        """Detect lesions using trained YOLO model + CV-based supplemental detection."""
        lesions = []

        if self.yolo_model is not None:
            lesions = self._detect_lesions_yolo(image, face_data, full_exclusion)
            print(f"  [DEBUG] YOLO detections: {len(lesions)}")

        # Supplement with CV-based detectors
        dark_spots = self._detect_dark_spots(image, face_data, full_exclusion)
        print(f"  [DEBUG] Dark spot CV detections: {len(dark_spots)}")
        
        inflammatory_marks = self._detect_inflammatory_marks(image, face_data, full_exclusion)
        print(f"  [DEBUG] Inflammatory mark CV detections: {len(inflammatory_marks)}")

        dark_circles = self._detect_dark_circles(image, face_data, full_exclusion)
        print(f"  [DEBUG] Dark circle CV detections: {len(dark_circles)}")

        # Merge all detections
        lesions = self._merge_detections(lesions, dark_spots)
        lesions = self._merge_detections(lesions, inflammatory_marks)
        lesions = self._merge_detections(lesions, dark_circles)

        return lesions

    def _detect_lesions_yolo(self, image: np.ndarray, face_data: dict, exclusion_mask: np.ndarray = None) -> list:
        """Detect lesions using the trained YOLOv8 model."""
        h, w = image.shape[:2]
        # Low confidence (0.05)
        # Model requires absolute minimum conf (0.01) to detect spots, relying purely on spatial masks for noise
        results = self.yolo_model(image, conf=0.01, iou=0.25, verbose=False)
        lesions = []
        lesion_id = 1
        # Build face oval mask (where detections ARE allowed)
        landmarks = face_data.get("landmarks", [])
        face_mask = self._create_face_mask(landmarks, w, h) if landmarks else None

        # Build local exclusion if not provided (fallback)
        if exclusion_mask is None and landmarks:
            exclusion_mask = self._build_exclusion_mask(landmarks, w, h)

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = result.names.get(cls_id, "other").lower()

                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                # Clamp to image bounds
                cx = max(0, min(cx, w - 1))
                cy = max(0, min(cy, h - 1))

                # Must be inside the face oval
                if face_mask is not None and face_mask[cy, cx] == 0:
                    continue

                # Exclude detections that fall within anatomical exclusion zones
                if exclusion_mask is not None and exclusion_mask[cy, cx] > 0:
                    continue

                # Map class names to our categories
                lesion_type = self._classify_lesion_type(cls_name)
                color_info = LESION_COLORS.get(lesion_type, LESION_COLORS["other"])

                lesions.append({
                    "id": f"YOLO-{lesion_id}", # Identifiable YOLO tag
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

    def _detect_dark_spots(self, image: np.ndarray, face_data: dict, exclusion_mask: np.ndarray = None) -> list:
        """
        Detect dark spots (post-inflammatory hyperpigmentation, sun spots, melasma)
        using LAB L-channel local adaptive analysis.
        """
        h, w = image.shape[:2]
        landmarks = face_data.get("landmarks", [])
        if not landmarks:
            return []

        # Create face mask from landmarks
        face_mask = self._create_face_mask(landmarks, w, h)
        if not np.any(face_mask):
            return []
            
        # Dilate face mask slightly for better edge/jawline coverage on profile faces
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        face_mask = cv2.dilate(face_mask, kernel_dilate)
        
        # Apply anatomical exclusion (lips, hair, etc.) to the mask
        if exclusion_mask is not None:
            face_mask = cv2.bitwise_and(face_mask, cv2.bitwise_not(exclusion_mask))
            
        if not np.any(face_mask):
            return []

        # Convert to LAB for luminance analysis
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_ch = lab[:, :, 0]

        # Get face skin stats
        face_pixels = face_mask > 0
        mean_l = cv2.mean(l_ch, mask=face_mask)[0]
        std_l = max(np.std(l_ch[face_pixels]), 1.0)

        # Method 1: Multi-Scale Local Adaptive Detection
        # Finds spots that are sharply darker than their immediate surroundings
        # C value is positive: pixel < mean - C
        local_dark_small = cv2.adaptiveThreshold(l_ch, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 1.5)
        local_dark_med = cv2.adaptiveThreshold(l_ch, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 2.5)
        local_dark_large = cv2.adaptiveThreshold(l_ch, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 101, 3.5)
        combined = cv2.bitwise_or(local_dark_small, local_dark_med)
        combined = cv2.bitwise_or(combined, local_dark_large)
        combined = cv2.bitwise_and(combined, combined, mask=face_mask)

        # Precompute large Gaussian blur for local background contrast evaluation
        l_blur = cv2.GaussianBlur(l_ch, (51, 51), 0)

        # Morphological cleanup — close small gaps, remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        lesions = []
        lesion_id = 1
        min_area = (w * h) * 0.00005   # Significantly lowered to catch tiny freckles/moles
        max_area = (w * h) * 0.005    # Lowered max size to avoid large shadows and patches

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area or area > max_area:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)

            # Skip very elongated shapes (shadows along edges, sideburns, etc.)
            # Strict aspect ratio filter: genuine spots are highly circular/square
            aspect = max(bw, bh) / max(min(bw, bh), 1)
            if aspect > 1.6:
                continue

            # Verify it's genuinely darker than surrounding skin (LOCAL CONTRAST)
            roi_l = l_ch[y:y+bh, x:x+bw]
            roi_bg = l_blur[y:y+bh, x:x+bw]
            
            if roi_l.size == 0 or roi_bg.size == 0:
                continue
                
            spot_mean = np.mean(roi_l)
            bg_mean = np.mean(roi_bg)
            
            # Must be darker than LOCAL background by at least 0.5 luminance unit
            if spot_mean >= bg_mean - 0.5:
                continue

            color_info = LESION_COLORS["dark_spot"]
            # Confidence based on how much darker the spot is compared to its LOCAL surroundings
            local_contrast_diff = bg_mean - spot_mean
            # Adjusted confidence scaling: higher confidence for more contrast, but allows lower contrast spots
            confidence = min(0.95, 0.35 + (local_contrast_diff / 20.0) * 0.60)

            lesions.append({
                "id": f"D{lesion_id}",
                "bbox": {"x1": int(x), "y1": int(y), "x2": int(x + bw), "y2": int(y + bh)},
                "confidence": round(float(confidence), 2),
                "type": "dark_spot",
                "class_name": "dark_spot",
                "color": color_info["hex"],
                "color_rgb": color_info["color"],
                "label": color_info["label"],
            })
            lesion_id += 1

        return lesions

    def _detect_inflammatory_marks(self, image: np.ndarray, face_data: dict, exclusion_mask: np.ndarray = None) -> list:
        """
        Detect inflammatory marks (red patches, papules, pustules)
        using LAB a-channel (redness) local adaptive analysis.
        Adds high-sensitivity coverage for lesions missed by YOLO.
        """
        h, w = image.shape[:2]
        landmarks = face_data.get("landmarks", [])
        if not landmarks:
            return []

        # Create face mask
        face_mask = self._create_face_mask(landmarks, w, h)
        if not np.any(face_mask):
            return []

        # Erode face mask slightly (5px instead of 15px)
        kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        face_mask = cv2.erode(face_mask, kernel_erode)
        
        # Apply anatomical exclusion
        if exclusion_mask is not None:
            face_mask = cv2.bitwise_and(face_mask, cv2.bitwise_not(exclusion_mask))
            
        if not np.any(face_mask):
            return []

        # Convert to LAB for redness analysis (a-channel)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        a_ch = lab[:, :, 1]

        # --- SANCTUARY EDGE COVERAGE ---
        skin_mask = self._create_skin_mask(image)
        # L-Channel for Luminance Masking (Exclude dark hair/shadows)
        l_ch = lab[:, :, 0]
        
        # Calculate base L stats just for safe exclusion
        face_pixels_l = face_mask > 0
        mean_l = np.mean(l_ch[face_pixels_l]) if np.any(face_pixels_l) else 128
        std_l = np.std(l_ch[face_pixels_l]) if np.any(face_pixels_l) else 20
        
        # Reject intensely dark regions like hair/sideburns (typically 2+ std below average skin brightness)
        # 35 was virtually black. Using a dynamic threshold ensures hair is excluded.
        lum_thresh = max(40, mean_l - 2.0 * std_l)
        lum_mask = cv2.threshold(l_ch, int(lum_thresh), 255, cv2.THRESH_BINARY)[1]
        
        # Dilate face_mask comfortably (30-pixel buffer for profile edges)
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
        face_mask_dilated = cv2.dilate(face_mask, kernel_dilate)
        
        # INTERSECTION: Scan only Skin-Colored AND near face AND reasonably bright
        coverage_mask = cv2.bitwise_and(face_mask_dilated, skin_mask)
        coverage_mask = cv2.bitwise_and(coverage_mask, lum_mask)
        
        if exclusion_mask is not None:
            coverage_mask = cv2.bitwise_and(coverage_mask, cv2.bitwise_not(exclusion_mask))

        # SAFETY: Final check to ensure we have a scanning region
        if not np.any(coverage_mask):
             coverage_mask = face_mask
             if not np.any(coverage_mask):
                 coverage_mask = np.ones((h, w), dtype=np.uint8) * 255

        # Get stats with high safety
        face_pixels = coverage_mask > 0
        mean_a = cv2.mean(a_ch, mask=coverage_mask)[0]
        std_a = np.std(a_ch[face_pixels]) if np.any(face_pixels) else 1.0
        if np.isnan(std_a) or std_a < 0.1: std_a = 1.0

        # --- SANCTUARY EDGE SIGNAL 1: Global Redness (Safety Filter) ---
        # Spot must be slightly redder than the overall face average to count as "Inflammatory"
        global_red_thresh = mean_a + 0.05 * std_a
        global_red_mask = cv2.threshold(a_ch, int(global_red_thresh), 255, cv2.THRESH_BINARY)[1]

        # --- SANCTUARY EDGE SIGNAL 2: Multi-Scale Local Adaptive Detection ---
        # This solves the "Giant Face Box" problem. Adaptive testing ensures we only find
        # DISTINCT SPOTS that are locally redder than the skin 15-50 pixels right next to them.
        local_mask_small = cv2.adaptiveThreshold(a_ch, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, -1)
        local_mask_med = cv2.adaptiveThreshold(a_ch, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, -1.5)
        local_mask_large = cv2.adaptiveThreshold(a_ch, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 101, -2)
        local_mask = cv2.bitwise_or(local_mask_small, local_mask_med)
        local_mask = cv2.bitwise_or(local_mask, local_mask_large)

        # Merge Phase: Spot must be locally a spot (local_mask) AND generally red (global_red_mask)
        combined = cv2.bitwise_and(local_mask, global_red_mask)
        
        # Optional: Saturation boost mask to catch extremely saturated small red pixels
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        sat_mask = cv2.threshold(hsv[:, :, 1], int(np.mean(hsv[:,:,1]) + 20), 255, cv2.THRESH_BINARY)[1]
        sat_spot_mask = cv2.bitwise_and(sat_mask, local_mask)
        
        combined = cv2.bitwise_or(combined, sat_spot_mask)
        combined = cv2.bitwise_and(combined, combined, mask=coverage_mask)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        # Bypassed MORPH_OPEN to preserve even the smallest inflammatory markers
        # combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)

        # Find contours with robustness for different OpenCV versions
        cnts = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = cnts[0] if len(cnts) == 2 else cnts[1]

        lesions = []
        lesion_id = 1
        min_area = (w * h) * 0.0001
        max_area = (w * h) * 0.15     # 15% permitted to capture actual large cheek redness patches, but small enough to prevent jawline engulfment
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area or area > max_area:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            
            # Streak/Hair/Shadow Filter: Genuine inflammation clusters are highly circular. 
            # If the mark is elongated (like a shadow edge or strand of hair), drop it.
            aspect = max(bw, bh) / max(min(bw, bh), 1)
            if aspect > 1.6:
                continue

            # Re-verify redness in ROI (STRICT)
            roi_a = a_ch[y:y+bh, x:x+bw]
            if roi_a.size == 0:
                continue
            spot_mean_a = np.mean(roi_a)
            
            # Clinical check: ROI must be redder than baseline (Hyper-sensitive)
            if spot_mean_a < mean_a + 0.01 * std_a:
                continue

            color_info = LESION_COLORS["inflammatory"]
            # Confidence based on intensity of redness
            redness_ratio = (spot_mean_a - mean_a) / (std_a + 0.01)
            confidence = min(0.92, 0.45 + redness_ratio * 0.15)

            lesions.append({
                "id": f"CV-{lesion_id}", # Identifiable CV tag
                "bbox": {"x1": int(x), "y1": int(y), "x2": int(x + bw), "y2": int(y + bh)},
                "confidence": round(float(confidence), 2),
                "type": "inflammatory",
                "class_name": "inflammatory",
                "color": color_info["hex"],
                "color_rgb": color_info["color"],
                "label": color_info["label"],
            })
            lesion_id += 1

        return lesions

    def _detect_dark_circles(self, image: np.ndarray, face_data: dict, exclusion_mask: np.ndarray = None) -> list:
        """
        Specialized detector for periorbital hyperpigmentation (dark circles).
        Uses eye landmarks to define search ROIs and applies local adaptive sensing.
        """
        h, w = image.shape[:2]
        landmarks = face_data.get("landmarks", [])
        if not landmarks:
            return []

        # Convert to LAB for luminance analysis
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_ch = lab[:, :, 0]

        # Define specific eye-bottom landmarks for ROI construction
        # Left eye lower: 145, 153, 154, 155
        # Right eye lower: 374, 380, 381, 382
        eye_bottom_indices = {
            "left": [145, 153, 154, 155],
            "right": [374, 380, 381, 382]
        }

        lesions = []
        lesion_id = 1

        for side, indices in eye_bottom_indices.items():
            pts = []
            for idx in indices:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    pts.append([int(lm["x"] * w), int(lm["y"] * h)])
            
            if not pts:
                continue
            
            # Construct ROI: From the eye bottom down to about 20% of face height
            # We'll use the bounding box of the eye bottom and expand it downwards
            pts_arr = np.array(pts, dtype=np.int32)
            ex, ey, ew, eh = cv2.boundingRect(pts_arr)
            
            # Expand the ROI downwards to cover the dark circle area
            roi_y1 = ey
            roi_y2 = min(h - 1, ey + int(h * 0.12)) # 12% of face height is usually enough
            roi_x1 = max(0, ex - ew // 2)
            roi_x2 = min(w - 1, ex + ew + ew // 2)
            
            roi_l = l_ch[roi_y1:roi_y2, roi_x1:roi_x2]
            if roi_l.size == 0:
                continue

            # Local detection in eye-specific ROI
            # Using very large block sizes to catch diffuse darkening. 
            # Lowering C from 1.5 to 0.5 to increase sensitivity.
            local_dark = cv2.adaptiveThreshold(roi_l, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                cv2.THRESH_BINARY_INV, 101, 0.5)
            
            # Filter detections by area and relative intensity
            contours, _ = cv2.findContours(local_dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                # Filter: Lowered area requirement from 10% to 2%
                if area < (ew * (roi_y2 - roi_y1)) * 0.02: 
                    continue
                
                x, y, bw, bh = cv2.boundingRect(cnt)
                
                # Global coordinates
                gx, gy = x + roi_x1, y + roi_y1
                
                # SPECIAL BYPASS: For dark circles, we ignore the dilated global exclusion mask
                # because it is too aggressive. We rely on the ROI and tight eye buffer instead.
                # Only check if it's deeply inside a hair exclusion (avoid sideburns).

                color_info = LESION_COLORS["dark_spot"]
                # Calculate confidence based on darkness relative to ROI average
                roi_mean = np.mean(roi_l)
                spot_mean = np.mean(roi_l[y:y+bh, x:x+bw])
                diff = roi_mean - spot_mean
                
                # Lowered from 2.0 to 0.5 to catch very faint circles
                if diff < 0.5: 
                    continue
                    
                confidence = min(0.95, 0.40 + (diff / 25.0) * 0.55)

                lesions.append({
                    "id": f"DC-{side}-{lesion_id}", # Dark Circle tag
                    "bbox": {"x1": int(gx), "y1": int(gy), "x2": int(gx + bw), "y2": int(gy + bh)},
                    "confidence": round(float(confidence), 2),
                    "type": "dark_spot",
                    "class_name": "dark_circle",
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
        Enhanced CV-based lesion detection with multiple detection strategies:
        1. Local adaptive redness detection (LAB a-channel)
        2. Dark spot detection (luminance anomalies)
        3. Saturation-based detection
        4. Texture/bump detection (Laplacian)
        5. Blob detection (SimpleBlobDetector) for small spots
        6. Difference of Gaussians for subtle marks
        """
        h, w = image.shape[:2]
        landmarks = face_data.get("landmarks", [])
        if not landmarks:
            return []

        # Create face mask from landmarks
        face_mask = self._create_face_mask(landmarks, w, h)

        # Original clinical-grade Face Oval landmarks
        # Dilation: Restored to 20px to ensure coverage of edge-pigments while filtering distant hair.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
        mask = cv2.dilate(mask, kernel)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)

        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        s_ch = hsv[:, :, 1]

        # ─── Stats on face skin only ───
        face_pixels = face_mask > 0
        if not np.any(face_pixels):
            return []

        mean_a = cv2.mean(a_ch, mask=face_mask)[0]
        std_a = max(np.std(a_ch[face_pixels]), 1.0)
        mean_l = cv2.mean(l_ch, mask=face_mask)[0]
        std_l = max(np.std(l_ch[face_pixels]), 1.0)
        mean_s = cv2.mean(s_ch, mask=face_mask)[0]
        std_s = max(np.std(s_ch[face_pixels]), 1.0)

        # ─── Method 1: Redness (lower threshold: from 1.2 to 0.7) ───
        red_thresh = mean_a + 0.7 * std_a
        red_mask = cv2.threshold(a_ch, int(red_thresh), 255, cv2.THRESH_BINARY)[1]
        red_mask = cv2.bitwise_and(red_mask, red_mask, mask=face_mask)

        # ─── Method 2: Local adaptive redness (catches local anomalies) ───
        a_blur = cv2.GaussianBlur(a_ch, (51, 51), 0)
        local_red_diff = cv2.subtract(a_ch, a_blur)
        local_red_mask = cv2.threshold(local_red_diff, 5, 255, cv2.THRESH_BINARY)[1] # From 12 to 5
        local_red_mask = cv2.bitwise_and(local_red_mask, local_red_mask, mask=face_mask)

        # ─── Method 3: Dark spots (pigmentation) ───
        dark_thresh = mean_l - 0.5 * std_l
        dark_mask = cv2.threshold(l_ch, int(max(dark_thresh, 15)), 255, cv2.THRESH_BINARY_INV)[1]
        dark_mask = cv2.bitwise_and(dark_mask, dark_mask, mask=face_mask)

        # ─── Method 4: Local dark spots (adaptive) ───
        l_blur = cv2.GaussianBlur(l_ch, (51, 51), 0)
        local_dark_diff = cv2.subtract(l_blur, l_ch)
        local_dark_mask = cv2.threshold(local_dark_diff, 4, 255, cv2.THRESH_BINARY)[1]
        local_dark_mask = cv2.bitwise_and(local_dark_mask, local_dark_mask, mask=face_mask)

        # ─── Method 5: High saturation ───
        sat_thresh = mean_s + 1.2 * std_s
        sat_mask = cv2.threshold(s_ch, int(min(sat_thresh, 200)), 255, cv2.THRESH_BINARY)[1]
        sat_mask = cv2.bitwise_and(sat_mask, sat_mask, mask=face_mask)

        # ─── Method 6: Texture variance (bumpy skin) ───
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_abs = np.abs(laplacian).astype(np.uint8)
        lap_mean = cv2.mean(laplacian_abs, mask=face_mask)[0]
        lap_std = max(np.std(laplacian_abs[face_pixels]), 1.0)
        texture_thresh = lap_mean + 1.5 * lap_std
        texture_mask = cv2.threshold(laplacian_abs, int(texture_thresh), 255, cv2.THRESH_BINARY)[1]
        texture_mask = cv2.bitwise_and(texture_mask, texture_mask, mask=face_mask)

        # ─── Method 7: Difference of Gaussians for subtle spots ───
        g1 = cv2.GaussianBlur(gray, (3, 3), 1.0)
        g2 = cv2.GaussianBlur(gray, (15, 15), 3.0)
        dog = cv2.absdiff(g1, g2)
        dog_thresh = np.mean(dog[face_pixels]) + 1.0 * np.std(dog[face_pixels])
        dog_mask = cv2.threshold(dog, int(dog_thresh), 255, cv2.THRESH_BINARY)[1]
        dog_mask = cv2.bitwise_and(dog_mask, dog_mask, mask=face_mask)

        # ─── Combine all detection masks ───
        combined = cv2.bitwise_or(red_mask, local_red_mask)
        combined = cv2.bitwise_or(combined, dark_mask)
        combined = cv2.bitwise_or(combined, local_dark_mask)
        combined = cv2.bitwise_or(combined, sat_mask)
        combined = cv2.bitwise_or(combined, texture_mask)
        combined = cv2.bitwise_or(combined, dog_mask)

        # Morphological cleanup — minimal to preserve small spots
        # Close gaps in nearby detections without eroding tiny spots
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel_close)

        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        lesions = []
        lesion_id = 1
        min_area = (w * h) * 0.000005  # Extremely small min to catch tiny moles/freckles
        max_area = (w * h) * 0.06

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

            # Classification logic — sensitive thresholds (lowered from 0.4 to 0.2)
            if mean_roi_a > mean_a + 0.2 * std_a:
                lesion_type = "inflammatory"
            elif mean_roi_l < mean_l - 0.3 * std_l:
                lesion_type = "comedonal"
            elif mean_roi_s > mean_s + 0.4 * std_s:
                lesion_type = "other"
            else:
                lesion_type = "other"

            color_info = LESION_COLORS[lesion_type]
            confidence = min(0.95, 0.45 + (abs(mean_roi_a - mean_a) / (2.5 * std_a + 0.01)))

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

    def _merge_detections(self, primary: list, secondary: list) -> list:
        """
        Merge secondary detections into primary list, skipping any that
        overlap significantly (IoU > 0.3) with existing detections.
        """
        if not primary:
            return secondary
        if not secondary:
            return primary

        merged = list(primary)

        for sec in secondary:
            sb = sec["bbox"]
            overlaps = False
            for pri in merged:
                pb = pri["bbox"]
                # Compute IoU
                ix1 = max(sb["x1"], pb["x1"])
                iy1 = max(sb["y1"], pb["y1"])
                ix2 = min(sb["x2"], pb["x2"])
                iy2 = min(sb["y2"], pb["y2"])
                if ix2 > ix1 and iy2 > iy1:
                    inter = (ix2 - ix1) * (iy2 - iy1)
                    area_s = (sb["x2"] - sb["x1"]) * (sb["y2"] - sb["y1"])
                    area_p = (pb["x2"] - pb["x1"]) * (pb["y2"] - pb["y1"])
                    union = area_s + area_p - inter
                    # NUCLEAR MERGE: If CV detection is significantly larger than YOLO detection,
                    # KEEP BOTH (don't set overlaps=True), allowing the "area" to show up around the "spot".
                    primary_area = (pb["x2"] - pb["x1"]) * (pb["y2"] - pb["y1"])
                    secondary_area = (sb["x2"] - sb["x1"]) * (sb["y2"] - sb["y1"])
                    
                    if union > 0 and inter / union > 0.1:
                        # CRITICAL BUG FIX: If CV detected "inflammatory/dark_spot" but YOLO detected "comedonal",
                        # we must keep the CV box so the user knows it's inflamed!
                        if sec["type"] != pri["type"]:
                            continue
                            
                        # Only skip if the boxes are similar in size and SAME type.
                        # If CV box is 4x larger than YOLO box, show it as an "area" box.
                        if secondary_area < primary_area * 4.0:
                            overlaps = True
                            break
            if not overlaps:
                merged.append(sec)

        # Hard Diagnostic: DO NOT re-number or change IDs.
        return merged

        return merged

    def _build_exclusion_mask(self, landmarks: list, w: int, h: int, tight: bool = False) -> np.ndarray:
        """
        Build a binary mask of anatomical regions that should NOT be
        flagged as lesions (lips, eyes, eyebrows).
        If tight=True, uses minimal padding to avoid masking closely-adjacent skin (like under-eyes).
        """
        mask = np.zeros((h, w), dtype=np.uint8)
        if not landmarks:
            return mask

        def _fill_region(indices, dilate_px=10):
            pts = []
            for idx in indices:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    pts.append([int(lm["x"] * w), int(lm["y"] * h)])
            if len(pts) >= 3:
                poly = np.array(pts, dtype=np.int32)
                cv2.fillPoly(mask, [poly], 255)
                # Dilate slightly to cover edges
                if dilate_px > 0:
                    kernel = cv2.getStructuringElement(
                        cv2.MORPH_ELLIPSE, (dilate_px * 2, dilate_px * 2)
                    )
                    cv2.dilate(mask, kernel, dst=mask)

        lip_pad = 1 if tight else 12     # Minimized to 1px for high-precision
        eye_pad = 1 if tight else 20     # Minimized to 1px for high-precision
        brow_pad = 5 if tight else 20    # Reduced brow padding too in tight mode
        nose_pad = 5 if tight else 15    # Critical for profile: nose tip padding reduced from 10 to 5

        # Exclude lip region
        _fill_region(LIP_OUTER_INDICES, dilate_px=lip_pad)
        # Exclude eye regions
        _fill_region(LEFT_EYE_INDICES, dilate_px=eye_pad)
        _fill_region(RIGHT_EYE_INDICES, dilate_px=eye_pad)
        # Exclude eyebrows
        _fill_region(LEFT_EYEBROW_INDICES, dilate_px=brow_pad)
        _fill_region(RIGHT_EYEBROW_INDICES, dilate_px=brow_pad)
        # Exclude nose tip and nostril region
        _fill_region(NOSE_TIP_INDICES, dilate_px=nose_pad)
        # Exclude mustache region (reduced padding for profile safety)
        _fill_region(MUSTACHE_INDICES, dilate_px=2)
        # [DISABLED] Hairline/temple exclusion creates massive tangled polygons across the cheek on profile faces!
        # _fill_region(HAIRLINE_INDICES, dilate_px=20)

        return mask

    def _filter_exclusion_zones(self, lesions: list, exclusion_mask: np.ndarray) -> list:
        """
        Filter out lesions whose center points fall within the semantic exclusion mask.
        """
        if exclusion_mask is None:
            return lesions
            
        filtered = []
        h, w = exclusion_mask.shape[:2]
        
        for lesion in lesions:
            b = lesion["bbox"]
            cx = (b["x1"] + b["x2"]) // 2
            cy = (b["y1"] + b["y2"]) // 2
            
            # Clamp to bounds
            cx = max(0, min(cx, w - 1))
            cy = max(0, min(cy, h - 1))
            
            # Mask > 0 indicates an exclusion zone (lip, eye, eyebrow, etc.)
            if exclusion_mask[cy, cx] == 0:
                filtered.append(lesion)
                
        return filtered

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
            # Use fillPoly instead of fillConvexPoly to support non-convex profile face shapes
            cv2.fillPoly(mask, [pts], 255)
            
            # Diagnostic: REMOVED DILATION to prevent hairline bleeding.
            # Minimal 1px dilation just to close sub-pixel gaps.
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
            mask = cv2.dilate(mask, kernel)

        return mask

    def _create_zones_mask(self, face_data: dict, w: int, h: int) -> np.ndarray:
        """Create a combined mask of all defined facial zones."""
        mask = np.zeros((h, w), dtype=np.uint8)
        zones = face_data.get("zones", {})
        
        if not zones:
            # Fallback: if no zones, return full white mask (no restriction)
            return np.ones((h, w), dtype=np.uint8) * 255

        for zone_name, zone_info in zones.items():
            points = zone_info.get("points", [])
            if points:
                poly = np.array([[p["x"], p["y"]] for p in points], dtype=np.int32)
                cv2.fillPoly(mask, [poly], 255)
        
        # Restore 40px dilation to ensure "jagged" default zones are fused into solid blocks.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
        mask = cv2.dilate(mask, kernel)
        
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

        # Lesion Count Buckets (Client Requirement: 0-2, 3-5, 5-10, 11-15, 15+)
        if count <= 2:
            count_label = "0-2"
        elif count <= 5:
            count_label = "3-5"
        elif count <= 10:
            count_label = "5-10"
        elif count <= 15:
            count_label = "11-15"
        else:
            count_label = "15+"

        return {
            "grade": grade,
            "score": min(score, 100),
            "total_lesions": count,
            "count_label": count_label,
            "inflammatory_count": inflammatory_count,
            "comedonal_count": sum(1 for l in lesions if l["type"] == "comedonal"),
            "dark_spot_count": sum(1 for l in lesions if l["type"] == "dark_spot"),
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

            # Calculate centroid for label placement
            if points:
                cx_label = int(sum(p["x"] for p in points) / len(points))
                cy_label = int(sum(p["y"] for p in points) / len(points))
            else:
                cx_label, cy_label = 0, 0

            zone_health[zone_name] = {
                "display_name": zone_info.get("display_name", zone_name.replace("_", " ").capitalize()),
                "affected": affected,
                "severity": severity,
                "lesion_count": zone_lesions,
                "points": points,
                "centroid": {"x": cx_label, "y": cy_label},
                "description": f"{severity.capitalize()} — {zone_lesions} lesion(s) detected",
            }

        return zone_health

    def _build_hair_mask(self, image: np.ndarray, face_mask: np.ndarray) -> np.ndarray:
        """Create a mask of facial hair (beard, mustache) using texture and saturation."""
        if not np.any(face_mask):
            return np.zeros(image.shape[:2], dtype=np.uint8)

        # Texture/Hair mask to exclude facial hair
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_abs = np.abs(laplacian).astype(np.uint8)
        tex_blur = cv2.GaussianBlur(lap_abs, (15, 15), 0)

        mean_tex = cv2.mean(tex_blur, mask=face_mask)[0]
        std_tex = np.std(tex_blur[face_mask > 0]) if np.any(face_mask > 0) else 1

        # High texture Regions (Hair). More aggressive (2.2 * std instead of 3.5)
        # to ensure forehead hairline and fine beard hairs are caught.
        hair_thresh = mean_tex + 2.2 * std_tex
        hair_mask = cv2.threshold(tex_blur, int(max(hair_thresh, 45)), 255, cv2.THRESH_BINARY)[1]

        # Thick, dense beards might be smooth, but they are very LOW SATURATION compared to skin pigment
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        s_ch = hsv[:, :, 1]
        mean_s = cv2.mean(s_ch, mask=face_mask)[0]
        std_s = max(np.std(s_ch[face_mask > 0]), 1.0)

        # Hair is also fundamentally very dark
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_ch = lab[:, :, 0]
        mean_l = cv2.mean(l_ch, mask=face_mask)[0]
        std_l = max(np.std(l_ch[face_mask > 0]), 1.0)
        
        # Desaturated AND dark areas = hair (melanin is saturated, normal shadows aren't desaturated)
        # More conservative color masking (loosen saturation and brightness thresholds)
        low_sat_thresh = mean_s - 0.4 * std_s
        dark_thresh = mean_l - 0.8 * std_l
        
        hair_color_mask = np.zeros_like(s_ch)
        hair_color_mask[(s_ch < low_sat_thresh) & (l_ch < dark_thresh)] = 255
        
        # Combine texture and color to perfectly mask beards
        hair_mask = cv2.bitwise_or(hair_mask, hair_color_mask)
        return hair_mask

    def _detect_hyperpigmentation(self, image: np.ndarray, face_data: dict) -> dict:
        """Detect hyperpigmented regions on the face."""
        h, w = image.shape[:2]
        landmarks = face_data.get("landmarks", [])
        if not landmarks:
            return {"coverage_pct": 0, "coverage_bucket": "0-10%", "regions": [], "mask": None}

        # Build the "Sanctuary Mask": Face Mesh Oval INTERSECT Clinical Zones
        # This prevents hyperpigmentation detection in hair, background, or clothing.
        face_oval_mask = self._create_face_mask(landmarks, w, h)
        # Base face detection mask for stats and detection
        face_mask = self._create_face_mask(landmarks, w, h)

        # Anatomical exclusions
        exclusion_mask = self._build_exclusion_mask(landmarks, w, h, tight=True)

        # Hair mask 
        hair_mask = self._build_hair_mask(image, face_mask)
        hair_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        hair_mask_dilated = cv2.dilate(hair_mask, hair_kernel)

        # Clear, valid skin mask
        valid_skin_mask = face_mask.copy()
        valid_skin_mask[exclusion_mask > 0] = 0
        valid_skin_mask[hair_mask_dilated > 0] = 0

        # Convert to LAB
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_ch = lab[:, :, 0]

        # Get skin luminance stats strictly from valid clear skin
        skin_pixels = l_ch[valid_skin_mask > 0]
        if len(skin_pixels) == 0:
            return {"coverage_pct": 0, "coverage_bucket": "0-10%", "regions": [], "mask": None}

        mean_l = np.mean(skin_pixels)
        std_l = np.std(skin_pixels)

        # Dark spots = significantly darker than valid average skin
        dark_threshold = mean_l - 0.6 * std_l
        dark_mask = np.zeros_like(l_ch)
        dark_mask[(l_ch < dark_threshold) & (valid_skin_mask > 0)] = 255

        # ADDITIONAL: Local Periorbital (Eye) sensing for hyperpigmentation regions
        eye_bottom_indices = {
            "left": [145, 153, 154, 155],
            "right": [374, 380, 381, 382]
        }
        for side, indices in eye_bottom_indices.items():
            pts = []
            for idx in indices:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    pts.append([int(lm["x"] * w), int(lm["y"] * h)])
            if pts:
                pts_arr = np.array(pts, dtype=np.int32)
                ex, ey, ew, eh = cv2.boundingRect(pts_arr)
                # ROI: Standard eye-bag depth (15% of face height)
                ry1, ry2 = ey, min(h - 1, ey + int(h * 0.15))
                rx1, rx2 = ex, ex + ew
                
                roi_l = l_ch[ry1:ry2, rx1:rx2]
                if roi_l.size > 0:
                    local_dark = cv2.adaptiveThreshold(roi_l, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                        cv2.THRESH_BINARY_INV, 251, -0.5)
                    # Merge directly into mask
                    dark_mask[ry1:ry2, rx1:rx2] = cv2.bitwise_or(dark_mask[ry1:ry2, rx1:rx2], local_dark)

        # Morphological cleanup
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_open)
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel_close)

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
            if area < (w * h) * 0.0005:  
                continue
            if area > (w * h) * 0.03:    # Skip massive regions
                continue
            
            # --- Centroid Safety Check for Mouth ---
            danger_indices = [61, 291, 164, 0]
            danger_pts = []
            for idx in danger_indices:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    danger_pts.append([int(lm["x"] * w), int(lm["y"] * h)])
            
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                if danger_pts:
                    mouth_nose_y = sum(p[1] for p in danger_pts) / len(danger_pts)
                    mouth_nose_x = sum(p[0] for p in danger_pts) / len(danger_pts)
                    dist = np.sqrt((cx - mouth_nose_x)**2 + (cy - mouth_nose_y)**2)
                    if dist < 60:
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

    def _create_skin_mask(self, image: np.ndarray) -> np.ndarray:
        """
        Identify skin-colored pixels using HSV and LAB color spaces.
        Provides a robust scan area for profile views where landmarks might fail.
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # HSV skin range (Calibrated Precision-Tuning)
        lower_hsv = np.array([0, 20, 70], dtype=np.uint8)
        upper_hsv = np.array([25, 255, 255], dtype=np.uint8)
        mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)
        
        # LAB skin range (Calibrated)
        lower_lab = np.array([0, 133, 133], dtype=np.uint8)
        upper_lab = np.array([255, 173, 173], dtype=np.uint8)
        mask_lab = cv2.inRange(lab, lower_lab, upper_lab)
        
        # Combine masks
        skin_mask = cv2.bitwise_and(mask_hsv, mask_lab)
        
        # Cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        skin_mask = cv2.dilate(skin_mask, kernel, iterations=2)
        
        return skin_mask

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
