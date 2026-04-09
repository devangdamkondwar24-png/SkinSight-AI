"""
SkinSight AI — FastAPI Backend Server

Main entry point for the skin health analysis API.
Handles image upload, orchestrates the analysis pipeline,
and returns structured JSON results.
"""

import base64
import io
import time
import traceback

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from services.face_mesh import FaceMeshService
from services.skin_analyzer import SkinAnalyzer
from services.heatmap import generate_heatmap
from services.recommendations import generate_recommendations
from services.progress import generate_progress

# ─── Initialize App ───
app = FastAPI(
    title="SkinSight AI",
    description="AI-Powered Facial Skin Health Screening Tool",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Initialize Services ───
print("\n" + "="*60)
print("  SkinSight AI - Initializing Services")
print("="*60)

face_mesh_service = FaceMeshService()
print("  [OK] Face Mesh Service loaded")

skin_analyzer = SkinAnalyzer()
print("  [OK] Skin Analyzer loaded")

print("="*60 + "\n")


# ─── Preprocessing ───
def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Apply preprocessing for diverse skin tones and lighting.
    Uses CLAHE (Contrast Limited Adaptive Histogram Equalization).
    """
    # Convert to LAB
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)

    # Apply CLAHE to luminance channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_ch)

    # Merge and convert back
    enhanced = cv2.merge([l_enhanced, a_ch, b_ch])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    # Subtle bilateral filter to reduce noise while preserving edges
    enhanced = cv2.bilateralFilter(enhanced, 5, 50, 50)

    return enhanced


# ─── Routes ───
@app.get("/")
async def root():
    return {"status": "ok", "service": "SkinSight AI", "version": "1.0.0"}


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "face_mesh": True,
            "skin_analyzer": True,
            "yolo_model": skin_analyzer.yolo_model is not None,
        }
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Main analysis endpoint.
    Accepts a face image and returns comprehensive skin health report.
    """
    start = time.time()

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image file (jpg, png, webp)")

    try:
        # Read and decode image
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Resize if too large (max 1280px on longest side)
        max_dim = 1280
        w, h = pil_image.size
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            pil_image = pil_image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        # Convert to OpenCV format
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # Preprocess for lighting/skin tone robustness
        processed = preprocess_image(image)

        # Step 1: Face Mesh extraction
        face_data = face_mesh_service.process(processed)
        if not face_data["detected"]:
            return JSONResponse(status_code=200, content={
                "success": False,
                "error": "No face detected in the image. Please upload a clear, front-facing photo.",
                "processing_time": round(time.time() - start, 2),
            })

        # Step 2: Skin analysis (acne, lesions, zones, pigmentation)
        analysis = skin_analyzer.analyze(processed, face_data)

        # Step 3: Generate heatmap overlay
        heatmap = generate_heatmap(processed, analysis["lesions"], analysis["zone_health"])

        # Step 4: Generate recommendations
        recommendations = generate_recommendations(analysis)

        # Step 5: Generate progress projections
        progress = generate_progress(analysis)

        # Step 6: Encode original image as base64 for frontend overlay
        _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        image_b64 = base64.b64encode(buffer).decode("utf-8")

        processing_time = round(time.time() - start, 2)

        return JSONResponse(content={
            "success": True,
            "processing_time": processing_time,
            "image": {
                "base64": image_b64,
                "width": image.shape[1],
                "height": image.shape[0],
            },
            "face_mesh": {
                "landmarks": face_data["landmarks"],
                "connections": face_data["connections"],
            },
            "analysis": {
                "acne_severity": analysis["acne_severity"],
                "lesions": analysis["lesions"],
                "lesion_count": analysis["lesion_count"],
                "lesion_count_bucket": analysis["lesion_count_bucket"],
                "zone_health": analysis["zone_health"],
                "hyperpigmentation": analysis["hyperpigmentation"],
            },
            "heatmap": heatmap,
            "recommendations": recommendations,
            "progress": progress,
        })

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"Analysis failed: {str(e)}")


# ─── Run ───
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
