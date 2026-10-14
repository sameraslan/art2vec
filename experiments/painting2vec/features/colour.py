"""Colour block: palette and light, computed directly in OKLab. No trained model.

colour_features(rgb, norm) -> dict of named parts (see PARTS). Every part is a fixed-length
float32 vector meant to be compared with Euclidean distance, except `palette_kmeans`, which is a
weighted point set to be compared with `palette_emd`.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

NORMS = ("raw", "greyworld", "lstd", "std", "rank")

L_BINS, AB_BINS, AB_RANGE = 6, 9, 0.32
N_DIRS, N_QUANT = 24, 16
K_PALETTE = 6
HUE_BINS, LC_BINS, C_MAX = 24, 16, 0.32

PARTS = {
    "palette_hist": L_BINS * AB_BINS * AB_BINS,  # 486
    "palette_sw": N_DIRS * N_QUANT,  # 384
    "palette_kmeans": K_PALETTE * 4,  # 24
    "lightness": LC_BINS + 5,  # 21
    "chroma": LC_BINS + 5,  # 21
    "hue": HUE_BINS + 1,  # 25
}

_DIRS = np.random.RandomState(20261008).randn(N_DIRS, 3)
_DIRS /= np.linalg.norm(_DIRS, axis=1, keepdims=True)
_DIRS = _DIRS.astype(np.float32)


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4).astype(np.float32)


_M1 = np.array(
    [
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005],
    ],
    np.float32,
)
_M2 = np.array(
    [
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660],
    ],
    np.float32,
)


def linear_to_oklab(lin: np.ndarray) -> np.ndarray:
    lms = np.cbrt(np.clip(lin @ _M1.T, 0, None))
    return (lms @ _M2.T).astype(np.float32)


def srgb_to_oklab(rgb: np.ndarray, greyworld: bool = False) -> np.ndarray:
    """rgb: [..., 3] sRGB in [0, 1] -> OKLab (L in [0, 1], a and b roughly in [-0.3, 0.3])."""
    lin = srgb_to_linear(rgb)
    if greyworld:
        m = lin.reshape(-1, 3).mean(axis=0)
        gain = np.clip(m.mean() / np.maximum(m, 1e-4), 0.5, 2.0)  # capped: a red painting is not a cast
        lin = np.clip(lin * gain, 0, 1)
    return linear_to_oklab(lin)


def normalise(rgb: np.ndarray, norm: str) -> np.ndarray:
    """sRGB stats image -> [N, 3] OKLab pixels under one of the illuminant/exposure normalisations.

    raw        nothing.
    greyworld  linear-RGB channel gains so the three channel means are equal (gains capped 0.5..2).
    lstd       lightness standardised per image to mean 0.5, sd 0.2; a, b untouched.
    std        lstd, plus a and b centred on the image mean (removes a cast) and scaled so the RMS
               chroma is 0.1 (gain capped at 4). Drops how saturated the picture is overall.
    rank       histogram shape only: lightness replaced by its rank in the image (so any monotone
               tone curve is removed), a and b centred and scaled as in std.
    """
    if norm not in NORMS:
        raise ValueError(f"unknown colour normalisation {norm!r}; choose from {NORMS}")
    lab = srgb_to_oklab(rgb, greyworld=(norm == "greyworld")).reshape(-1, 3).copy()
    if norm in ("lstd", "std"):
        L = lab[:, 0]
        lab[:, 0] = np.clip(0.5 + 0.2 * (L - L.mean()) / max(float(L.std()), 0.02), 0, 1)
    if norm == "rank":
        order = np.argsort(lab[:, 0], kind="stable")
        ranks = np.empty(len(order), np.float32)
        ranks[order] = (np.arange(len(order), dtype=np.float32) + 0.5) / len(order)
        lab[:, 0] = ranks
    if norm in ("std", "rank"):
        ab = lab[:, 1:] - lab[:, 1:].mean(axis=0)
        rms = float(np.sqrt((ab**2).sum(axis=1).mean()))
        lab[:, 1:] = ab * min(4.0, 0.1 / max(rms, 1e-4))
    return lab


def _soft_hist(x: np.ndarray, lo: float, hi: float, bins: int, weights=None, circular=False) -> np.ndarray:
    """Linear-interpolation histogram: each sample is shared between its two nearest bin centres."""
    if circular:
        pos = (x - lo) / (hi - lo) * bins - 0.5
    else:
        pos = np.clip((x - lo) / (hi - lo) * bins - 0.5, 0, bins - 1)
    i0 = np.floor(pos).astype(np.int64)
    f = (pos - i0).astype(np.float32)
    w = np.ones_like(f) if weights is None else weights.astype(np.float32)
    if circular:
        a, b = i0 % bins, (i0 + 1) % bins
    else:
        a, b = i0, np.minimum(i0 + 1, bins - 1)
    h = np.bincount(a, w * (1 - f), bins) + np.bincount(b, w * f, bins)
    return h.astype(np.float32)


def _soft_hist3(lab: np.ndarray) -> np.ndarray:
    n = (L_BINS, AB_BINS, AB_BINS)
    lo = np.array([0.0, -AB_RANGE, -AB_RANGE], np.float32)
    hi = np.array([1.0, AB_RANGE, AB_RANGE], np.float32)
    nb = np.array(n, np.float32)
    pos = np.clip((lab - lo) / (hi - lo) * nb - 0.5, 0, nb - 1)
    i0 = np.floor(pos).astype(np.int64)
    f = pos - i0
    i1 = np.minimum(i0 + 1, np.array(n) - 1)
    h = np.zeros(n[0] * n[1] * n[2], np.float64)
    for cl in (0, 1):
        for ca in (0, 1):
            for cb in (0, 1):
                il = i1[:, 0] if cl else i0[:, 0]
                ia = i1[:, 1] if ca else i0[:, 1]
                ib = i1[:, 2] if cb else i0[:, 2]
                w = (
                    (f[:, 0] if cl else 1 - f[:, 0])
                    * (f[:, 1] if ca else 1 - f[:, 1])
                    * (f[:, 2] if cb else 1 - f[:, 2])
                )
                h += np.bincount((il * n[1] + ia) * n[2] + ib, w, h.size)
    return (h / h.sum()).astype(np.float32)


def _kmeans(lab: np.ndarray, k: int, iters: int = 12) -> np.ndarray:
    """Deterministic k-means++ palette. Returns [k, 4]: L, a, b, weight; heaviest first."""
    rs = np.random.RandomState(0)
    pts = lab[:: max(1, len(lab) // 8192)].astype(np.float64)
    cent = [pts[rs.randint(len(pts))]]
    d = ((pts - cent[0]) ** 2).sum(axis=1)
    for _ in range(k - 1):
        p = d / d.sum() if d.sum() > 0 else np.full(len(pts), 1 / len(pts))
        cent.append(pts[rs.choice(len(pts), p=p)])
        d = np.minimum(d, ((pts - cent[-1]) ** 2).sum(axis=1))
    c = np.array(cent)
    for _ in range(iters):
        a = ((pts[:, None] - c[None]) ** 2).sum(axis=2).argmin(axis=1)
        for j in range(k):
            if (a == j).any():
                c[j] = pts[a == j].mean(axis=0)
    a = ((pts[:, None] - c[None]) ** 2).sum(axis=2).argmin(axis=1)
    w = np.bincount(a, minlength=k) / len(pts)
    order = np.argsort(-w, kind="stable")
    return np.concatenate([c[order], w[order, None]], axis=1).astype(np.float32)


def palette_emd(p: np.ndarray, q: np.ndarray) -> float:
    """Exact earth mover's distance (W1, OKLab units) between two `palette_kmeans` vectors."""
    p, q = p.reshape(-1, 4).astype(np.float64), q.reshape(-1, 4).astype(np.float64)
    n, m = len(p), len(q)
    cost = np.linalg.norm(p[:, None, :3] - q[None, :, :3], axis=2).ravel()
    a_eq = np.zeros((n + m, n * m))
    for i in range(n):
        a_eq[i, i * m : (i + 1) * m] = 1
    for j in range(m):
        a_eq[n + j, j::m] = 1
    b_eq = np.concatenate([p[:, 3] / p[:, 3].sum(), q[:, 3] / q[:, 3].sum()])
    res = linprog(cost, A_eq=a_eq[:-1], b_eq=b_eq[:-1], bounds=(0, None), method="highs")
    return float(res.fun)


