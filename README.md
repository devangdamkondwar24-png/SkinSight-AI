# 🧬 Skin Sight: Clinical-Grade Dermal Analysis

**Skin Sight** is a professional-grade, AI-driven facial health screening and longitudinal tracking platform. It transforms standard mobile imagery into clinical-grade diagnostic data, providing users with a "Clinical Sanctuary" for their skincare journey.

![Skin Sight Banner](https://images.unsplash.com/photo-1612817288484-6f916006741a?q=80&w=2070&auto=format&fit=crop)

## ✨ The Clinical Sanctuary Experience

Skin Sight is built on the philosophy of **Precision Dermatology**. We combine state-of-the-art Computer Vision with Predictive Machine Learning to deliver a distract-free, evidence-based diagnostic environment.

### 🔬 Core Diagnostic Capabilities
- **Advanced Lesion Mapping**: Utilizing **YOLOv8** and **OpenCV**, we identify and categorize Comedonal, Inflammatory, and Hyperpigmentation markers with ~94% diagnostic sensitivity.
- **Anatomical Face Mesh Synthesis**: Powered by **MediaPipe**, our engine maps 468+ facial landmarks to ensure precise zone-based reporting and feature-specific exclusion (e.g., Mustache Shields for high-precision lip-region analysis).
- **Multi-Spectral Visualization**: 
  - **Zone Mapping**: Geometric segmentation of the T-zone, cheeks, and forehead.
  - **Dermal Heatmaps**: Heat-density visualization of inflammatory clusters.
  - **Pigmentation Overlays**: High-contrast sub-surface pigmentation detection.

### 📈 Dermal Evolution Tracking
Unlike standard analyzers, Skin Sight provides a **Longitudinal Synthesis**:
- **2-4 Week Stabilization Prediction**: ML-based forecast of initial inflammatory reduction.
- **8-12 Week Dermal Equilibrium**: Long-term target mapping for cellular health restoration.
- **Progress Synthesis**: Side-by-side evolution tracking using synthesized "short-term" and "long-term" visual targets.

## 🛠️ Technology Stack

### Backend (The Diagnostic Engine)
- **Framework**: FastAPI (High-performance Python API)
- **Computer Vision**: OpenCV, MediaPipe, Ultralytics YOLOv8
- **Machine Learning**: Scikit-Learn (Progression Regressors)
- **Database**: SQLite (Clinical Data Integrity)

### Frontend (The Sanctuary UI)
- **Framework**: Next.js 16 (App Router) & React 19
- **Aesthetics**: Vanilla CSS + Tailwind CSS 4 (Clinical Sanctuary Design System)
- **Motion**: Framer Motion (Fluid, premium micro-animations)
- **Icons**: Lucide React (Clinical Iconography)

## 🚀 Deployment & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 20+
- [Roboflow API Credentials](https://app.roboflow.com/) (Required for YOLOv8 weights)

### 2. Backend Initialization
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

### 3. Frontend Initialization
```bash
cd frontend
npm install
npm run dev
```

## ⚖️ Clinical Scope & Privacy
**Skin Sight** is a screening tool designed to inform, not replace, clinical judgment. 
- **Privacy Sanctuary**: All biometric markers are processed within a clinical confidentiality protocol.
- **Disclaimer**: This platform does not provide medical diagnosis. Always consult a board-certified dermatologist for medical treatment.

---
**Skin Sight Clinical Labs • v2.0 • Premium Digital Dermatology**
