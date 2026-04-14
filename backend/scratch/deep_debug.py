
import cv2
import numpy as np
import sys
from pathlib import Path

# Add the backend directory to sys.path
backend_dir = Path("c:/Users/darsh/OneDrive/Desktop/hackathon/win/backend")
sys.path.append(str(backend_dir))

from services.skin_analyzer import SkinAnalyzer

def deep_debug():
    analyzer = SkinAnalyzer()
    
    # Red spot on grey
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[:, :] = [100, 100, 100]
    cv2.circle(img, (100, 100), 10, [50, 50, 250], -1) # BGR Red
    
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    a_ch = lab[:, :, 1]
    
    # Face mesh landmarks mock
    landmarks = [{"x": 0.1, "y": 0.1}, {"x": 0.9, "y": 0.1}, {"x": 0.9, "y": 0.9}, {"x": 0.1, "y": 0.9}]
    face_data = {"landmarks": landmarks, "detected": True}
    
    # Execute detection
    results = analyzer._detect_inflammatory_marks(img, face_data)
    print(f"Final results count: {len(results)}")
    
    # Manual step execution to see where it fails
    h, w = img.shape[:2]
    face_mask = analyzer._create_face_mask(landmarks, w, h)
    skin_mask = analyzer._create_skin_mask(img)
    coverage_mask = cv2.bitwise_or(face_mask, skin_mask)
    if not np.any(coverage_mask): coverage_mask = face_mask
    if not np.any(coverage_mask): coverage_mask = np.ones((h, w), dtype=np.uint8) * 255
    
    print(f"Coverage Mask Pixels: {np.sum(coverage_mask > 0)}")
    
    abs_red_mask = cv2.threshold(a_ch, 145, 255, cv2.THRESH_BINARY)[1]
    print(f"Absolute Red Pixels: {np.sum(abs_red_mask > 0)}")
    
    mean_a = cv2.mean(a_ch, mask=coverage_mask)[0]
    std_a = np.std(a_ch[coverage_mask > 0])
    red_thresh = mean_a + 0.05 * std_a
    red_mask = cv2.threshold(a_ch, int(red_thresh), 255, cv2.THRESH_BINARY)[1]
    print(f"Global Red Pixels: {np.sum(red_mask > 0)}")
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat_mask = cv2.threshold(hsv[:, :, 1], 15, 255, cv2.THRESH_BINARY)[1]
    print(f"Saturation Mask Pixels: {np.sum(sat_mask > 0)}")
    
    a_float = a_ch.astype(np.float32)
    a_blur = cv2.GaussianBlur(a_float, (101, 101), 0)
    a_norm = cv2.subtract(a_float, a_blur)
    a_norm = cv2.normalize(a_norm, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    local_mask = cv2.threshold(a_norm, 40, 255, cv2.THRESH_BINARY)[1]
    print(f"Local Contrast Mask Pixels: {np.sum(local_mask > 0)}")

if __name__ == "__main__":
    deep_debug()
