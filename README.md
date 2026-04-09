# SkinSight AI — AI-Powered Facial Skin Health Screening 🧬

SkinSight AI is a production-grade facial skin health screening tool that analyzes images across multiple dimensions: acne severity, lesion counts, facial zone mapping, and hyperpigmentation. 

Built with **FastAPI**, **MediaPipe**, **YOLOv8**, and **React**, it provides users with an instant, interactive report and an AI-driven skincare recommendation engine.

![Dashboard Preview](https://via.placeholder.com/1200x600/111/fff?text=SkinSight+AI+Dashboard+Preview)

## ✨ Key Features
- **AI-Driven Analysis**: Automatic grading of acne severity (Clear/Mild/Moderate/Severe).
- **Lesion Detection**: Precision mapping of Comedonal, Inflammatory, and other lesion types.
- **Interactive Layers**: Toggleable overlays for Face Mesh, Zones, Pigmentation, and Heatmaps.
- **Progress Tracking**: Simulated treatment trajectory (Now → Short Term → Long Term).
- **Personalized Routine**: AI-generated AM/PM skincare routines based on analysis results.
- **Premium UI**: Modern dark glassmorphism design with smooth animations.

## 🛠️ Technology Stack
- **Backend**: Python, FastAPI, MediaPipe, OpenCV, YOLOv8 (Ultralytics).
- **Frontend**: React (Vite), HTML5 Canvas, Vanilla CSS.
- **Design**: Dark Glassmorphism Design System.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- Node.js & npm
- [Roboflow API Key](https://app.roboflow.com/settings/api) (for model training)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Training the Model
To achieve maximum accuracy, train the YOLOv8 model:
```bash
cd backend
python train_model.py --api-key YOUR_API_KEY
```

## ⚕️ Medical Disclaimer
SkinSight AI is an AI-powered screening tool and does NOT constitute medical diagnosis. Results are for informational purposes only. Always consult a qualified dermatologist for medical advice and treatment.

## 📄 License
MIT License
