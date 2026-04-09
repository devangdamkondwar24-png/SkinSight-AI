"""
SkinSight AI — YOLOv8 Acne/Lesion Detection Model Training Pipeline

This script:
1. Downloads an acne detection dataset from Roboflow
2. Trains a YOLOv8 model on it
3. Saves the best weights for inference

Usage:
    python train_model.py --api-key YOUR_ROBOFLOW_API_KEY
    
    Or set environment variable:
    set ROBOFLOW_API_KEY=YOUR_KEY
    python train_model.py
"""

import argparse
import os
import sys
from pathlib import Path


def download_dataset(api_key: str, workspace: str = "project-design-zsvzk",
                     project: str = "acne-detection-yags7", version: int = 12):
    """Download acne detection dataset from Roboflow."""
    from roboflow import Roboflow

    print(f"\n{'='*60}")
    print("  STEP 1: Downloading Dataset from Roboflow")
    print(f"{'='*60}")
    print(f"  Workspace: {workspace}")
    print(f"  Project:   {project}")
    print(f"  Version:   {version}")
    print(f"{'='*60}\n")

    rf = Roboflow(api_key=api_key)
    proj = rf.workspace(workspace).project(project)
    dataset = proj.version(version).download("yolov8", location=str(Path(__file__).parent / "dataset"))

    print(f"\n  ✅ Dataset downloaded to: {dataset.location}")
    return dataset.location


def train_model(dataset_path: str, epochs: int = 50, imgsz: int = 640, batch: int = 16):
    """Train YOLOv8 model on the acne detection dataset."""
    from ultralytics import YOLO

    print(f"\n{'='*60}")
    print("  STEP 2: Training YOLOv8 Model")
    print(f"{'='*60}")
    print(f"  Dataset:  {dataset_path}")
    print(f"  Epochs:   {epochs}")
    print(f"  ImgSize:  {imgsz}")
    print(f"  Batch:    {batch}")
    print(f"{'='*60}\n")

    # Use YOLOv8 small for better accuracy (Small > Nano)
    model = YOLO("yolov8s.pt")

    data_yaml = os.path.join(dataset_path, "data.yaml")
    if not os.path.exists(data_yaml):
        print(f"  ❌ data.yaml not found at {data_yaml}")
        sys.exit(1)

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=str(Path(__file__).parent / "runs"),
        name="acne_detector",
        exist_ok=True,
        patience=20, # Increased patience for deeper learning
        save=True,
        plots=True,
        verbose=True,
    )

    # Copy best weights to a known location
    best_pt = Path(__file__).parent / "runs" / "acne_detector" / "weights" / "best.pt"
    target_pt = Path(__file__).parent / "models" / "acne_detector.pt"
    target_pt.parent.mkdir(parents=True, exist_ok=True)

    if best_pt.exists():
        import shutil
        shutil.copy2(str(best_pt), str(target_pt))
        print(f"\n  ✅ Best model saved to: {target_pt}")
    else:
        print(f"\n  ⚠️  best.pt not found at expected path. Check runs/acne_detector/weights/")

    return results


def main():
    parser = argparse.ArgumentParser(description="Train SkinSight AI acne detection model")
    parser.add_argument("--api-key", type=str, default=None,
                        help="Roboflow API key (or set ROBOFLOW_API_KEY env var)")
    parser.add_argument("--workspace", type=str, default="project-design-zsvzk",
                        help="Roboflow workspace ID")
    parser.add_argument("--project", type=str, default="acne-detection-yags7",
                        help="Roboflow project ID")
    parser.add_argument("--version", type=int, default=12,
                        help="Dataset version number")
    parser.add_argument("--epochs", type=int, default=100,
                        help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640,
                        help="Training image size")
    parser.add_argument("--batch", type=int, default=8,
                        help="Batch size")
    parser.add_argument("--skip-download", action="store_true",
                        help="Skip dataset download (use existing dataset/)")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ROBOFLOW_API_KEY")

    if not args.skip_download:
        if not api_key:
            print("❌ Please provide a Roboflow API key:")
            print("   python train_model.py --api-key YOUR_KEY")
            print("   or: set ROBOFLOW_API_KEY=YOUR_KEY")
            sys.exit(1)
        dataset_path = download_dataset(api_key, args.workspace, args.project, args.version)
    else:
        dataset_path = str(Path(__file__).parent / "dataset")
        if not os.path.exists(dataset_path):
            print(f"❌ Dataset not found at {dataset_path}. Run without --skip-download first.")
            sys.exit(1)

    train_model(dataset_path, args.epochs, args.imgsz, args.batch)

    print(f"\n{'='*60}")
    print("  🎉 Training Complete!")
    print(f"  Model saved to: backend/models/acne_detector.pt")
    print(f"  You can now start the server: python main.py")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
