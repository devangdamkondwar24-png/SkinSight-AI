
import cv2
import numpy as np
import sys
import os
from pathlib import Path

# Add the backend directory to sys.path
backend_dir = Path("c:/Users/darsh/OneDrive/Desktop/hackathon/win/backend")
sys.path.append(str(backend_dir))

from services.skin_analyzer import SkinAnalyzer
from services.face_mesh import FaceMeshService

def check_mask():
    analyzer = SkinAnalyzer()
    mesh_service = FaceMeshService()
    
    # Use the acne-intake image as it's a real photo
    img_path = Path("c:/Users/darsh/OneDrive/Desktop/hackathon/win/frontend/public/acne-intake.png")
    if not img_path.exists():
        print("Test image not found.")
        return
        
    image = cv2.imread(str(img_path))
    h, w = image.shape[:2]
    
    face_data = mesh_service.process(image)
    if not face_data["detected"]:
        print("Face NOT detected by MediaPipe on this image.")
        return
        
    face_mask = analyzer._create_face_mask(face_data["landmarks"], w, h)
    
    # Calculate coverage of the image
    mask_area = np.sum(face_mask > 0)
    total_area = w * h
    coverage = (mask_area / total_area) * 100
    
    print(f"Face Mask Coverage: {coverage:.2f}%")
    
    # Check if a specific point (the cheek) is covered. 
    # Usually cheeks are around x=0.3-0.7, y=0.5
    cheek_points = [(int(w*0.3), int(h*0.5)), (int(w*0.7), int(h*0.5)), (int(w*0.5), int(h*0.7))]
    for i, p in enumerate(cheek_points):
        covered = face_mask[p[1], p[0]] > 0
        print(f"Cheek Point {i} at {p}: {'Covered' if covered else 'MISSING'}")

if __name__ == "__main__":
    check_mask()
