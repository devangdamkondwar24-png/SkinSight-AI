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
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from database import get_db
from PIL import Image

from services.face_mesh import FaceMeshService
from services.skin_analyzer import SkinAnalyzer
from services.heatmap import generate_heatmap
from services.recommendations import generate_recommendations
from services.progress import generate_progress
from services.progression_service import progression_service
from services.auth_service import auth_service
from services.image_synthesis import HealingSynthesizer
from pydantic import BaseModel

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
async def analyze(file: UploadFile = File(...), phone: str = Form(None)):
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
        # Use ORIGINAL image for detection (bilateral filter smooths out acne spots)
        analysis = skin_analyzer.analyze(image, face_data)

        # Step 3: Generate heatmap overlay
        heatmap = generate_heatmap(processed, analysis["lesions"], analysis["zone_health"], analysis["hyperpigmentation"])

        # Step 4: Generate recommendations
        recommendations = generate_recommendations(analysis)

        # Step 5: Generate progress projections
        progress = generate_progress(analysis)

        # Step 6: Generate Healing Synthesized Images with Anatomical Protection
        synthesized = HealingSynthesizer.synthesize(image, analysis["lesions"], face_data.get("feature_masks"))

        # Step 7: Encode all images to base64
        _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        image_b64 = base64.b64encode(buffer).decode("utf-8")
        
        _, buffer_st = cv2.imencode(".jpg", synthesized["short_term"], [cv2.IMWRITE_JPEG_QUALITY, 85])
        st_b64 = base64.b64encode(buffer_st).decode("utf-8")
        
        _, buffer_lt = cv2.imencode(".jpg", synthesized["long_term"], [cv2.IMWRITE_JPEG_QUALITY, 85])
        lt_b64 = base64.b64encode(buffer_lt).decode("utf-8")

        processing_time = round(time.time() - start, 2)

        response_data = {
            "success": True,
            "processing_time": processing_time,
            "image": {
                "base64": image_b64,
                "short_term_base64": st_b64,
                "long_term_base64": lt_b64,
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
        }

        # Save to database if phone is provided
        if phone:
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO analyses (phone, result_json) VALUES (?, ?)",
                    (phone, json.dumps(response_data))
                )
                db.commit()

        return JSONResponse(content=response_data)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"Analysis failed: {str(e)}")


# ─── DB & Profile Routes ───

class ProfileRequest(BaseModel):
    phone: str
    name: str
    gender: str
    age: int

class ConcernsRequest(BaseModel):
    phone: str
    primary_concern: str
    secondary_concerns: list[str]

@app.post("/api/user/profile")
async def save_profile(req: ProfileRequest):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (phone, name, gender, age) VALUES (?, ?, ?, ?)",
            (req.phone, req.name, req.gender, req.age)
        )
        db.commit()
    return {"success": True}

    return {"success": True}

@app.get("/api/user/full-profile/{phone}")
async def get_full_profile(phone: str):
    """Fetch complete user profile including basic details and concerns."""
    with get_db() as db:
        cursor = db.cursor()
        # Fetch basic details
        cursor.execute("SELECT name, gender, age FROM users WHERE phone = ?", (phone,))
        user_row = cursor.fetchone()
        
        if not user_row:
            return {"exists": False}
            
        # Fetch concerns
        cursor.execute("SELECT primary_concern, secondary_concerns FROM concerns WHERE phone = ?", (phone,))
        concerns_row = cursor.fetchone()
        
        return {
            "exists": True,
            "details": {
                "name": user_row["name"],
                "gender": user_row["gender"],
                "age": user_row["age"]
            },
            "concerns": {
                "primary_concern": concerns_row["primary_concern"] if concerns_row else "Other",
                "secondary_concerns": json.loads(concerns_row["secondary_concerns"]) if concerns_row else []
            }
        }
@app.get("/api/user/analysis/{phone}/latest")
async def get_latest_analysis(phone: str):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT result_json FROM analyses WHERE phone = ? ORDER BY created_at DESC LIMIT 1", (phone,))
        row = cursor.fetchone()
        if row:
            data = json.loads(row["result_json"])
            
            # HYDRATION LOGIC: If products or buckets are missing (old data), inject them now
            from services.recommendations import _get_products
            
            # 1. Inject missing bucket labels
            if "analysis" in data:
                total_lesions = data["analysis"].get("lesion_count", 0)
                # If total_lesions is 0 but acne_severity exists, use that
                if total_lesions == 0 and "acne_severity" in data["analysis"]:
                    total_lesions = data["analysis"]["acne_severity"].get("total_lesions", 0)
                
                bucket = "0-2"
                if 3 <= total_lesions <= 5: bucket = "3-5"
                elif 6 <= total_lesions <= 10: bucket = "5-10"
                elif 11 <= total_lesions <= 15: bucket = "11-15"
                elif total_lesions > 15: bucket = "15+"
                
                data["analysis"]["lesion_count_bucket"] = bucket

            # 2. Inject missing products
            if "recommendations" in data:
                recs = data["recommendations"]
                for routine_key in ["am_routine", "pm_routine"]:
                    if routine_key in recs:
                        for step in recs[routine_key]:
                            if "recommended_products" not in step or not step["recommended_products"]:
                                step["recommended_products"] = _get_products(step.get("action", ""))
            
            return JSONResponse(content=data)
        raise HTTPException(status_code=404, detail="No analysis found")

