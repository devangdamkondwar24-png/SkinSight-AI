"""
Heatmap Service

Generates lesion density heatmap overlay by accumulating
Gaussian blobs at each lesion center point.
"""

import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image


def generate_heatmap(image: np.ndarray, lesions: list, zone_health: dict, hyperpigmentation: dict = None) -> dict:
    """
    Generate a lesion density heatmap overlay.

    Args:
        image: Original BGR image
        lesions: List of detected lesions with bboxes
        zone_health: Dict of zone assessments
        hyperpigmentation: Optional dict of pigmented regions

    Returns:
        dict with base64-encoded heatmap image and metadata
    """
    h, w = image.shape[:2]
    heatmap = np.zeros((h, w), dtype=np.float32)

    if not lesions:
        # Return blank heatmap
        return _encode_heatmap(heatmap, w, h)

    # Accumulate Gaussian blobs at each lesion center
    for lesion in lesions:
        bbox = lesion["bbox"]
        cx = (bbox["x1"] + bbox["x2"]) // 2
        cy = (bbox["y1"] + bbox["y2"]) // 2
        bw = bbox["x2"] - bbox["x1"]
        bh = bbox["y2"] - bbox["y1"]

        # Sigma proportional to lesion size
        sigma = max(bw, bh) * 1.5

        # Weight by lesion type
        weight = 1.0
        if lesion.get("type") == "inflammatory":
            weight = 1.5
        elif lesion.get("type") == "comedonal":
            weight = 0.8

        # Add Gaussian blob
        _add_gaussian(heatmap, cx, cy, sigma, weight)

    # Also add subtle density for affected zones
    for zone_name, zone_info in zone_health.items():
        if zone_info.get("affected"):
            severity_weight = {"mild": 0.3, "moderate": 0.6, "severe": 1.0}
            weight = severity_weight.get(zone_info.get("severity", "clear"), 0)
            if weight > 0 and zone_info.get("points"):
                points = zone_info["points"]
                # Increased spread for zone-based density
                for p in points[::2]:  # Sample more points
                    _add_gaussian(heatmap, p["x"], p["y"], 60, weight * 0.4)

    # NEW: Add high density for pigmented regions (Dark Circles, Spots)
    if hyperpigmentation and "regions" in hyperpigmentation:
        for region in hyperpigmentation["regions"]:
            points = region.get("points", [])
            if points:
                # Accumulate density within the region
                # Sample points to spread density across the whole region
                sample_step = max(1, len(points) // 10)
                for p in points[::sample_step]:
                    _add_gaussian(heatmap, p["x"], p["y"], 80, 0.8)

    return _encode_heatmap(heatmap, w, h)


def _add_gaussian(heatmap: np.ndarray, cx: int, cy: int, sigma: float, weight: float):
    """Add a weighted Gaussian blob to the heatmap."""
    h, w = heatmap.shape
    sigma = max(sigma, 10)

    # Compute bounding box for the Gaussian
    size = int(3 * sigma)
    x1 = max(0, cx - size)
    y1 = max(0, cy - size)
    x2 = min(w, cx + size)
    y2 = min(h, cy + size)

    if x2 <= x1 or y2 <= y1:
        return

    # Create grid
    yy, xx = np.mgrid[y1:y2, x1:x2]
    gaussian = weight * np.exp(-((xx - cx)**2 + (yy - cy)**2) / (2 * sigma**2))
    heatmap[y1:y2, x1:x2] += gaussian.astype(np.float32)


def _encode_heatmap(heatmap: np.ndarray, w: int, h: int) -> dict:
    """Normalize and encode heatmap as base64 RGBA image."""
    # Normalize to 0-255
    max_val = heatmap.max()
    if max_val > 0:
        heatmap_norm = (heatmap / max_val * 255).astype(np.uint8)
    else:
        heatmap_norm = np.zeros((h, w), dtype=np.uint8)

    # Apply colormap (JET for heat visualization)
    colored = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)

    # Create RGBA with alpha based on intensity
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = colored[:, :, ::-1]  # BGR -> RGB
    # Higher alpha multiplier (0.8 instead of 0.6) for visibility
    rgba[:, :, 3] = (heatmap_norm * 0.8).astype(np.uint8) 

    # Encode to base64
    img = Image.fromarray(rgba, "RGBA")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "image_base64": b64,
        "max_density": float(max_val) if max_val > 0 else 0,
        "width": w,
        "height": h,
    }
