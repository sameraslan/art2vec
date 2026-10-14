"""One preprocessing path for every feature.

load_image   file -> sRGB PIL image (ICC converted, EXIF rotated, alpha flattened), optional auto-crop
stats_array  PIL -> float32 sRGB array in [0, 1] with a fixed pixel budget (aspect kept)
model_views  PIL -> normalised model inputs under a named view (center / squash / pad / tile / native)
"""

from __future__ import annotations

import io
import math
from pathlib import Path

import numpy as np
from scipy import ndimage
from PIL import Image, ImageCms, ImageOps

Image.MAX_IMAGE_PIXELS = 400_000_000  # museum masters are large; these are trusted local files

VIEWS = ("center", "squash", "pad", "tile", "native")
AUTOCROP = ("none", "border", "frame")
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")

_SRGB = ImageCms.createProfile("sRGB")


def list_images(directory: str | Path) -> list[Path]:
    d = Path(directory)
    return sorted(p for p in d.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES and p.is_file())


def to_srgb(img: Image.Image) -> Image.Image:
    """Convert to 8-bit sRGB. Honours an embedded ICC profile; untagged files are assumed sRGB."""
    img = ImageOps.exif_transpose(img)
    icc = img.info.get("icc_profile")
    if img.mode in ("I;16", "I;16B", "I;16L", "I"):
        arr = np.asarray(img).astype(np.float32)
        img = Image.fromarray(np.clip(arr / 257.0, 0, 255).astype(np.uint8), "L")
    if img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, rgba).convert("RGB")
    if icc and img.mode in ("RGB", "CMYK", "L"):
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            img = ImageCms.profileToProfile(img, src, _SRGB, outputMode="RGB")
        except (ImageCms.PyCMSError, OSError, ValueError):
            pass  # broken profile: fall through and treat the numbers as sRGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.info.pop("icc_profile", None)
    return img


# ---------------------------------------------------------------- auto-crop


