"""New colour descriptors meant to survive a different photograph of the same painting.

Pure numpy. `describe(rgb)` takes the stats image (HxWx3 sRGB in [0, 1], about 65k pixels) and
returns a dict of named float32 vectors. Histograms are stored as plain proportions (not rooted);
the evaluation decides the distance.

Chromatic adaptation (linear RGB gains, capped 0.5..2):
  raw   none
  sog   shades-of-grey: Minkowski p=6 mean of each channel made equal
  wp    white patch on the 97th percentile of each channel
Standardisation in OKLab:
  std   lightness to mean 0.5, sd 0.2; a, b centred on the image mean, RMS chroma set to 0.1
        (the invariance experiment's best)
  sca   lightness as std; a, b NOT centred, only divided so the RMS chroma is 0.1 (keeps the tint)
  rank  each of L, a, b replaced by its within-image rank (per-channel histogram standardisation)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "features"))
from colour import _DIRS, N_DIRS, N_QUANT, _soft_hist, linear_to_oklab, srgb_to_linear  # noqa: E402

WARM = np.deg2rad(55.0)  # OKLab hue of orange; the warm pole. The cool pole is opposite (blue).


def adapt(lin: np.ndarray, mode: str) -> np.ndarray:
    if mode == "raw":
        return lin
    flat = lin.reshape(-1, 3)
    if mode == "sog":
        m = np.power(np.power(flat, 6).mean(0), 1 / 6)
    elif mode == "wp":
        m = np.percentile(flat, 97, axis=0)
    else:
        raise ValueError(mode)
    gain = np.clip(m.mean() / np.maximum(m, 1e-4), 0.5, 2.0)
    return np.clip(lin * gain, 0, 1)


def _lstd(L):
    return np.clip(0.5 + 0.2 * (L - L.mean()) / max(float(L.std()), 0.02), 0, 1)


def _rank(x):
    o = np.argsort(x, kind="stable")
    r = np.empty(len(o), np.float32)
    r[o] = (np.arange(len(o), dtype=np.float32) + 0.5) / len(o)
    return r


def standardise(lab: np.ndarray, mode: str) -> np.ndarray:
    out = lab.copy()
    if mode in ("std", "sca"):
        out[:, 0] = _lstd(lab[:, 0])
        ab = lab[:, 1:] - (lab[:, 1:].mean(0) if mode == "std" else 0)
        rms = float(np.sqrt((ab**2).sum(1).mean()))
        out[:, 1:] = ab * min(4.0, 0.1 / max(rms, 1e-4))
    elif mode == "rank":
        for c in range(3):
            out[:, c] = _rank(lab[:, c])
    return out


def hist3(lab, n=(6, 9, 9), lo=(0.0, -0.32, -0.32), hi=(1.0, 0.32, 0.32)) -> np.ndarray:
    """Trilinear soft histogram, proportions."""
    lo, hi, nb = np.array(lo, np.float32), np.array(hi, np.float32), np.array(n, np.float32)
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
                w = (f[:, 0] if cl else 1 - f[:, 0]) * (f[:, 1] if ca else 1 - f[:, 1]) * (f[:, 2] if cb else 1 - f[:, 2])
                h += np.bincount((il * n[1] + ia) * n[2] + ib, w, h.size)
    return (h / h.sum()).astype(np.float32)


def sw(lab) -> np.ndarray:
    proj = lab @ _DIRS.T
    qs = (np.arange(N_QUANT) + 0.5) / N_QUANT * 100
    return (np.percentile(proj, qs, axis=0).T.ravel() / np.sqrt(N_DIRS * N_QUANT)).astype(np.float32)


def _chromatic_weight(C, lo, hi):
    t = np.clip((C - lo) / (hi - lo), 0, 1)
    return (t * t * (3 - 2 * t)).astype(np.float32)


def hue_family(lab, lo=0.02, hi=0.06):
    """12 hue families among sufficiently chromatic pixels (soft threshold on chroma), the
    chroma-weighted version, the 6 families x 3 lightness terciles table, the achromatic share."""
    a, b = lab[:, 1], lab[:, 2]
    C = np.hypot(a, b)
    w = _chromatic_weight(C, lo, hi)
    hue = np.arctan2(b, a)
    tot = max(float(w.sum()), 1e-6)
    h12 = _soft_hist(hue, -np.pi, np.pi, 12, weights=w, circular=True) / tot
    h12w = _soft_hist(hue, -np.pi, np.pi, 12, weights=C, circular=True)
    h12w = h12w / max(float(h12w.sum()), 1e-8)
    achrom = 1.0 - float(w.mean())
    lr = _rank(lab[:, 0])
    tab = []
    for t in range(3):
        m = (lr >= t / 3) & (lr < (t + 1) / 3 + 1e-9)
        tab.append(_soft_hist(hue[m], -np.pi, np.pi, 6, weights=w[m], circular=True) / tot)
    return h12.astype(np.float32), h12w.astype(np.float32), np.concatenate(tab).astype(np.float32), achrom


def warm_cool(lab, lo=0.02, hi=0.06):
    a, b = lab[:, 1], lab[:, 2]
    C = np.hypot(a, b)
    w = _chromatic_weight(C, lo, hi)
    warmth = a * np.cos(WARM) + b * np.sin(WARM)
    rms = max(float(np.sqrt((C**2).mean())), 1e-4)
    lr = _rank(lab[:, 0])
    hi_t, lo_t = lr > 2 / 3, lr < 1 / 3
    sw_, sl = float(warmth.std()), float(lab[:, 0].std())
    corr = float(np.corrcoef(lab[:, 0], warmth)[0, 1]) if sw_ > 1e-6 and sl > 1e-6 else 0.0
    return np.array(
        [
            float(warmth.sum() / max(C.sum(), 1e-6)),  # chroma-weighted balance, -1 cool .. +1 warm
            float((w * (warmth > 0)).sum() / max(w.sum(), 1e-6)),  # warm share of chromatic pixels
            corr,  # are the lights the warm part?
            float((warmth[hi_t].mean() - warmth[lo_t].mean()) / rms),  # lights minus darks, in chroma units
            1.0 - float(w.mean()),  # achromatic share
        ],
        np.float32,
    )


def tone_bands(lab, n=8):
    """The colour of each lightness band (band = equal share of pixels by lightness rank):
    mean a, mean b and mean chroma per band. Any monotone tone curve leaves the bands unchanged."""
    o = np.argsort(lab[:, 0], kind="stable")
    ab = lab[o, 1:]
    C = np.hypot(ab[:, 0], ab[:, 1])
    out = []
    for idx in np.array_split(np.arange(len(o)), n):
        out += [ab[idx, 0].mean(), ab[idx, 1].mean(), C[idx].mean()]
    return np.array(out, np.float32)


def rank_quantiles(lab_raw):
    L, C = lab_raw[:, 0], np.hypot(lab_raw[:, 1], lab_raw[:, 2])
    q = np.arange(10, 100, 10)
    lq = np.percentile(L, q)
    iqr = max(float(np.percentile(L, 75) - np.percentile(L, 25)), 0.02)
    lq = (lq - lq[4]) / iqr
    cq = np.percentile(C, q)
    cq = cq / max(float(cq[4]), 0.005)
    lr, cr = _rank(L), _rank(C)
    h = np.histogram2d(lr, cr, bins=4, range=[[0, 1], [0, 1]])[0].ravel() / len(L)
    return lq.astype(np.float32), np.clip(cq, 0, 8).astype(np.float32), h.astype(np.float32)


def copula(lab, n=4):
    r = np.stack([_rank(lab[:, c]) for c in range(3)], 1)
    i = np.minimum((r * n).astype(np.int64), n - 1)
    h = np.bincount((i[:, 0] * n + i[:, 1]) * n + i[:, 2], minlength=n**3)
    return (h / len(lab)).astype(np.float32)


def palette_rel(lab_std, k=5, iters=15):
    """k-means palette on standardised OKLab, ordered by lightness (L weighted 0.5 so the scales
    match). Returns the ordered palette (L, a, b, sqrt weight) and its internal spacing: the sorted
    pairwise distances over their mean, and the sorted weights."""
    rs = np.random.RandomState(0)
    pts = lab_std[:: max(1, len(lab_std) // 4096)].astype(np.float64).copy()
    pts[:, 0] *= 0.5
    cent = [pts[rs.randint(len(pts))]]
    d = ((pts - cent[0]) ** 2).sum(1)
    for _ in range(k - 1):
        p = d / d.sum() if d.sum() > 0 else np.full(len(pts), 1 / len(pts))
        cent.append(pts[rs.choice(len(pts), p=p)])
        d = np.minimum(d, ((pts - cent[-1]) ** 2).sum(1))
    c = np.array(cent)
    for _ in range(iters):
        a = ((pts[:, None] - c[None]) ** 2).sum(2).argmin(1)
        for j in range(k):
            if (a == j).any():
                c[j] = pts[a == j].mean(0)
    a = ((pts[:, None] - c[None]) ** 2).sum(2).argmin(1)
    w = np.bincount(a, minlength=k) / len(pts)
    o = np.argsort(c[:, 0], kind="stable")
    c, w = c[o], w[o]
    pd_ = np.sqrt(((c[:, None] - c[None]) ** 2).sum(2))[np.triu_indices(k, 1)]
    spacing = np.sort(pd_) / max(float(pd_.mean()), 1e-6)
    return (
        np.concatenate([c, np.sqrt(w)[:, None]], 1).ravel().astype(np.float32),
        np.concatenate([spacing, np.sort(w)[::-1]]).astype(np.float32),
    )


def layout(lab_hw, n=4):
    """n x n grid of mean (L, a, b), aspect-normalised."""
    H, W, _ = lab_hw.shape
    ys = np.linspace(0, H, n + 1).round().astype(int)
    xs = np.linspace(0, W, n + 1).round().astype(int)
    out = np.empty((n, n, 3), np.float32)
    for i in range(n):
        for j in range(n):
            out[i, j] = lab_hw[ys[i] : max(ys[i + 1], ys[i] + 1), xs[j] : max(xs[j + 1], xs[j] + 1)].reshape(-1, 3).mean(0)
    return out.ravel()


def describe(rgb: np.ndarray) -> dict[str, np.ndarray]:
    H, W, _ = rgb.shape
    lin = srgb_to_linear(rgb)
    out: dict[str, np.ndarray] = {}
    labs = {m: linear_to_oklab(adapt(lin, m)).reshape(-1, 3) for m in ("raw", "sog", "wp")}
    for m, lab in labs.items():
        s = standardise(lab, "std")
        out[f"hist_{m}_std"] = hist3(s)
        out[f"sw_{m}_std"] = sw(s)
        if m != "wp":
            out[f"histc_{m}_std"] = hist3(s, n=(3, 5, 5))
        sc = standardise(lab, "sca")
        if m != "wp":
            out[f"hist_{m}_sca"] = hist3(sc)
            out[f"histc_{m}_sca"] = hist3(sc, n=(3, 5, 5))
            out[f"sw_{m}_sca"] = sw(sc)
        # hue families and warm/cool on the adapted, unstandardised colours
        h12, h12w, tab, ach = hue_family(lab)
        out[f"hue12_{m}"] = np.concatenate([h12, [ach]]).astype(np.float32)
        out[f"hue12w_{m}"] = h12w
        out[f"hue6xL3_{m}"] = tab
        out[f"warm_{m}"] = warm_cool(lab)
        out[f"tb8_{m}_sca"] = tone_bands(sc, 8)
        if m == "raw":
            out["tb8_std"] = tone_bands(s, 8)
            out["tb5_std"] = tone_bands(s, 5)
            h12, h12w, tab, ach = hue_family(s, lo=0.03, hi=0.09)  # hue relative to the image's own mean colour
            out["hue12_cen"] = np.concatenate([h12, [ach]]).astype(np.float32)
            out["hue6xL3_cen"] = tab
            out["warm_cen"] = warm_cool(s, lo=0.03, hi=0.09)
            out["pal5_std"], out["pal5_spacing"] = palette_rel(s, 5)
            out["pal4_std"], out["pal4_spacing"] = palette_rel(s, 4)
            out["layout4_std"] = layout(s.reshape(H, W, 3), 4)
            out["layout6_std"] = layout(s.reshape(H, W, 3), 6)
            out["lq"], out["cq"], out["lc_copula"] = rank_quantiles(lab)
            out["copula4"] = copula(lab, 4)
            out["copula3"] = copula(lab, 3)
            out["hist_rank"] = hist3(standardise(lab, "rank"), n=(4, 6, 6), lo=(0, 0, 0), hi=(1, 1, 1))
        if m == "sog":
            out["layout4_sog_sca"] = layout(sc.reshape(H, W, 3), 4)
    return out
