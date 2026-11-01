# RideShield AI web: run, validate and deploy

The website is a static React + TypeScript + Vite app in `web/`. The YOLO model runs in the visitor's browser with ONNX Runtime Web. There is no backend, database, API key or paid service. The desktop PyQt app in the repository root is untouched.

## 1. Run locally

```bash
cd web
npm install
npm run dev        # http://localhost:5173
npm run build      # typecheck, production build, asset size check
npm run preview    # serve the production build on http://localhost:4173
npm run lint
```

Routes: `/` landing, `/test-drive` cockpit, `/trailer` trailer page. Camera access needs HTTPS or `localhost`.

Troubleshooting switch: `/test-drive?backend=wasm` skips WebGPU and uses WebAssembly.

## 2. Prepare or export the model

The site ships three models and the test drive has a switcher (`/test-drive?model=yolov8s` also selects one). Each is exported from a weights file in `models/` (all with classes `helmet`, `nohelmet`):

| Switcher label | Weights | Trained from | ONNX file |
|---|---|---|---|
| YOLO26n (default) | `helmet_yolo26n.pt` | `yolo26n.pt` | `helmet_yolo26n.dynamic.onnx` |
| YOLOv8s | `best.pt` | `yolov8s.pt` | `helmet_yolov8s.dynamic.onnx` |
| YOLO11m | `yolo11m.pt` | `yolo11m.pt` | `helmet_yolo11m.dynamic.onnx` |

```bash
# from the repository root, using the project's Python environment
.venv\Scripts\python.exe web/scripts/export_model.py            # all three
.venv\Scripts\python.exe web/scripts/export_model.py yolov8s    # one
```

Then update `sizeBytes` in `web/src/inference/models.ts` if a size changed. Only the selected model is downloaded, and switching releases the previous one.

Why `dynamic=True`: Ultralytics pads non-square images only to the next multiple of 32. A fixed 640x640 export pads to a full square, which lowered confidence on the same photo from 0.90 to 0.30. The dynamic export reproduces the PyTorch results exactly (see section 3).

### Model sizes (measured)

| Model | `.pt` | ONNX (fp32) | Fits Cloudflare 25 MiB? | Fits Vercel / GitHub (100 MB)? |
|---|---|---|---|---|
| YOLO26n | 5.1 MiB | 9.6 MiB | Yes | Yes |
| YOLOv8s | 21.5 MiB | 42.7 MiB | No | Yes |
| YOLO11m (desktop default) | 38.6 MiB | 76.9 MiB | No | Yes |

Vercel is the current host, so all three ship. On Cloudflare Pages Free only YOLO26n fits: to deploy there, delete the other two ONNX files and their entries in `src/inference/models.ts` first. `npm run build` prints a note for every file over 25 MiB and fails above 100 MB. GitHub warns above 50 MB per file; the YOLO11m file is 76.9 MiB, so move the larger models to Git LFS or a release asset if the repository grows. Int8 quantization would shrink them but was not tried; it needs an accuracy check and is not supported by the WebGPU backend.

The desktop app's default is `yolo11m.pt`; the website defaults to YOLO26n, so out-of-the-box results can differ between them.

The UI reads the model name, size and class names from `src/inference/models.ts`, which matches the exported file.

## 3. Validate browser inference

Verified in this repository (Chromium-based browser, Windows, WebGPU available):

- The same four captured photos give identical results in PyTorch (`.pt`, rectangular padding), ONNX Runtime CPU in Python, and the browser on WebGPU: `nohelmet 0.90`, `nohelmet 0.90`, `helmet 0.36`, no detection.
- A 15-second test clip uploaded through the UI produced real boxes, tracked counts and events on both WebGPU (about 20 ms per frame) and WebAssembly (about 115 ms per frame, 4 threads).
- Both worked from the production build served with `npm run preview`, loaded directly at `/test-drive`.
- YOLOv8s and YOLO11m (raw output, decoded in the browser with NMS) match their PyTorch weights exactly on the same four photos when run on CPU in Python, and both ran the test clip through the switcher in the browser on WebGPU with tracked counts and events (about 32 ms and 43 ms per frame).

To repeat a check yourself: open `/test-drive`, wait for "System ready", choose Upload video with any clip showing riders, and confirm boxes and counters update. Compare against the desktop app or `ultralytics` on the same frames.