def _uniform_trim(a: np.ndarray, max_frac: float, std_t: float, col_t: float) -> tuple[int, int, int, int]:
    """Trim rows/columns that are flat and match the outermost line's colour. a: HxWx3 float 0..255."""
    h, w, _ = a.shape

    def run(lines: np.ndarray, limit: int) -> int:
        # lines: [n_lines, length, 3], outermost first
        ref = np.median(lines[0], axis=0)
        k = max(3, (lines.shape[1] // 8) | 1)
        n = 0
        for line in lines[:limit]:
            # flat = close to its own running mean (tolerates a lighting gradient along a wall);
            # the 2% most deviant pixels are ignored (dust, a label)
            dev = np.abs(line - ndimage.uniform_filter1d(line, k, axis=0, mode="nearest")).max(axis=1)
            flat = np.percentile(dev, 98) < std_t
            same = np.abs(np.median(line, axis=0) - ref).max() < col_t
            if not (flat and same):
                break
            n += 1
        if n == 0 or n >= len(lines) - 2:
            return 0
        # A margin ends at the picture's edge: most of the next lines must differ from the margin.
        # A painted dark background ends where one figure pokes in, so this rejects it (and it
        # rejects shaped panels, which no rectangle can crop).
        nxt = lines[min(n + 1, len(lines) - 1)]
        if (np.abs(nxt - ref).max(axis=1) > col_t).mean() < 0.5:
            return 0
        return n

    top = run(a, int(h * max_frac))
    bottom = run(a[::-1], int(h * max_frac))
    left = run(a.transpose(1, 0, 2), int(w * max_frac))
    right = run(a.transpose(1, 0, 2)[::-1], int(w * max_frac))
    return left, top, w - right, h - bottom


def _frame_trim(a: np.ndarray, max_frac: float = 0.2) -> tuple[int, int, int, int] | None:
    """Look for a picture frame: a long straight edge parallel to each side, at a similar depth on
    at least three sides. Returns the inner box or None. a: HxWx3 float 0..255."""
    g = a.mean(axis=2)
    h, w = g.shape
    # fraction of a line's pixels that sit on a strong perpendicular step
    dy = np.abs(np.diff(g, axis=0))  # [h-1, w]
    dx = np.abs(np.diff(g, axis=1))  # [h, w-1]
    row_score = (dy > 18).mean(axis=1)
    col_score = (dx > 18).mean(axis=0)

    def innermost(score: np.ndarray, n: int) -> int:
        lim = max(3, int(n * max_frac))
        idx = np.nonzero(score[:lim] > 0.6)[0]
        return int(idx.max()) + 1 if idx.size else 0

    top = innermost(row_score, h)
    bottom = innermost(row_score[::-1], h)
    left = innermost(col_score, w)
    right = innermost(col_score[::-1], w)
    depths = np.array([left, top, right, bottom], dtype=float)
    found = depths > 0.012 * min(h, w)
    if found.sum() < 3:
        return None
    d = depths[found]
    if d.max() > 2.5 * d.min():  # frames have a similar width on every side
        return None
    fill = int(np.median(d))
    left, top, right, bottom = (int(x) if f else fill for x, f in zip(depths, found, strict=True))
    return left, top, w - right, h - bottom


def autocrop_box(img: Image.Image, mode: str = "border") -> tuple[int, int, int, int]:
    """Crop box (left, top, right, bottom) in the image's own pixels.

    border  trims flat, single-colour margins (scanner white, black bars, a plain wall).
    frame   does that, then looks for a frame's straight inner edge and trims to it, then trims
            any flat margin left inside (a mount). Heuristic; see the README for how well it does.
    """
    if mode == "none":
        return (0, 0, img.width, img.height)
    scale = 512 / max(img.size)
    small = img.resize((max(8, round(img.width * scale)), max(8, round(img.height * scale))), Image.BILINEAR)
    a = np.asarray(small, dtype=np.float32)
    l, t, r, b = _uniform_trim(a, 0.3, 8.0, 14.0)
    if mode == "frame":
        inner = _frame_trim(a[t:b, l:r])
        if inner is not None:
            l, t, r, b = l + inner[0], t + inner[1], l + inner[2], t + inner[3]
            l2, t2, r2, b2 = _uniform_trim(a[t:b, l:r], 0.15, 8.0, 14.0)
            l, t, r, b = l + l2, t + t2, l + r2, t + b2
    if (r - l) < 0.4 * a.shape[1] or (b - t) < 0.4 * a.shape[0]:
        return (0, 0, img.width, img.height)  # refuse a crop that eats most of the picture
    if (l, t, r, b) == (0, 0, a.shape[1], a.shape[0]):
        return (0, 0, img.width, img.height)
    # one small-image pixel of safety margin inward, then back to full resolution
    inv = 1 / scale
    box = (
        min(img.width - 1, math.ceil((l + (l > 0)) * inv)),
        min(img.height - 1, math.ceil((t + (t > 0)) * inv)),
        max(1, math.floor((r - (r < a.shape[1])) * inv)),
        max(1, math.floor((b - (b < a.shape[0])) * inv)),
    )
    return box


def load_image(path: str | Path, autocrop: str = "none") -> Image.Image:
    """Load, convert to sRGB, optionally auto-crop. This is the only loader the features use."""
    with Image.open(path) as im:
        im.load()
        img = to_srgb(im)
    if autocrop != "none":
        img = img.crop(autocrop_box(img, autocrop))
    return img


# ---------------------------------------------------------------- statistics image


def stats_array(img: Image.Image, budget: int = 256 * 256) -> np.ndarray:
    """Float32 sRGB in [0, 1], HxWx3, about `budget` pixels, aspect ratio kept (box-filter resize)."""
    w, h = img.size
    s = math.sqrt(budget / (w * h))
    size = (max(8, round(w * s)), max(8, round(h * s)))
    if size != img.size:
        img = img.resize(size, Image.BOX if s < 1 else Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255.0


# ---------------------------------------------------------------- model inputs


def _norm(img: Image.Image, mean: tuple[float, ...], std: tuple[float, ...]) -> np.ndarray:
    a = np.asarray(img, dtype=np.float32) / 255.0
    a = (a - np.asarray(mean, np.float32)) / np.asarray(std, np.float32)
    return np.ascontiguousarray(a.transpose(2, 0, 1))


def n_tiles(aspect: float) -> int:
    """Number of square tiles along the long side for the `tile` view."""
    r = max(aspect, 1 / aspect)
    return int(min(5, max(1, math.ceil(r - 0.15))))


def model_views(
    img: Image.Image,
    size: int,
    view: str,
    mean: tuple[float, ...],
    std: tuple[float, ...],
    patch: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Model inputs for one painting.

    Returns (pixels [V, 3, H, W] float32, mask [V, H/patch, W/patch] bool). The mask is False on
    patches that are mostly letterbox padding, so patch statistics can leave them out.

    center  short side -> size, centre crop. Loses the ends of wide and tall paintings.
    squash  resize to size x size ignoring aspect (what SigLIP's own processor does).
    pad     long side -> size, centred on a square of the model's mean colour (zero after
            normalisation). Sees everything, at lower resolution for elongated paintings.
    tile    short side -> size, then n square crops evenly spaced end to end along the long side
            (n = ceil(aspect - 0.15), 1..5). Outputs are averaged by the caller. Sees everything
            at full resolution; no view sees the whole.
    native  keep the aspect ratio, about (size/patch)^2 patches in total, sides rounded to the
            patch size. Only for models that interpolate position embeddings (DINOv2).
    """
    w, h = img.size
    bic = Image.BICUBIC
    if view == "squash":
        px = _norm(img.resize((size, size), bic), mean, std)[None]
        return px, np.ones((1, size // patch, size // patch), bool)
    if view in ("center", "tile"):
        s = size / min(w, h)
        rw, rh = max(size, round(w * s)), max(size, round(h * s))
        r = img.resize((rw, rh), bic)
        k = 1 if view == "center" else n_tiles(w / h)
        if k == 1:
            offs = [((rw - size) // 2, (rh - size) // 2)]
        elif rw >= rh:
            offs = [(round(i * (rw - size) / (k - 1)), 0) for i in range(k)]
        else:
            offs = [(0, round(i * (rh - size) / (k - 1))) for i in range(k)]
        px = np.stack([_norm(r.crop((x, y, x + size, y + size)), mean, std) for x, y in offs])
        return px, np.ones((len(offs), size // patch, size // patch), bool)
    if view == "pad":
        s = size / max(w, h)
        rw, rh = max(1, round(w * s)), max(1, round(h * s))
        r = img.resize((rw, rh), bic)
        fill = tuple(int(round(m * 255)) for m in mean)
        canvas = Image.new("RGB", (size, size), fill)
        x0, y0 = (size - rw) // 2, (size - rh) // 2
        canvas.paste(r, (x0, y0))
        cover = np.zeros((size, size), np.float32)
        cover[y0 : y0 + rh, x0 : x0 + rw] = 1
        g = size // patch
        frac = cover[: g * patch, : g * patch].reshape(g, patch, g, patch).mean(axis=(1, 3))
        mask = frac >= 0.5
        if not mask.any():
            # A strip thinner than one patch (handscrolls beyond about 16:1) covers no patch by half,
            # which left the patch statistics empty (NaN). Keep the patches it covers most.
            mask = frac >= frac.max() - 1e-6
        return _norm(canvas, mean, std)[None], mask[None]
    if view == "native":
        n = (size // patch) ** 2
        gw = max(1, round(math.sqrt(n * w / h)))
        gh = max(1, round(n / gw))
        r = img.resize((gw * patch, gh * patch), bic)
        return _norm(r, mean, std)[None], np.ones((1, gh, gw), bool)
    raise ValueError(f"unknown view {view!r}; choose from {VIEWS}")
