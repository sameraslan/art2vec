"""Shared code for the fusion experiment. Reads feature stores only; no model is run.

Row universes: pilot (2,000, of which `keep` = 1,972 are used), repro (689), versions (355).
Every fit (mean, scale, PCA) is on the kept pilot rows.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data" / "painting2vec"
FEAT = DATA / "features"
OUT = DATA / "exp_fusion"
RES = HERE / "results"
DEMO = DATA / "demo"
for _d in (OUT, RES):
    _d.mkdir(parents=True, exist_ok=True)
NP = 2000
SETS = ("pilot", "repro", "versions")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(HERE.parent / "exp_separation"))
seplib = _load("lib", HERE.parent / "exp_separation" / "lib.py")
inv = _load("inv_common", HERE.parent / "exp_invariance" / "common.py")


def meta():
    return seplib.load_pilot_meta()


def store(setname: str, name: str, part: str) -> np.ndarray:
    with np.load(FEAT / setname / f"{name}.npz") as z:
        return z[part].astype(np.float32)


def colour2(setname: str, part: str, ac: str = "none") -> np.ndarray:
    with np.load(OUT / "colour2" / f"{setname}__{ac}.npz") as z:
        return z[part].astype(np.float32)


def colour2_parts(ac="none"):
    with np.load(OUT / "colour2" / f"pilot__{ac}.npz") as z:
        return [k for k in z.files if k != "cropped"]


def unit(a):
    return a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)


def sqdist(a, b=None):
    b = a if b is None else b
    d2 = (a * a).sum(1)[:, None] + (b * b).sum(1)[None, :] - 2.0 * (a @ b.T)
    np.maximum(d2, 0, out=d2)
    return d2.astype(np.float32)


class Fit:
    """pre-scale -> centre -> PCA(k) -> optional whiten -> optional unit rows. Fitted on `xfit`."""

    def __init__(self, xfit, pre="none", k=None, whiten=False, unit_out=False):
        self.pre, self.whiten, self.unit_out = pre, whiten, unit_out
        x = xfit.astype(np.float32)
        if pre == "z":
            self.m0, self.s0 = x.mean(0), x.std(0)
            self.ok = self.s0 > 1e-8 * max(float(self.s0.max()), 1e-30)
        x = self._pre(x)
        self.mu = x.mean(0)
        xc = (x - self.mu).astype(np.float64)
        n, d = xc.shape
        if k is None:
            self.V, self.sd, self.eig = None, None, None
            return
        if d <= n:
            w, V = np.linalg.eigh(xc.T @ xc / n)
            o = np.argsort(w)[::-1]
            w, V = w[o], V[:, o]
        else:
            w, U = np.linalg.eigh(xc @ xc.T / n)
            o = np.argsort(w)[::-1]
            w, U = w[o], U[:, o]
            V = xc.T @ (U[:, : n - 1] / np.sqrt(np.maximum(w[: n - 1], 1e-30) * n))
        w = np.maximum(w, 0)
        # never keep a direction with (numerically) no variance
        live = int((w > 1e-10 * w[0]).sum())
        k = min(k, live, V.shape[1])
        self.eig = w
        self.V = V[:, :k].astype(np.float32)
        self.sd = np.sqrt(np.maximum(w[:k], 1e-30)).astype(np.float32)

    def _pre(self, x):
        if self.pre == "l2":
            return unit(x)
        if self.pre == "z":
            return (x[:, self.ok] - self.m0[self.ok]) / self.s0[self.ok]
        if self.pre == "sqrt":
            return np.sqrt(np.maximum(x, 0))
        return x

    def __call__(self, x):
        z = self._pre(x.astype(np.float32)) - self.mu
        if self.V is not None:
            z = z @ self.V
            if self.whiten:
                z = z / self.sd
        if self.unit_out:
            z = unit(z)
        return z.astype(np.float32)


def scaled_concat(parts: list[np.ndarray], keep_rows: np.ndarray) -> np.ndarray:
    """Join parts after dividing each by the root of its total variance on the fit rows."""
    out = []
    for p in parts:
        f = p[keep_rows]
        s = float(np.sqrt(((f - f.mean(0)) ** 2).sum(1).mean()))
        out.append(p / (s if s > 0 else 1.0))
    return np.concatenate(out, 1)


def participation_ratio(x):
    xc = (x - x.mean(0)).astype(np.float64)
    g = xc.T @ xc if xc.shape[1] <= xc.shape[0] else xc @ xc.T
    return float(np.trace(g) ** 2 / max((g * g).sum(), 1e-30))


def topk(D, k=10, exclude_self=True):
    D = D.copy()
    if exclude_self:
        np.fill_diagonal(D, np.inf)
    idx = np.argpartition(D, k, axis=1)[:, :k]
    o = np.argsort(np.take_along_axis(D, idx, 1), axis=1, kind="stable")
    return np.take_along_axis(idx, o, 1)


def overlap(a, b):
    """Mean share of list a's entries that are also in list b (same k)."""
    return float(np.mean([len(set(x) & set(y)) for x, y in zip(a.tolist(), b.tolist())]) / a.shape[1])