import re

@app.get("/api/user/analyses/{phone}")
async def get_all_analyses(phone: str):
    """
    Retrieve all historical analyses for a user.
    Optimized: Uses Regex to extract thumbnail and summary fields without parsing 
    the entire heavy JSON block (which contains multiple synthetic images).
    """
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, phone, result_json, created_at FROM analyses WHERE phone = ? ORDER BY created_at DESC", 
            (phone,)
        )
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            json_blob = row["result_json"]
            
            # Extract severity - look for acne_severity: { ..., "grade": "..." }
            severity_match = re.search(r'"acne_severity":\s*\{[^}]*"grade":\s*"([^"]+)"', json_blob)
            severity = severity_match.group(1) if severity_match else "N/A"
            
            # Extract lesion count
            count_match = re.search(r'"lesion_count":\s*(\d+)', json_blob)
            count = int(count_match.group(1)) if count_match else 0
            
            # Extract first base64 (main image)
            thumb_match = re.search(r'"base64":\s*"([^"]+)"', json_blob)
            thumbnail = thumb_match.group(1) if thumb_match else ""
            
            results.append({
                "id": row["id"],
                "created_at": row["created_at"],
                "analysis_summary": {
                    "severity": severity,
                    "lesion_count": count,
                },
                "thumbnail": thumbnail, 
            })
            
        return results

@app.get("/api/user/analysis/{analysis_id}")
async def get_analysis_by_id(analysis_id: int):
    """Retrieve a specific analysis by its database ID."""
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT result_json FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        if row:
            return JSONResponse(content=json.loads(row["result_json"]))
        raise HTTPException(status_code=404, detail="Analysis not found")
        
@app.delete("/api/user/analysis/{analysis_id}")
async def delete_analysis(analysis_id: int):
    """Permanently delete an analysis record from the database."""
    with get_db() as db:
        cursor = db.cursor()
        # Verify it exists first
        cursor.execute("SELECT id FROM analyses WHERE id = ?", (analysis_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Analysis record not found")
            
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        db.commit()
    return {"success": True, "message": "Record deleted permanently"}


# ─── ML Progression Routes ───

class ProgressionRequest(BaseModel):
    lesion_count: int
    severity: str
    pigmentation: float
    age: int
    skin_type: str

@app.post("/api/predict-progression")
async def predict_progression(request: ProgressionRequest):
    """
    Pure ML endpoint for predicting skin condition progressing.
    Takes current skin metrics and outputs short/long term AI predictions.
    """
    result = progression_service.predict(
        lesion_count=request.lesion_count,
        severity=request.severity,
        pigmentation=request.pigmentation,
        age=request.age,
        skin_type=request.skin_type
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

# ─── Auth Routes ───

class SendOTPRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

@app.post("/api/auth/send-otp")
async def send_otp(request: SendOTPRequest):
    """Generates and sends an OTP to the given phone number."""
    # Clean phone number (remove +91 or spaces)
    phone = request.phone.replace(" ", "").replace("+91", "")
    
    if len(phone) != 10:
        raise HTTPException(400, "Invalid phone number. Must be 10 digits.")
        
    otp = auth_service.generate_otp(phone)
    success = auth_service.send_sms(phone, otp)
    
    if not success:
        raise HTTPException(500, "Failed to send SMS. Please check API configuration.")
        
    return {"message": "OTP sent successfully."}

@app.post("/api/auth/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """Verifies the OTP provider by the user."""
    print(f"[API] Received OTP verification request: Phone={request.phone}, OTP={request.otp}")
    phone = request.phone.replace(" ", "").replace("+91", "")
    
    if auth_service.verify_otp(phone, request.otp):
        return {"message": "Success", "token": "mock-jwt-token"}
    else:
        print(f"[API] Verification failed for {phone}")
        raise HTTPException(400, "Invalid or expired OTP.")


# ─── Run ───
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
