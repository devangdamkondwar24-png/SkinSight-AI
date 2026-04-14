
import cv2
import numpy as np
import sys
from pathlib import Path

# Add the backend directory to sys.path
backend_dir = Path("c:/Users/darsh/OneDrive/Desktop/hackathon/win/backend")
sys.path.append(str(backend_dir))

from services.skin_analyzer import SkinAnalyzer

def debug_detection():
    analyzer = SkinAnalyzer()
    
    # Create a synthetic image with a red spot
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[:, :] = [100, 100, 100] # Grey background
    cv2.circle(img, (150, 150), 20, [0, 0, 255], -1) # Red spot
    
    # Mock face_data
    face_data = {"landmarks": [{"x": 0.1, "y": 0.1}, {"x": 0.9, "y": 0.1}, {"x": 0.9, "y": 0.9}, {"x": 0.1, "y": 0.9}]}
    
    # Test _detect_inflammatory_marks
    try:
        results = analyzer._detect_inflammatory_marks(img, face_data)
        print(f"Results count: {len(results)}")
        if len(results) == 0:
            print("FAILED to detect inflammatory marks in synthetic image.")
            
            # Step-by-step debug inside the logic
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            a_ch = lab[:, :, 1]
            print(f"a_ch mean: {np.mean(a_ch)}")
            print(f"a_ch max: {np.max(a_ch)}")
            
            skin_mask = analyzer._create_skin_mask(img)
            print(f"skin_mask sum: {np.sum(skin_mask)}")
            
            if not np.any(skin_mask):
                 print("Skin mask is EMPTY for synthetic image.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_detection()
