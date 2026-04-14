import cv2
import numpy as np

class HealingSynthesizer:
    """
    Generates realistic healed facial images using OpenCV Inpainting.
    Completely local and free (no generative API costs).
    """

    @staticmethod
    def synthesize(image: np.ndarray, lesions: list, feature_masks: dict = None) -> dict:
        """
        Synthesize Short-Term and Long-Term healing progressions with Anatomical Shielding.
        
        Args:
            image: Original camera image (BGR numpy array)
            lesions: List of detected lesion dictionaries
            feature_masks: Optional dict containing landmark sequences for 'eye_left', 'eye_right', 'lips'
            
        Returns:
            dict containing numpy arrays for 'short_term' and 'long_term'
        """
        if not lesions or image is None:
            return {"short_term": image, "long_term": image}

        h, w = image.shape[:2]
        
        # 1. Create independent masks for inpainting
        mild_mask = np.zeros((h, w), dtype=np.uint8)
        severe_mask = np.zeros((h, w), dtype=np.uint8)

        # 2. Create the Anatomical Guard (Protects eyes/lips from blurring)
        guard_mask = np.ones((h, w), dtype=np.uint8) * 255 # White = Allowed to heal
        if feature_masks:
            for feature in ["eye_left", "eye_right", "lips"]:
                points = feature_masks.get(feature)
                if points:
                    pts = np.array([[int(p["x"] * w), int(p["y"] * h)] for p in points], dtype=np.int32)
                    # Use convex hull to ensure the whole feature area is shielded
                    hull = cv2.convexHull(pts)
                    cv2.fillPoly(guard_mask, [hull], 0) # Black = PROTECTED
        
        # Process lesions and bake them into the masks
        for lesion in lesions:
            bbox = lesion["bbox"]
            x1, y1 = max(0, bbox["x1"]), max(0, bbox["y1"])
            x2, y2 = min(w, bbox["x2"]), min(h, bbox["y2"])
            
            width_bbox = x2 - x1
            height_bbox = y2 - y1
            area = width_bbox * height_bbox
            
            if area > 15000 or width_bbox <= 0 or height_bbox <= 0:
                continue
            
            # Extremely tight padding
            pad_x = min(2, int(width_bbox * 0.15))
            pad_y = min(2, int(height_bbox * 0.15))
            
            center_x = x1 + width_bbox // 2
            center_y = y1 + height_bbox // 2
            axes = (width_bbox // 2 + pad_x, height_bbox // 2 + pad_y)

            if lesion["type"] in ["comedonal", "other"]:
                cv2.ellipse(mild_mask, (center_x, center_y), axes, 0, 0, 360, 255, -1)
            else:
                cv2.ellipse(severe_mask, (center_x, center_y), axes, 0, 0, 360, 255, -1)

        # 3. Apply Anatomical Shielding: Subtract guarded areas from inpaint masks
        mild_mask = cv2.bitwise_and(mild_mask, guard_mask)
        severe_mask = cv2.bitwise_and(severe_mask, guard_mask)

        # Apply a mild gaussian blur to feather the mask edges realistically
        mild_mask = cv2.GaussianBlur(mild_mask, (3, 3), 0)
        severe_mask = cv2.GaussianBlur(severe_mask, (3, 3), 0)

        # ---------------------------------------------------------
        # SHORT TERM SYNTHESIS (2-4 Weeks)
        # ---------------------------------------------------------
        # Remove mild lesions completely using extremely tight radius
        short_term = cv2.inpaint(image, mild_mask, 2, cv2.INPAINT_TELEA)

        # For severe lesions, gently inpaint and blend
        full_healed_severe = cv2.inpaint(short_term, severe_mask, 2, cv2.INPAINT_TELEA)
        # Blend 50% healed to look natural without structural distortion
        short_term = cv2.addWeighted(full_healed_severe, 0.50, short_term, 0.50, 0)
        
        # ---------------------------------------------------------
        # LONG TERM SYNTHESIS (8-12 Weeks)
        # ---------------------------------------------------------
        # Remove ALL lesions completely using standard 3px radius
        combined_mask = cv2.bitwise_or(mild_mask, severe_mask)
        long_term = cv2.inpaint(image, combined_mask, 3, cv2.INPAINT_TELEA)

        # Apply very subtle bilateral filter to simulate the "cleared skin glow"
        long_term = cv2.bilateralFilter(long_term, d=5, sigmaColor=25, sigmaSpace=25)
        
        # Subtle brightness/contrast bump for the final healed result directly in the pixel data
        long_term = cv2.convertScaleAbs(long_term, alpha=1.01, beta=2)

        # ---------------------------------------------------------
        # FINAL ANATOMICAL RESTORE (The "Pixel-Perfect" Pass)
        # ---------------------------------------------------------
        # Physically paste the ORIGINAL eyes and lips back onto the result
        # This guarantees 100% sharp features regardless of any skin filters applied above.
        if feature_masks:
            # Broadcast mask to 3 channels for image selection
            mask_3ch = cv2.merge([guard_mask, guard_mask, guard_mask])
            
            # Where mask is 0 (protected), use ORIGINAL image. Where 255 (allowed), use synthesized.
            short_term = np.where(mask_3ch == 0, image, short_term)
            long_term = np.where(mask_3ch == 0, image, long_term)

        return {
            "short_term": short_term.astype(np.uint8),
            "long_term": long_term.astype(np.uint8)
        }
