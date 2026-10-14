"""Shared code for the subject / manner separation experiment.

Everything here reads the precomputed feature stores. No model is run.
Labels (painter, year, movement, genre, depicts, museum, fame) are used for evaluation only,
except in the functions whose names start with `label_assisted_`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "painting2vec"
FEAT = DATA / "features"
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
IMG = DATA / "exp_separation"
CAND = IMG / "cand"
for _d in (OUT, IMG, CAND):
    _d.mkdir(parents=True, exist_ok=True)

GREY = ["Q106864313", "Q1778000", "Q2395137", "Q78727757", "Q78834676", "Q78875327", "Q78761942", "Q12615728"]

# ---------------------------------------------------------------------------- metadata

BROAD = {
    "portrait": "portrait", "self-portrait": "portrait", "group portrait": "portrait",
    "family portrait": "portrait", "double portrait": "portrait", "equestrian portrait": "portrait",
    "tronie": "portrait", "historiated portrait": "portrait", "portrait painting": "portrait",
    "full-length portrait": "portrait", "court painting": "portrait",
    "religious art": "narrative", "mythological painting": "narrative", "history painting": "narrative",
    "allegory": "narrative", "battle painting": "narrative", "Arthurian painting": "narrative",
    "Christian art": "narrative", "sacred art": "narrative", "Buddhist painting": "narrative",
    "Art of Manichaeism": "narrative", "literary painting": "narrative", "biblical art": "narrative",
    "genre art": "genre", "figure painting": "genre", "bijin-ga": "genre", "interior view": "genre",
    "landscape painting": "landscape", "cityscape": "landscape", "marine art": "landscape",
    "veduta": "landscape", "capriccio": "landscape", "shan shui": "landscape", "seascape": "landscape",
    "still life": "stilllife", "floral painting": "stilllife", "animal art": "stilllife",
    "bird-and-flower painting": "stilllife", "vanitas": "stilllife", "kachō-ga": "stilllife",
    "nude": "nude",
}


def _split(s) -> list[str]:
    if not isinstance(s, str) or not s:
        return []
    return [t for t in s.split("|") if t]


def load_pilot_meta() -> pd.DataFrame:
    """Pilot metadata in the row order of the feature stores, with a `keep` flag."""
    ids = (FEAT / "pilot" / "composition.ids.txt").read_text().split()
    m = pd.read_csv(DATA / "pilot" / "meta.csv").set_index("qid").loc[ids].reset_index()
    strip = np.minimum(m.px_width, m.px_height) < 100
    grey = m.qid.isin(GREY)
    m["strip"] = strip
    m["grey"] = grey
    m["keep"] = ~(strip | grey)
    m["genre_set"] = m.genres.map(_split)
    m["broad_set"] = m.genre_set.map(lambda g: sorted({BROAD[t] for t in g if t in BROAD}))
    m["move_set"] = m.movements.map(_split)
    m["dep_set"] = m.depicts.map(_split)
    m["painter"] = m.creator_qid.fillna("")
    return m


def load_versions():
    ids = (FEAT / "versions" / "composition.ids.txt").read_text().split()
    vm = pd.read_csv(DATA / "versions" / "meta.csv").set_index("qid")
    pairs = pd.read_csv(DATA / "versions" / "version_pairs.csv")
    ca = pairs.qid_a.map(vm.creator_qid).fillna("")
    cb = pairs.qid_b.map(vm.creator_qid).fillna("")
    hand = np.where((ca == "") | (cb == ""), "unknown", np.where(ca == cb, "same_hand", "other_hand"))
    pairs["hand"] = hand
    return ids, vm, pairs


def multihot(sets, min_count=1):
    vocab: dict[str, int] = {}
    cnt: dict[str, int] = {}
    for s in sets:
        for t in s:
            cnt[t] = cnt.get(t, 0) + 1
    for t, c in cnt.items():
        if c >= min_count:
            vocab[t] = len(vocab)
    M = np.zeros((len(sets), len(vocab)), dtype=np.float32)
    for i, s in enumerate(sets):
        for t in s:
            if t in vocab:
                M[i, vocab[t]] = 1
    return M, vocab


# ---------------------------------------------------------------------------- raw parts

_IU = np.triu_indices(24)
_OFF = _IU[0] != _IU[1]


def _gram_log(g: np.ndarray) -> np.ndarray:
    """300-number Gram triangle -> matrix logarithm of the 24x24 covariance, same packing.
    Euclidean distance between two of these is the log-Euclidean distance between covariances."""
    out = np.empty_like(g, dtype=np.float32)
    for i in range(len(g)):
        v = g[i].astype(np.float64).copy()
        v[_OFF] /= np.sqrt(2)
        C = np.zeros((24, 24))
        C[_IU] = v
        C = C + C.T - np.diag(np.diag(C))
        w, U = np.linalg.eigh(C)
        w = np.maximum(w, 1e-6 * max(w.max(), 1e-12))
        L = (U * np.log(w)) @ U.T
        t = L[_IU]
        t[_OFF] *= np.sqrt(2)
        out[i] = t
    return out


def raw_part(setname: str, store: str, part: str) -> np.ndarray:
    """One stored or derived part as float32 [N, D].

    Derived names: `mean_<layer>` and `std_<layer>` (the two halves of `meanstd_<layer>`),
    `gramlog_<layer>` (log-Euclidean form of `gram_<layer>`), `a+b+c` (plain concatenation).
    """
    if "+" in part:
        return np.concatenate([raw_part(setname, store, p) for p in part.split("+")], axis=1)
    with np.load(FEAT / setname / f"{store}.npz") as z:
        m = re.fullmatch(r"(mean|std)_(early|mid|late)", part)
        if m:
            x = z[f"meanstd_{m.group(2)}"].astype(np.float32)
            h = x.shape[1] // 2
            return x[:, :h] if m.group(1) == "mean" else x[:, h:]
        m = re.fullmatch(r"gramlog_(early|mid|late)", part)
        if m:
            return _gram_log(z[f"gram_{m.group(1)}"].astype(np.float32))
        x = z[part].astype(np.float32)
    return x.reshape(len(x), -1)


# ---------------------------------------------------------------------------- treatments


class Treated:
    """A candidate after pre-scaling, centring on the pilot mean and PCA (fit on kept pilot rows).

    `pilot` and `versions` hold up to 128 PCA scores (not whitened); `eig` the variances.
    """

    def __init__(self, pilot, versions, eig):
        self.pilot, self.versions, self.eig = pilot, versions, eig

    def get(self, k=64, whiten=False):
        k = min(k, self.pilot.shape[1])
        s = 1 / np.sqrt(self.eig[:k] + 1e-12) if whiten else 1.0
        return (self.pilot[:, :k] * s).astype(np.float32), (self.versions[:, :k] * s).astype(np.float32)


def treat(store: str, part: str, pre: str, keep: np.ndarray, kmax=128, cache=True) -> Treated:
    """pre: 'l2' (unit rows), 'z' (per-dimension z-score on kept pilot rows), 'zl2' (z then unit rows),
    'none'. Then centre on the kept-pilot mean and PCA."""
    key = re.sub(r"[^A-Za-z0-9_+]", "-", f"{store}__{part}__{pre}")
    f = CAND / f"{key}.npz"
    if cache and f.exists():
        with np.load(f) as z:
            return Treated(z["pilot"], z["versions"], z["eig"])
    xs = {s: raw_part(s, store, part) for s in ("pilot", "versions")}

    def unit(x):
        return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)

    if pre in ("z", "zl2"):
        mu, sd = xs["pilot"][keep].mean(0), xs["pilot"][keep].std(0)
        ok = sd > 1e-8
        xs = {s: ((x[:, ok] - mu[ok]) / sd[ok]) for s, x in xs.items()}
    if pre in ("l2", "zl2"):
        xs = {s: unit(x) for s, x in xs.items()}
    mu = xs["pilot"][keep].mean(0)
    xs = {s: (x - mu).astype(np.float32) for s, x in xs.items()}
    xp = xs["pilot"][keep]
    # PCA through the smaller Gram matrix
    if xp.shape[1] <= xp.shape[0]:
        C = (xp.T @ xp).astype(np.float64) / len(xp)
        w, V = np.linalg.eigh(C)
        o = np.argsort(w)[::-1][:kmax]
        w, V = w[o], V[:, o].astype(np.float32)
    else:
        G = (xp @ xp.T).astype(np.float64) / len(xp)
        w, U = np.linalg.eigh(G)
        o = np.argsort(w)[::-1][:kmax]
        w, U = w[o], U[:, o]
        V = (xp.T @ (U / np.sqrt(np.maximum(w, 1e-12) * len(xp)))).astype(np.float32)
    t = Treated(xs["pilot"] @ V, xs["versions"] @ V, np.maximum(w, 0).astype(np.float32))
    if cache:
        np.savez(f, pilot=t.pilot.astype(np.float32), versions=t.versions.astype(np.float32), eig=t.eig)
    return t


def cosdist(A: np.ndarray, B: np.ndarray | None = None) -> np.ndarray:
    a = A / np.maximum(np.linalg.norm(A, axis=1, keepdims=True), 1e-9)
    b = a if B is None else B / np.maximum(np.linalg.norm(B, axis=1, keepdims=True), 1e-9)
    return (1 - a @ b.T).astype(np.float32)


def ridge_fit(X, Y, alpha):
    d = X.shape[1]
    return np.linalg.solve(X.T @ X + alpha * np.eye(d, dtype=X.dtype), X.T @ Y)


def residual(target_p, target_v, nuis_p, nuis_v, keep, alpha=1.0):
    """Linear residual of `target` after ridge regression on `nuis` (fit on kept pilot rows)."""
    mu_t, mu_n = target_p[keep].mean(0), nuis_p[keep].mean(0)
    sd = nuis_p[keep].std(0) + 1e-9
    f = lambda n: (n - mu_n) / sd
    W = ridge_fit(f(nuis_p[keep]).astype(np.float64), (target_p[keep] - mu_t).astype(np.float64), alpha)
    rp = (target_p - mu_t) - f(nuis_p) @ W
    rv = (target_v - mu_t) - f(nuis_v) @ W
    return rp.astype(np.float32), rv.astype(np.float32)


def equal_var_concat(blocks):
    """Concatenate (pilot, versions) pairs after scaling each to unit total variance on the pilot."""
    ps, vs = [], []
    for p, v in blocks:
        s = np.sqrt(p.var(0).sum()) + 1e-9
        ps.append(p / s)
        vs.append(v / s)
    return np.concatenate(ps, 1), np.concatenate(vs, 1)


def dump(obj, name):
    (OUT / name).write_text(json.dumps(obj, indent=1, default=float))
