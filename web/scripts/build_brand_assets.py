"""Cut clean, transparent day and night logos out of the supplied logo sheet.

Source: "ai assets/logo full.png" (day logo on a light tile above, night logo on a black tile
below). Output goes to web/public/brand. Run from the repository root:

    .venv\\Scripts\\python.exe web/scripts/build_brand_assets.py

Day logo: dark artwork on a light tile, so alpha comes from how far a pixel is from the tile colour.
Night logo: light artwork on black, so alpha comes from the brightest channel. Colour is recovered
by un-premultiplying, which keeps the violet accent at its true colour on any background.
"""
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "ai assets" / "logo full.png"
OUT = ROOT / "web" / "public" / "brand"
OUT.mkdir(parents=True, exist_ok=True)

sheet = cv2.imread(str(SRC), cv2.IMREAD_COLOR)[:, :, ::-1].astype(np.float32)  # RGB


def to_rgba(region: np.ndarray, mode: str) -> np.ndarray:
    if mode == "day":
        bg = np.array([244.0, 244.0, 244.0])
        a = 1.0 - region.min(axis=2) / bg.mean()
        a = np.clip((a - 0.06) / 0.94, 0, 1)
        safe = np.maximum(a, 1e-3)[..., None]
        rgb = (region - (1 - a)[..., None] * bg) / safe
    else:
        a = region.max(axis=2) / 255.0
        a = np.clip((a - 0.06) / 0.94, 0, 1)
        safe = np.maximum(a, 1e-3)[..., None]
        rgb = region / safe
    rgb = np.clip(rgb, 0, 255)
    rgb[a < 0.02] = 0
    return np.dstack([rgb, a * 255.0]).astype(np.uint8)


def crop_alpha(img: np.ndarray, pad: int = 8) -> np.ndarray:
    ys, xs = np.where(img[..., 3] > 12)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    out = img[max(0, y0 - pad) : y1 + pad + 1, max(0, x0 - pad) : x1 + pad + 1]
    return out


def save(name: str, img: np.ndarray) -> None:
    cv2.imwrite(str(OUT / name), img[:, :, [2, 1, 0, 3]], [cv2.IMWRITE_PNG_COMPRESSION, 9])
    print(name, img.shape[1], "x", img.shape[0])


def runs(mask: np.ndarray):
    """Start/end indices of consecutive True runs."""
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        if not v and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(mask) - 1))
    return out


def split_parts(logo: np.ndarray):
    """Helmet mark, wordmark (without the tagline), tagline from a full lockup."""
    a = logo[..., 3] > 40
    col_runs = runs(a.any(axis=0))
    # Helmet = first horizontal block; text = everything to its right (gap > 8px).
    merged = [list(col_runs[0])]
    for s, e in col_runs[1:]:
        if s - merged[-1][1] <= 8:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    mark_x1 = merged[0][1]
    text_x0 = merged[1][0]
    mark = crop_alpha(logo[:, : mark_x1 + 1])
    text = logo[:, text_x0:]
    row_runs = runs((text[..., 3] > 40).any(axis=1))
    rows = [list(row_runs[0])]
    for s, e in row_runs[1:]:
        if s - rows[-1][1] <= 12:
            rows[-1][1] = e
        else:
            rows.append([s, e])
    word = crop_alpha(text[rows[0][0] : rows[0][1] + 1])
    return mark, word


def compact(mark: np.ndarray, word: np.ndarray) -> np.ndarray:
    """Helmet + wordmark side by side, wordmark centred on the helmet, no tagline."""
    h = mark.shape[0]
    wh = int(h * 0.52)
    ww = int(word.shape[1] * wh / word.shape[0])
    word_s = cv2.resize(word, (ww, wh), interpolation=cv2.INTER_AREA)
    gap = int(h * 0.12)
    canvas = np.zeros((h, mark.shape[1] + gap + ww, 4), np.uint8)
    canvas[:, : mark.shape[1]] = mark
    y = (h - wh) // 2
    canvas[y : y + wh, mark.shape[1] + gap :] = word_s
    return canvas