Not verified here: live webcam capture (blocked in the test browser), fullscreen on the trailer page, Safari and Firefox, and phones.

## 4a. Vercel (currently deployed)

Live at https://rideshield-ai.vercel.app (Vercel Hobby plan, free). Config is `web/vercel.json`: it sets the cross-origin isolation headers, cache lifetimes and a single-page-app rewrite so `/test-drive` and `/trailer` work on refresh.

The project is connected to the `taqi-ai/RideShieldAI` GitHub repository with root directory `web` and Node 22. Pushing a branch creates a preview deployment; the production branch is `main`, so merging to `main` updates https://rideshield-ai.vercel.app. Build command, output directory and framework come from `vercel.json`.

Because the root directory is set to `web`, run any manual CLI deploy from the repository root after `vercel link`, not from inside `web/`. The Hobby plan is for personal, non-commercial use, so move to another host if this becomes a commercial product. The `rideshield-ai` project name matches the final product name.

## 4b. Cloudflare Pages build settings (alternative)

| Setting | Value |
|---|---|
| Framework preset | None (or Vite) |
| Root directory | `web` |
| Build command | `npm run build` |
| Build output directory | `dist` |
| Environment variable | `NODE_VERSION` = `22` |

`public/_headers` sets cross-origin isolation (so WebAssembly can use several threads), cache lifetimes and a camera permissions policy. Cloudflare Pages serves `index.html` for unknown paths when there is no `404.html`, so refreshing `/test-drive` or `/trailer` works without a `_redirects` file.

## 5. Connect the GitHub repository

1. Push this branch (`feat/web-experience`) and merge it, or deploy the branch directly.
2. Cloudflare dashboard > Workers & Pages > Create > Pages > Connect to Git.
3. Choose the `taqi-ai/RideShieldAI` repository and your production branch.
4. Enter the build settings above and save. The site appears at `https://<project>.pages.dev`.

I did not deploy anything. Connecting the repository needs your Cloudflare login.

## 6. Add the trailer later

Copy the finished film to `web/public/media/rideshield-trailer.mp4` (H.264 MP4, under 25 MiB). Optional extras in the same folder: `rideshield-trailer.vtt` (captions) and `rideshield-trailer-poster.jpg`. No code change is needed: `/trailer` switches from the placeholder to a native video player (play, seek, volume, fullscreen) as soon as the file exists. Paths are in `src/config/brand.ts`.

## 7. Known constraints

- Cloudflare Pages limit: 25 MiB per file, 20,000 files per site. Largest shipped file is the WebGPU runtime `.wasm` at 17.1 MiB. The default ONNX Runtime WebGPU build (28 MiB) is over the limit, so the app uses the JSPI WebGPU build and the plain WebAssembly build instead.
- WebGPU here needs WebAssembly JSPI (recent Chromium-based browsers). Other browsers use WebAssembly, which is slower but gives the same detections.
- Built output contains the ONNX Runtime `.wasm` files twice (hashed copies in `assets/`). Only the loaded ones are downloaded.
- First visit downloads about 10 MB of model plus 14 to 17 MB of runtime (4 to 5 MB compressed). Later visits use the HTTP cache.
- Unique counts use a simple IoU tracker with no motion model, so crowded or fast scenes can split or merge tracks.
- No sample footage is bundled. To enable the Sample button, add `web/public/samples/sample.mp4` (footage you have the rights to).

## 8. No paid service required

The demo uses only static hosting (Cloudflare Pages Free), the free `*.pages.dev` domain, and code running in the visitor's browser. There are no API keys, environment secrets, analytics, databases or inference servers.

## Decisions for you

- **Licence:** Ultralytics YOLO weights and code are AGPL-3.0 (or a paid enterprise licence). Publishing the weights and a site built on them has obligations. Review before going public. No licence text was changed.
- **Repository data:** `database/rideshield.db` (24 MB) is tracked in git even though `*.db` is in `.gitignore`, and `assets/captures/` holds 541 photos of people. Check both before making the repository public.
- **Logo and themes:** the site has night and day themes (follows the OS, with a toggle that is remembered). Logos come from `ai assets/logo full.png` via `scripts/build_brand_assets.py`, which writes `public/brand`. The tagline in `src/config/brand.ts` is provisional.
