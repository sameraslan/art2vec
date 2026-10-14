"""Composition block: where things sit. Computed directly; no trained model.

composition_features(rgb) -> dict of named parts (see PARTS), each a fixed-length float32 vector,
kept separate so they can be ablated.
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from scipy import ndimage

from .colour import srgb_to_oklab

ORI_BINS = 8
PARTS = {
    "grid8_an": 192,  # 8x8 x (lightness, chroma, edge energy), aspect-normalised
    "grid4_an": 48,
    "grid8_ap": 192,  # the same on a square canvas with the painting letterboxed (aspect kept)
    "grid4_ap": 48,
    "symmetry": 6,
    "balance": 9,
    "edges": 13,
    "spectrum": 3,
    "saliency": 67,
    "aspect": 1,
}


def _resize(m: np.ndarray, w: int, h: int) -> np.ndarray:
    return np.asarray(Image.fromarray(m.astype(np.float32), "F").resize((w, h), Image.BOX))


def _letterbox(m: np.ndarray) -> np.ndarray:
    h, w = m.shape
    s = max(h, w)
    c = np.zeros((s, s), np.float32)
    y, x = (s - h) // 2, (s - w) // 2
    c[y : y + h, x : x + w] = m
    return c


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a - a.mean(), b - b.mean()
    d = float(np.sqrt((a**2).sum() * (b**2).sum()))
    return float((a * b).sum() / d) if d > 1e-12 else 1.0


def _mass_stats(m: np.ndarray) -> list[float]:
    """Centre of mass (x, y in -1..1, 0 = centre) and radial spread of a non-negative map."""
    h, w = m.shape
    m = np.clip(m, 0, None) + 1e-12
    m = m / m.sum()
    ys = (np.arange(h) + 0.5) / h * 2 - 1
    xs = (np.arange(w) + 0.5) / w * 2 - 1
    cx, cy = float((m.sum(axis=0) * xs).sum()), float((m.sum(axis=1) * ys).sum())
    r2 = (xs[None] - cx) ** 2 + (ys[:, None] - cy) ** 2
    return [cx, cy, float(np.sqrt((m * r2).sum()))]


def _spectrum(L: np.ndarray) -> np.ndarray:
    h, w = L.shape
    win = np.hanning(h)[:, None] * np.hanning(w)[None]
    p = np.abs(np.fft.fft2((L - L.mean()) * win)) ** 2
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None]
    f = np.hypot(fx, fy)
    sel = (f >= 0.02) & (f <= 0.35)
    edges = np.geomspace(0.02, 0.35, 13)
    idx = np.digitize(f[sel], edges) - 1
    ps = p[sel]
    xs, ys = [], []
    for i in range(12):
        v = ps[idx == i]
        if v.size:
            xs.append(np.log(np.sqrt(edges[i] * edges[i + 1])))
            ys.append(np.log(v.mean() + 1e-20))
    slope, icpt = np.polyfit(xs, ys, 1)
    ang = np.abs(np.arctan2(np.broadcast_to(fy, f.shape), np.broadcast_to(fx, f.shape)))
    horiz_f = sel & ((ang < np.pi / 8) | (ang > 7 * np.pi / 8))  # variation along x: vertical structure
    vert_f = sel & (np.abs(ang - np.pi / 2) < np.pi / 8)  # variation along y: horizontal structure
    aniso = np.log((p[vert_f].mean() + 1e-20) / (p[horiz_f].mean() + 1e-20))
    return np.array([slope, slope * np.log(0.1) + icpt, aniso], np.float32)


def _saliency(L: np.ndarray) -> np.ndarray:
    """Spectral-residual saliency (Hou and Zhang 2007) on a 64x64 aspect-normalised lightness map."""
    s = _resize(L, 64, 64)
    F = np.fft.fft2(s)
    la = np.log(np.abs(F) + 1e-8)
    resid = la - ndimage.uniform_filter(la, 3, mode="wrap")
    sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * np.angle(F)))) ** 2
    sal = ndimage.gaussian_filter(sal, 2.5)
    return (sal / sal.sum()).astype(np.float32)


def composition_features(rgb: np.ndarray) -> dict[str, np.ndarray]:
    """rgb: stats image, HxWx3 sRGB in [0, 1] (aspect kept). Returns the parts listed in PARTS.

    Three maps are used throughout: lightness L and chroma C in OKLab, and edge energy E. L and C
    are standardised per image (minus the image mean, over the image sd); E is the Sobel gradient
    magnitude of the standardised L and, for the grids, is divided by its image mean, minus 1. The grids therefore say
    where the light, the colour and the detail are relative to the rest of the picture; absolute
    levels live in the colour block. That also makes them indifferent to exposure and contrast.

    grid8_an, grid4_an  192, 48  cell means on an 8x8 / 4x4 grid stretched over the painting, so
                                 cell (0, 0) is always the top-left corner whatever the shape.
                                 Order: L cells row-major, then C, then E.
    grid8_ap, grid4_ap  192, 48  the same after letterboxing the painting onto a square canvas
                                 (padding = 0 = the image mean), so shape is part of the layout.
    symmetry              6      correlation of a 16x16 map with its mirror: left-right for L, C, E,
                                 then up-down for L, C, E. 1 = symmetric.
    balance               9      centre of mass x, y (-1..1; x right, y down) and radial spread, for
                                 three weightings: edge energy, chroma, and |L - mean L|.
    edges                13      mean gradient magnitude (of standardised L, in sd per pixel); share of pixels over 0.2;
                                 8-bin edge-orientation histogram weighted by magnitude (square
                                 root; bin 0 = vertical edges, turning through 180 degrees);
                                 orientation entropy (0..1); share of 8x8 cells that are empty
                                 (edge energy under a quarter of the mean); entropy of edge energy
                                 across the 8x8 cells (0..1; 1 = detail spread evenly).
    spectrum              3      slope of the radially averaged power spectrum of standardised L on log-log axes
                                 (0.02..0.35 cycles per pixel); log power at 0.1 c/px; log ratio of
                                 power in horizontal structure to vertical structure.
    saliency             67      spectral-residual saliency: 8x8 grid (square-rooted, sums to 1
                                 before the root), its centre of mass x, y, and its entropy (0..1).
    aspect                1      log(width / height).
    Not covered: depth against flatness (needs a trained depth model).
    """
    h, w, _ = rgb.shape
    lab = srgb_to_oklab(rgb)
    L, C = lab[..., 0], np.hypot(lab[..., 1], lab[..., 2])
    Ls = (L - L.mean()) / max(float(L.std()), 0.02)
    # gradients of the standardised lightness, so a contrast change does not read as more edges
    gx = ndimage.sobel(Ls, axis=1, mode="nearest") / 8.0
    gy = ndimage.sobel(Ls, axis=0, mode="nearest") / 8.0
    E = np.hypot(gx, gy)

    Cs = (C - C.mean()) / max(float(C.std()), 0.005)
    Es = E / max(float(E.mean()), 1e-4) - 1
    maps = (Ls, Cs, Es)

    out: dict[str, np.ndarray] = {}
    for g in (8, 4):
        out[f"grid{g}_an"] = np.concatenate([_resize(m, g, g).ravel() for m in maps])
        out[f"grid{g}_ap"] = np.concatenate([_resize(_letterbox(m), g, g).ravel() for m in maps])

    small = [_resize(m, 16, 16) for m in maps]
    out["symmetry"] = np.array(
        [_corr(m, m[:, ::-1]) for m in small] + [_corr(m, m[::-1]) for m in small], np.float32
    )

    contrast = np.abs(Ls)
    out["balance"] = np.array(
        _mass_stats(_resize(E, 32, 32)) + _mass_stats(_resize(C, 32, 32)) + _mass_stats(_resize(contrast, 32, 32)),
        np.float32,
    )

    theta = np.mod(np.arctan2(gy, gx), np.pi)  # gradient direction; 0 = a vertical edge
    pos = theta / np.pi * ORI_BINS
    i0 = np.floor(pos).astype(np.int64) % ORI_BINS
    f = pos - np.floor(pos)
    oh = np.bincount(i0.ravel(), (E * (1 - f)).ravel(), ORI_BINS) + np.bincount(
        ((i0 + 1) % ORI_BINS).ravel(), (E * f).ravel(), ORI_BINS
    )
    oh = oh / max(float(oh.sum()), 1e-12)
    ori_ent = float(-(oh * np.log(oh + 1e-12)).sum() / np.log(ORI_BINS))
    cells = _resize(E, 8, 8).ravel()
    cp = cells / max(float(cells.sum()), 1e-12)
    out["edges"] = np.concatenate(
        [
            [E.mean(), (E > 0.2).mean()],
            np.sqrt(oh),
            [ori_ent, (cells < 0.25 * cells.mean()).mean(), -(cp * np.log(cp + 1e-12)).sum() / np.log(64)],
        ]
    ).astype(np.float32)

    out["spectrum"] = _spectrum(Ls)

    sal = _saliency(L)
    sg = sal.reshape(8, 8, 8, 8).sum(axis=(1, 3)).ravel()
    ms = _mass_stats(sal)
    ent = float(-(sg * np.log(sg + 1e-12)).sum() / np.log(64))
    out["saliency"] = np.concatenate([np.sqrt(sg), [ms[0], ms[1], ent]]).astype(np.float32)

    out["aspect"] = np.array([np.log(w / h)], np.float32)
    for k, v in out.items():
        assert v.shape == (PARTS[k],), (k, v.shape)
        out[k] = np.asarray(v, np.float32)
    return out