def rounded_tile(size: int, rgb=(10, 10, 14), radius: float = 0.22) -> np.ndarray:
    tile = np.zeros((size, size, 4), np.uint8)
    mask = np.zeros((size, size), np.uint8)
    r = int(size * radius)
    cv2.rectangle(mask, (r, 0), (size - r, size), 255, -1)
    cv2.rectangle(mask, (0, r), (size, size - r), 255, -1)
    for cx, cy in [(r, r), (size - r, r), (r, size - r), (size - r, size - r)]:
        cv2.circle(mask, (cx, cy), r, 255, -1)
    tile[..., :3] = rgb
    tile[..., 3] = mask
    return tile


def paste_center(tile: np.ndarray, art: np.ndarray, fill: float) -> np.ndarray:
    size = tile.shape[0]
    scale = size * fill / max(art.shape[:2])
    art_s = cv2.resize(art, (int(art.shape[1] * scale), int(art.shape[0] * scale)), interpolation=cv2.INTER_AREA)
    y0 = (size - art_s.shape[0]) // 2
    x0 = (size - art_s.shape[1]) // 2
    a = art_s[..., 3:4] / 255.0
    region = tile[y0 : y0 + art_s.shape[0], x0 : x0 + art_s.shape[1]]
    region[..., :3] = (art_s[..., :3] * a + region[..., :3] * (1 - a)).astype(np.uint8)
    region[..., 3] = np.maximum(region[..., 3], art_s[..., 3])
    return tile


results = {}
for mode, rows in (("day", slice(70, 590)), ("night", slice(690, 1190))):
    full = crop_alpha(to_rgba(sheet[rows, 60:1200], mode))
    mark, word = split_parts(full)
    save(f"logo-{mode}.png", full)
    save(f"mark-{mode}.png", mark)
    save(f"lockup-{mode}.png", compact(mark, word))
    results[mode] = mark

# Favicons and app icons: the night mark on the dark brand tile reads on any browser chrome.
mark_night = results["night"]
for px, name in ((512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (48, "favicon-48.png"), (32, "favicon-32.png")):
    tile = rounded_tile(px) if name != "apple-touch-icon.png" else rounded_tile(px, radius=0.0)
    save(name, paste_center(tile, mark_night, 0.66))

# Social preview image: the night logo on the brand background with a soft violet glow.
W, H = 1200, 630
bg = np.zeros((H, W, 3), np.float32)
bg[:] = (10, 10, 14)
yy, xx = np.mgrid[0:H, 0:W]
glow = np.exp(-(((xx - 880) / 420) ** 2 + ((yy - 260) / 300) ** 2))
bg += glow[..., None] * np.array([60, 40, 120], np.float32)
og = np.dstack([np.clip(bg, 0, 255), np.full((H, W), 255.0)]).astype(np.uint8)
logo = cv2.imread(str(OUT / "logo-night.png"), cv2.IMREAD_UNCHANGED)[:, :, [2, 1, 0, 3]]
scale = 860 / logo.shape[1]
logo_s = cv2.resize(logo, (860, int(logo.shape[0] * scale)), interpolation=cv2.INTER_AREA)
y0, x0 = (H - logo_s.shape[0]) // 2, (W - 860) // 2
a = logo_s[..., 3:4] / 255.0
og[y0 : y0 + logo_s.shape[0], x0 : x0 + 860, :3] = (logo_s[..., :3] * a + og[y0 : y0 + logo_s.shape[0], x0 : x0 + 860, :3] * (1 - a)).astype(np.uint8)
cv2.imwrite(str(OUT / "og-image.jpg"), og[:, :, [2, 1, 0]], [cv2.IMWRITE_JPEG_QUALITY, 90])
print("og-image.jpg")
