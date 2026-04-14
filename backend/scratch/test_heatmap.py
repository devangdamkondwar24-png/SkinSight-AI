import cv2
import numpy as np
import base64
import sys
import os

# Add services to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.heatmap import generate_heatmap

def test_heatmap():
    print("Testing Heatmap Generation...")
    
    # Mock image (1000x1000)
    img = np.zeros((1000, 1000, 3), dtype=np.uint8)
    
    # Mock lesions
    lesions = [
        {"bbox": {"x1": 450, "y1": 450, "x2": 550, "y2": 550}, "type": "inflammatory"}
    ]
    
    # Mock zone health
    zone_health = {
        "Forehead": {"affected": True, "severity": "moderate", "points": [{"x": 100, "y": 100}, {"x": 200, "y": 100}]}
    }
    
    # Mock hyperpigmentation (The new part)
    hyperpigmentation = {
        "regions": [
            {
                "points": [
                    {"x": 600, "y": 600}, {"x": 700, "y": 600}, 
                    {"x": 700, "y": 700}, {"x": 600, "y": 700}
                ]
            }
        ]
    }
    
    result = generate_heatmap(img, lesions, zone_health, hyperpigmentation)
    
    if result["image_base64"]:
        print(f"[OK] Generated Heatmap (Base64 length: {len(result['image_base64'])})")
        print(f"Max Density: {result['max_density']}")
        
        # Save for manual check if needed
        # img_data = base64.b64decode(result["image_base64"])
        # with open("scratch/heatmap_result.png", "wb") as f:
        #     f.write(img_data)
        # print("Saved to scratch/heatmap_result.png")
    else:
        print("[FAIL] Heatmap generation failed")

if __name__ == "__main__":
    test_heatmap()
