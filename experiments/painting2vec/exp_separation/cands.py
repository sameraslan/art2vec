"""The candidate registry: name -> (pilot vectors on kept rows, versions vectors)."""

from __future__ import annotations

import numpy as np

from lib import equal_var_concat, residual, treat

FIRST = {"cls", "patch_mean", "embed", "style", "content", "backbone", "mean_early", "mean_mid", "mean_late"}
COLOUR_PARTS = ["palette_hist", "palette_sw", "lightness", "chroma", "hue"]
COMP_PARTS = ["grid8_an", "grid8_ap", "grid4_an", "grid4_ap", "symmetry+balance+edges+spectrum+aspect", "saliency"]


def default_pre(store, part):
    if store.startswith("colour") or store == "composition":
        return "z" if "+" in part and store == "composition" else "none"
    return "l2" if part in FIRST or part == "cls+patch_mean" else "z"


def repca(Zp, Zv, keep, k=128):
    mu = Zp[keep].mean(0)
    X = Zp[keep] - mu
    w, V = np.linalg.eigh((X.T @ X).astype(np.float64) / len(X))
    o = np.argsort(w)[::-1][:k]
    V = V[:, o].astype(np.float32)
    return (Zp - mu) @ V, (Zv - mu) @ V, np.maximum(w[o], 0)


class Cands:
    def __init__(self, keep):
        self.keep = keep
        self.memo = {}

    def base(self, store, part, pre=None, k=64, whiten=False):
        """Full-pilot [2000, k] and versions [355, k] for one stored or derived part."""
        t = treat(store, part, pre or default_pre(store, part), self.keep)
        return t.get(k, whiten)

    def composite(self, items, k=64, whiten=False):
        """Equal-variance concatenation of several (store, part) at 64 dims each, then PCA again."""
        key = ("comp", tuple(items))
        if key not in self.memo:
            blocks = [self.base(s, p, k=64) for s, p in items]
            blocks = [(a[:, :], b) for a, b in blocks]
            # scale on kept rows
            ps, vs = [], []
            for a, b in blocks:
                sc = np.sqrt(a[self.keep].var(0).sum()) + 1e-9
                ps.append(a / sc)
                vs.append(b / sc)
            self.memo[key] = repca(np.concatenate(ps, 1), np.concatenate(vs, 1), self.keep)
        P, V, w = self.memo[key]
        k = min(k, P.shape[1])
        s = 1 / np.sqrt(w[:k] + 1e-12) if whiten else 1.0
        return (P[:, :k] * s).astype(np.float32), (V[:, :k] * s).astype(np.float32)

    def colour(self, norm="lstd", **kw):
        return self.composite([(f"colour__{norm}", p) for p in COLOUR_PARTS], **kw)

    def composition(self, **kw):
        return self.composite([("composition", p) for p in COMP_PARTS], **kw)

    def resid(self, target, nuis_list, alpha=1.0):
        """target, nuis: (pilot, versions) pairs. Residual of target on the concatenated nuisances."""
        np_ = np.concatenate([n[0] for n in nuis_list], 1)
        nv = np.concatenate([n[1] for n in nuis_list], 1)
        return residual(target[0], target[1], np_, nv, self.keep, alpha)