class InvEval:
    """The invariance experiment's protocol, with the 28 excluded pilot rows removed from every pool."""

    def __init__(self):
        self.u = inv.Universe()
        self.keep = meta().keep.values
        u = self.u
        self.col = np.concatenate([self.keep, u.pool[NP:]])
        excl = set(np.array(u.pilot_ids)[~self.keep])
        self.pair_ok = np.array([r["qid"] not in excl for r in u.pairs])
        self.clean = u.primary & (u.flag == "none") & self.pair_ok
        self.primary = u.primary & self.pair_ok

    def run(self, xp, xr):
        """xp [2000, d] pilot, xr [689, d] repro, Euclidean. Returns per-pair dict and set-level dict."""
        u = self.u
        x = np.concatenate([xp, xr], 0)
        dq = np.sqrt(sqdist(xr, x))
        dpool = np.where(self.col[None, :] & ~u.same, dq, np.inf)
        nn_other = dpool.min(1)
        dpil = np.where(self.keep[None, :] & ~u.same[:, :NP], dq[:, :NP], np.inf)
        top = np.argsort(dpil, axis=1, kind="stable")[:, :10]
        dab, dba = dq[u.pa, NP + u.pb], dq[u.pb, NP + u.pa]
        pp = {
            "rank_ab": 1 + (dpool[u.pa] < dab[:, None]).sum(1),
            "rank_ba": 1 + (dpool[u.pb] < dba[:, None]).sum(1),
            "rnn_ab": dab / np.maximum(nn_other[u.pa], 1e-12),
            "rnn_ba": dba / np.maximum(nn_other[u.pb], 1e-12),
            "ov10": np.array([len(set(top[a].tolist()) & set(top[b].tolist())) / 10 for a, b in zip(u.pa, u.pb)]),
            "d": 0.5 * (dab + dba),
        }
        xk = xp[self.keep]
        dpp = np.sqrt(sqdist(xk))
        np.fill_diagonal(dpp, np.inf)
        two = np.partition(dpp, 1, axis=1)[:, :2]
        ok = (two[:, 0] > 0) & np.isfinite(two[:, 1])
        sl = {
            "med_nn": float(np.median(two[:, 0])),
            "twonn": float(ok.sum() / max(np.log(two[ok, 1] / two[ok, 0]).sum(), 1e-12)),
            "pr": participation_ratio(xk),
        }
        pp["rstep"] = pp["d"] / max(sl["med_nn"], 1e-12)
        return pp, sl, dpp

    @staticmethod
    def summ(pp, mask):
        rk = np.concatenate([pp["rank_ab"][mask], pp["rank_ba"][mask]])
        rn = np.concatenate([pp["rnn_ab"][mask], pp["rnn_ba"][mask]])
        return {
            "n": int(mask.sum()),
            "r1": float((rk <= 1).mean()),
            "r10": float((rk <= 10).mean()),
            "rnn_med": float(np.median(rn)),
            "rnn_p90": float(np.percentile(rn, 90)),
            "under_step": float((pp["rstep"][mask] < 1).mean()),
            "ov10": float(pp["ov10"][mask].mean()),
        }


def dump(obj, name):
    (RES / name).write_text(json.dumps(obj, indent=1, default=float))


def load(name):
    return json.loads((RES / name).read_text())
