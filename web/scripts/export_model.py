"""Export the trained Ultralytics weights to the ONNX file the website loads.

Run from the repository root with the project's Python environment:

    .venv\\Scripts\\python.exe web/scripts/export_model.py

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
SRC = ROOT / "models" / "helmet_yolo26n.pt"
OUT = ROOT / "web" / "public" / "models" / "helmet_yolo26n.dynamic.onnx"
LIMIT = 25 * 1024 * 1024  # Cloudflare Pages per-file limit

if not SRC.exists():
    sys.exit(f"Missing weights: {SRC}")

# Export next to a copy so the original models/ folder is not littered with build files.
work = ROOT / "web" / ".export-tmp"
work.mkdir(exist_ok=True)
copy = work / SRC.name
shutil.copy2(SRC, copy)

model = YOLO(str(copy))
print("classes:", model.names)
exported = Path(model.export(format="onnx", imgsz=640, opset=17, simplify=True, dynamic=True, half=False))

OUT.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(exported, OUT)
shutil.rmtree(work, ignore_errors=True)

size = OUT.stat().st_size
print(f"wrote {OUT} ({size / 1048576:.2f} MiB)")
if size >= LIMIT:
    sys.exit("ONNX file is over the Cloudflare Pages 25 MiB limit; use a smaller model or quantize it.")
print("Update sizeBytes in web/src/inference/models.ts to", size)
