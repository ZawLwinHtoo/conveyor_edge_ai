"""
Conveyor Belt Defect Detection - Model Training Pipeline
Fine-tunes or retrains YOLOv8 for higher accuracy, recall, and precision.

Recommended architectures:
- yolov8s.pt (Small - 11.2M params): Great balance of speed & high precision.
- yolov8m.pt (Medium - 25.9M params): Maximum precision for industrial quality control.
"""

import argparse
import os
import sys
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8 on Conveyor Defect Dataset")
    parser.add_argument("--data", type=str, default="dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", type=str, default="yolov8s.pt", help="Base model (yolov8s.pt, yolov8m.pt, or best.pt)")
    parser.add_argument("--epochs", type=int, default=80, help="Number of training epochs (recommended: 60-100)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (reduce if out of GPU memory)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--device", type=str, default="", help="Device: '0' for CUDA GPU, 'cpu' for CPU")
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"❌ Error: Dataset config '{args.data}' not found.")
        print("Please ensure your dataset is placed in 'dataset/' and configured in 'dataset/data.yaml'.")
        sys.exit(1)

    print("=" * 60)
    print("🚀 STARTING CONVEYOR BELT DEFECT AI TRAINING")
    print("=" * 60)
    print(f"Base Model:    {args.model}")
    print(f"Dataset YAML:  {args.data}")
    print(f"Epochs:        {args.epochs}")
    print(f"Batch Size:    {args.batch}")
    print(f"Image Size:    {args.imgsz}")
    print("=" * 60)

    # Initialize model
    model = YOLO(args.model)

    # Train with augmented hyperparameters for industrial environments
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device if args.device else None,
        # Augmentations for variable lighting, dust, and screen/camera reflections
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        patience=20,  # Early stopping if no improvement
        save=True,
        plots=True,
        project="runs/detect",
        name="conveyor_defect_model"
    )

    print("\n✅ Training complete!")
    print(f"Best weights saved to: runs/detect/conveyor_defect_model/weights/best.pt")
    print("Copy the generated best.pt to the project root to use it immediately.")

if __name__ == "__main__":
    main()
