# RideShield AI

AI helmet detection for road safety. The repository keeps both versions of the product, which share the same trained model family (classes `helmet` and `nohelmet`):

| Part | Folder | What it is |
|---|---|---|
| Web experience | [`web/`](web/) | Public website with an in-browser test drive. The YOLO model runs on the visitor's device with ONNX Runtime Web. No backend, free to host. Live at https://rideshield-ai.vercel.app |
| Desktop app (offline) | `main.py`, `src/`, `models/`, `start.bat` | PyQt6 instrument-cluster app that runs Ultralytics YOLO on a local camera and logs events to SQLite. See [Desktop app](#desktop-app-offline-version). |

The name is **RideShield AI**. The helmet logo comes from `ai assets/logo full.png`. The web app has day and night themes, each with its own logo. To change the logo, replace the sheet and run `.venv\Scripts\python.exe web/scripts/build_brand_assets.py`; it rewrites `web/public/brand` (logos, favicons, social image). Identity text is in `web/src/config/brand.ts`.

## Web experience

Routes: `/` landing page, `/test-drive` cockpit (webcam or uploaded video), `/trailer` trailer page (placeholder until the film is added).

```bash
cd web
npm install
npm run dev        # http://localhost:5173
npm run build      # typecheck, production build, 25 MiB per-file check
npm run preview    # serve the production build locally
```

- **Privacy:** webcam frames and uploaded videos are processed in the browser and never uploaded. There is no inference server.
- **Engine:** WebGPU when the browser supports it, WebAssembly otherwise. `/test-drive?backend=wasm` forces WebAssembly.
- **Model:** `web/public/models/helmet_yolo26n.dynamic.onnx` (9.6 MiB), exported from `models/helmet_yolo26n.pt`. Re-export with `npm run export:model` from `web/`.
- **Counters:** boxes are counted per frame, and unique riders are counted separately with a simple tracker. Nothing shown is simulated; the gauges show measured model throughput, not vehicle speed.
- **Hosting:** live on Vercel Hobby (free) at https://rideshield-ai.vercel.app. Cloudflare Pages Free also works and its settings are documented. Build settings, how to add the trailer, model sizes and known limits are in [`web/DEPLOYMENT.md`](web/DEPLOYMENT.md).

### What has and has not been verified

Verified: the browser model gives the same detections as the PyTorch weights on test photos; uploaded-video analysis works on WebGPU and WebAssembly from the production build; denied-camera and invalid-file messages; no horizontal scroll at phone width.

Verified on the live Vercel site: direct load of `/test-drive`, cross-origin isolation, WebGPU engine and model loading.

Not yet verified: live webcam capture, trailer fullscreen, Safari and Firefox, real phones, and a Cloudflare Pages deployment.

## Desktop app (offline version)

The original RideShield AI desktop software is kept in this repository and is separate from the website. It runs on one computer with a local camera, uses the YOLO weights in `models/` directly through Ultralytics, and needs no internet connection to run detection. You only need internet once, to install the Python packages.

**Run it (Windows):**

```bash
start.bat          # creates .venv, installs requirements.txt, then runs main.py
```

Or by hand: `python -m venv .venv`, `.venv\Scripts\activate`, `pip install -r requirements.txt`, `python main.py`.

**What it does** (from the source in `src/`):

- Splash screen, then a full-screen "TFT cluster" dashboard with custom-drawn dials, helmet status, engine control, ride information, system alerts and a live camera feed with detection boxes.
- Pages for Live Monitor, Fleet Analytics, Event Stream, Rider Safety Center, Settings and an Engineering Console (CPU, memory, GPU and model status).
- Settings for confidence threshold (0.30 to 0.90), model file (any `.pt` in `models/`), camera resolution, safety mode (Monitor Only, Smart Lock Mode, Strict Enforcement) and alert delay.
- When no helmet is seen for the configured delay it raises an alert, saves a snapshot to `assets/captures/` and speaks a warning. Voice uses the Windows speech synthesizer through PowerShell, so spoken alerts work on Windows only.
- Detections, events, alerts, sessions and settings are stored in a local SQLite file, `database/rideshield.db`.

**Models:** `yolo11m.pt` is the default. Choose `helmet_yolo26n.pt` or `best.pt` in Settings. All three detect `helmet` and `nohelmet`.

**Files:** `main.py` (entry point), `src/` (UI, detection thread, alert and audio systems, database), `assets/` (images and stylesheet), `models/` (weights), `requirements.txt` (PyQt6, opencv-python, numpy, ultralytics, psutil, py-cpuinfo).

The desktop app has not been changed by the website work, and I did not run it while writing this section.

### Website versus desktop

| | Website (`web/`) | Desktop app |
|---|---|---|
| Runs on | Any modern browser | Windows computer with Python |
| Input | Webcam or uploaded video | Local camera |
| Inference | In the browser (WebGPU or WebAssembly) | Ultralytics on the local CPU or GPU |
| Needs internet | To open the site | Only to install packages |
| History | This session only | Saved to a local SQLite database |
| Alerts | On-screen events | On-screen, snapshots and voice |

## Models

All three weights in `models/` have the classes `helmet` and `nohelmet`.

| Weights | Size | Browser ONNX (fp32) | Used by |
|---|---|---|---|
| `helmet_yolo26n.pt` | 5.1 MiB | 9.6 MiB | Web (shipped) and desktop |
| `best.pt` | 21.5 MiB | 42.7 MiB, over the 25 MiB hosting limit | Desktop |
| `yolo11m.pt` | 38.6 MiB | 76.7 MiB, over the limit | Desktop (default) |

The web demo and the desktop app can therefore give different results unless the desktop is set to `helmet_yolo26n.pt`.

## Things to decide before going public

- **Licence:** Ultralytics YOLO is AGPL-3.0 (or a paid enterprise licence). Publishing the weights and a site built on them carries obligations. No licence text in this repository has been changed.
- **Private data:** `database/rideshield.db` is tracked in git even though `*.db` is in `.gitignore`, and `assets/captures/` holds photos of people. Review both first.

## Project skills

`.claude/` and `.agents/` hold Claude Code skills used for design, motion and workflow. They are tooling only and are not part of the product.
