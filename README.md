# RideShield AI

AI helmet detection for road safety. The repository has two parts that share the same trained model family (classes `helmet` and `nohelmet`):

| Part | Folder | What it is |
|---|---|---|
| Web experience | [`web/`](web/) | Public website with an in-browser test drive. The YOLO model runs on the visitor's device with ONNX Runtime Web. No backend, free to host. |
| Desktop app | `main.py`, `src/` | PyQt6 instrument-cluster app that runs Ultralytics YOLO on a local camera and logs events to SQLite. |

The name is **RideShield AI** (final). The logo is a placeholder until the final mark is ready; on the web side it lives in `web/src/components/Logo.tsx` and `web/public/favicon.svg`, and identity text is in `web/src/config/brand.ts`.

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

## Desktop app

```bash
start.bat          # creates .venv, installs requirements.txt, runs main.py
```

Or manually: `python -m venv .venv`, `pip install -r requirements.txt`, `python main.py`. Pick the model in Settings. `yolo11m.pt` is the default.

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
