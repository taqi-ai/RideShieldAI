"""Export the trained Ultralytics weights to the ONNX files the website loads.

Run from the repository root with the project's Python environment:

    .venv\\Scripts\\python.exe web/scripts/export_model.py            # all models
    .venv\\Scripts\\python.exe web/scripts/export_model.py yolo26n    # one model

Why dynamic=True: Ultralytics pads non-square images only to the next multiple of 32 when it
runs the .pt file. A fixed 640x640 ONNX pads to a full square, which changed confidences
noticeably on the same photos (0.90 became 0.30 on one test image). A dynamic-shape export
lets the browser use the same minimal padding and reproduce the PyTorch results.
"""
import shutil
import sys
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "web" / "public" / "models"

# id -> (weights file in models/, output file name, architecture the weights were trained from)
MODELS = {
    "yolo26n": ("helmet_yolo26n.pt", "helmet_yolo26n.dynamic.onnx", "YOLO26n"),
    "yolov8s": ("best.pt", "helmet_yolov8s.dynamic.onnx", "YOLOv8s"),
    "yolo11m": ("yolo11m.pt", "helmet_yolo11m.dynamic.onnx", "YOLO11m"),
}

wanted = sys.argv[1:] or list(MODELS)
work = ROOT / "web" / ".export-tmp"
work.mkdir(exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

for key in wanted:
    weights, out_name, arch = MODELS[key]
    src = ROOT / "models" / weights
    if not src.exists():
        sys.exit(f"Missing weights: {src}")
    # Export from a copy so the original models/ folder is not littered with build files.
    copy = work / src.name
    shutil.copy2(src, copy)
    model = YOLO(str(copy))
    print(f"[{key}] {arch} classes: {model.names}")
    exported = Path(model.export(format="onnx", imgsz=640, opset=17, simplify=True, dynamic=True, half=False))
    dest = OUT_DIR / out_name
    shutil.copy2(exported, dest)
    size = dest.stat().st_size
    print(f"[{key}] wrote {dest.name}: {size} bytes ({size / 1048576:.2f} MiB)")
    if size >= 25 * 1024 * 1024:
        print(f"[{key}] note: over Cloudflare Pages' 25 MiB per-file limit; fine on Vercel (100 MB), not on Cloudflare.")

shutil.rmtree(work, ignore_errors=True)
print("Update sizeBytes in web/src/inference/models.ts to match.")