def _summary(x: np.ndarray) -> np.ndarray:
    q = np.percentile(x, [5, 50, 95])
    return np.array([x.mean(), x.std(), q[0], q[1], q[2]], np.float32)


def colour_features(rgb: np.ndarray, norm: str = "raw") -> dict[str, np.ndarray]:
    """rgb: stats image, HxWx3 sRGB in [0, 1]. Returns the parts listed in PARTS.

    palette_hist    486  soft 6x9x9 histogram over OKLab (L 0..1, a and b +-0.32), square-rooted, so
                         Euclidean distance is the Hellinger distance (x sqrt 2). Trilinear binning
                         makes a small colour shift a small move.
    palette_sw      384  sliced-Wasserstein embedding: the pixels projected on 24 fixed directions in
                         OKLab, 16 quantiles each, divided by sqrt(384). Euclidean distance between
                         two of these approximates the sliced 2-Wasserstein distance between the two
                         colour distributions, i.e. an earth mover's distance you can put in a vector.
    palette_kmeans   24  6 k-means colours (L, a, b, weight), heaviest first. Compare with
                         palette_emd(); Euclidean distance on this one is only a rough guide.
    lightness        21  soft 16-bin histogram of L (square-rooted) + mean, sd, 5th/50th/95th pct.
    chroma           21  the same for chroma C = hypot(a, b), bins over 0..0.32.
    hue              25  soft circular 24-bin hue histogram weighted by chroma (square-rooted, sums
                         to 1 before the root) + the share of pixels that are near-grey (C < 0.02).
    """
    lab = normalise(rgb, norm)
    L, a, b = lab[:, 0], lab[:, 1], lab[:, 2]
    C = np.hypot(a, b)
    out: dict[str, np.ndarray] = {}
    out["palette_hist"] = np.sqrt(_soft_hist3(lab))
    proj = lab @ _DIRS.T  # [N, dirs]
    qs = (np.arange(N_QUANT) + 0.5) / N_QUANT * 100
    out["palette_sw"] = (np.percentile(proj, qs, axis=0).T.ravel() / np.sqrt(N_DIRS * N_QUANT)).astype(np.float32)
    out["palette_kmeans"] = _kmeans(lab, K_PALETTE).ravel()
    hl = _soft_hist(L, 0, 1, LC_BINS)
    out["lightness"] = np.concatenate([np.sqrt(hl / hl.sum()), _summary(L)])
    hc = _soft_hist(C, 0, C_MAX, LC_BINS)
    out["chroma"] = np.concatenate([np.sqrt(hc / hc.sum()), _summary(C)])
    hue = np.arctan2(b, a)
    hh = _soft_hist(hue, -np.pi, np.pi, HUE_BINS, weights=C, circular=True)
    hh = hh / max(float(hh.sum()), 1e-8)
    out["hue"] = np.concatenate([np.sqrt(hh), [np.float32((C < 0.02).mean())]]).astype(np.float32)
    for k, v in out.items():
        assert v.shape == (PARTS[k],), (k, v.shape)
        out[k] = v.astype(np.float32)
    return out
