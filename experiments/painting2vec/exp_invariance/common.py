"""Shared machinery for experiment 2: how much does the photograph move a painting?

Universe of rows = pilot (2,000) followed by repro (689). A repro row `<qid>__commons` is the
pilot file itself (hard link), so those rows are queries only and never distractors; the pilot row
of a query's own qid is excluded by qid. All distances are Euclidean-type: cosine is turned into
the chord distance sqrt(2 - 2 cos), which ranks identically and keeps ratios comparable.

Memory: nothing larger than 2,000 x 2,000 or 689 x 2,689 float32 is ever built.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import scipy.linalg

ROOT = Path(__file__).resolve().parents[3]
FEAT = ROOT / "data" / "painting2vec" / "features"
DATA = ROOT / "data" / "painting2vec"
OUT = DATA / "exp_invariance"
HERE = Path(__file__).resolve().parent
DATASET = HERE.parent / "dataset"

NP = 2000  # pilot rows come first


def read_ids(d: Path, store: str) -> list[str]:
    return (d / f"{store}.ids.txt").read_text().split()


class Universe:
    def __init__(self) -> None:
        self.pilot_ids = read_ids(FEAT / "pilot", "composition")
        self.repro_ids = read_ids(FEAT / "repro", "composition")
        self.version_ids = read_ids(FEAT / "versions", "composition")
        assert len(self.pilot_ids) == NP
        self.nr = len(self.repro_ids)
        self.qid = np.array(self.pilot_ids + [r.split("__")[0] for r in self.repro_ids])
        self.src = np.array(["pilot"] * NP + [r.split("__")[1] for r in self.repro_ids])
        self.pool = np.ones(NP + self.nr, bool)
        self.pool[NP:] = self.src[NP:] != "commons"  # the commons file IS the pilot row
        rix = {r: i for i, r in enumerate(self.repro_ids)}
        rows = list(csv.DictReader(open(DATASET / "repro_pairs.csv")))
        self.pairs = rows
        self.pa = np.array([rix[r["file_a"][:-4]] for r in rows])  # indices into repro rows
        self.pb = np.array([rix[r["file_b"][:-4]] for r in rows])
        self.primary = np.array([r["pair_kind"] == "primary" for r in rows])
        self.flag = np.array([r["flag"] or "none" for r in rows])
        self.lab = np.array([float(r["lab_diff"]) for r in rows])
        self.srcpair = np.array([f'{r["source_a"]}|{r["source_b"]}' for r in rows])
        self.same = self.qid[NP:, None] == self.qid[None, :]  # [nr, NP+nr]
        # version pairs (both images present in the versions store)
        vix = {v: i for i, v in enumerate(self.version_ids)}
        vr = [r for r in csv.DictReader(open(DATASET / "version_pairs.csv")) if r["qid_a"] in vix and r["qid_b"] in vix]
        self.vpairs = vr
        self.va = np.array([vix[r["qid_a"]] for r in vr])
        self.vb = np.array([vix[r["qid_b"]] for r in vr])
        self.vyes = np.array([r["composition_match"] == "yes" for r in vr])
        self.vlab = np.array([float(r["lab_diff"]) if r["lab_diff"] else np.nan for r in vr])


def load_part(setdir: str, store: str, part: str) -> np.ndarray:
    with np.load(FEAT / setdir / f"{store}.npz") as z:
        return z[part].astype(np.float32)


def load_univ(store: str, part: str, repro_dir: str = "repro", versions: bool = True):
    """[2689, d] pilot+repro, and the versions rows [355, d]."""
    x = np.concatenate([load_part("pilot", store, part), load_part(repro_dir, store, part)], 0)
    v = load_part("versions", store, part) if versions else None
    return x, v


# ------------------------------------------------------------------ distances


def d_euc(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aa = (a * a).sum(1)[:, None]
    bb = (b * b).sum(1)[None, :]
    d2 = aa + bb - 2.0 * (a @ b.T)
    np.maximum(d2, 0, out=d2)
    return np.sqrt(d2, dtype=np.float32)


def unit(a: np.ndarray) -> np.ndarray:
    return a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)


def d_cos(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return d_euc(unit(a), unit(b))


def d_l1(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.empty((len(a), len(b)), np.float32)
    step = max(1, int(2e7 // (len(b) * a.shape[1])))
    for i in range(0, len(a), step):
        out[i : i + step] = np.abs(a[i : i + step, None, :] - b[None, :, :]).sum(2)
    return out


def d_circ_emd(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular W1 between histograms on a ring: sum |F - G - median(F - G)| over the cdf."""
    ca, cb = np.cumsum(a, 1), np.cumsum(b, 1)
    out = np.empty((len(a), len(b)), np.float32)
    step = max(1, int(1e7 // (len(b) * a.shape[1])))
    for i in range(0, len(a), step):
        d = ca[i : i + step, None, :] - cb[None, :, :]
        d = d - np.median(d, axis=2, keepdims=True)
        out[i : i + step] = np.abs(d).sum(2)
    return out / a.shape[1]


def d_sinkhorn(a: np.ndarray, b: np.ndarray, eps: float = 0.02, iters: int = 80) -> np.ndarray:
    """Approximate EMD between k-means palettes [n, 24] = 6 x (L, a, b, weight). Entropic OT."""
    pa, pb = a.reshape(len(a), 6, 4).astype(np.float64), b.reshape(len(b), 6, 4).astype(np.float64)
    wa = pa[:, :, 3] / pa[:, :, 3].sum(1, keepdims=True)
    wb = pb[:, :, 3] / pb[:, :, 3].sum(1, keepdims=True)
    out = np.empty((len(a), len(b)), np.float32)
    step = 16  # 64 peaked at 1.4 GB RSS
    for i in range(0, len(a), step):
        A, WA = pa[i : i + step, :, :3], wa[i : i + step]
        C = np.linalg.norm(A[:, None, :, None, :] - pb[None, :, None, :, :3], axis=4)  # [s, nb, 6, 6]
        K = np.exp(-C / eps)
        u = np.ones((len(A), len(b), 6))
        r = np.broadcast_to(WA[:, None, :], u.shape)
        c = np.broadcast_to(wb[None, :, :], u.shape)
        for _ in range(iters):
            v = c / np.maximum(np.einsum("xyij,xyi->xyj", K, u), 1e-300)
            u = r / np.maximum(np.einsum("xyij,xyj->xyi", K, v), 1e-300)
        out[i : i + step] = np.einsum("xyi,xyij,xyj->xy", u, K * C, v)
    return out


METRICS = {"euc": d_euc, "cos": d_cos, "l1": d_l1, "circ_emd": d_circ_emd, "sinkhorn": d_sinkhorn}


# ------------------------------------------------------------------ treatments (fitted on pilot only)


def scale_part(x: np.ndarray, v: np.ndarray | None):
    """Divide a part by the root of its total variance on the pilot set (FRAMEWORK section 3)."""
    mu = x[:NP].mean(0)
    s = float(np.sqrt(((x[:NP] - mu) ** 2).sum(1).mean()))
    s = s if s > 0 else 1.0
    return x / s, (None if v is None else v / s)


def concat_scaled(parts):
    xs, vs = zip(*[scale_part(x, v) for x, v in parts])
    return np.concatenate(xs, 1), (None if vs[0] is None else np.concatenate(vs, 1))


class PCA:
    def __init__(self, base_pilot: np.ndarray, kmax: int = 128) -> None:
        self.mu = base_pilot.mean(0)
        xc = (base_pilot - self.mu).astype(np.float64)
        n, d = xc.shape
        if d <= n:
            w, vecs = scipy.linalg.eigh(xc.T @ xc)
            w, vecs = w[::-1], vecs[:, ::-1]
        else:
            w, u = scipy.linalg.eigh(xc @ xc.T)
            w, u = w[::-1], u[:, ::-1]
            k = min(kmax, n - 1)
            vecs = xc.T @ u[:, :k] / np.sqrt(np.maximum(w[:k], 1e-30))
        w = np.maximum(w, 0)
        self.eig = w / (n - 1)
        self.k = min(kmax, vecs.shape[1])
        self.comp = vecs[:, : self.k].astype(np.float32)
        self.sd = np.sqrt(np.maximum(self.eig[: self.k], 1e-20)).astype(np.float32)
        self.pr = float(self.eig.sum() ** 2 / max((self.eig**2).sum(), 1e-30))

    def tr(self, x: np.ndarray, k: int, whiten: bool) -> np.ndarray:
        z = (x - self.mu) @ self.comp[:, :k]
        return z / self.sd[:k] if whiten else z


def participation_ratio(xp: np.ndarray) -> float:
    xc = (xp - xp.mean(0)).astype(np.float64)
    g = xc @ xc.T if xc.shape[1] > xc.shape[0] else xc.T @ xc
    tr = np.trace(g)
    return float(tr * tr / max((g * g).sum(), 1e-30))


def treatments(x: np.ndarray, v: np.ndarray | None, learned: bool, which=None):
    """Yield (name, metric, X', V', participation ratio on pilot) for the standard treatments."""
    want = lambda n: which is None or n in which  # noqa: E731
    vv = (lambda f: None if v is None else f(v))
    if want("euc"):
        yield "euc", "euc", x, v, participation_ratio(x[:NP])
    if want("cos"):
        yield "cos", "cos", x, v, participation_ratio(unit(x[:NP]))
    xn = unit(x)
    mu = xn[:NP].mean(0)
    xc = xn - mu
    vc = vv(lambda a: unit(a) - mu)
    if want("cen"):
        yield "cen", "cos", xc, vc, participation_ratio(xc[:NP])
    if want("zs"):
        m, s = x[:NP].mean(0), x[:NP].std(0)
        keep = s > 1e-8 * max(float(s.max()), 1e-30)
        f = lambda a: (a[:, keep] - m[keep]) / s[keep]  # noqa: E731
        z = f(x)
        yield "zs", "euc", z, vv(f), participation_ratio(z[:NP])
    ks = [k for k in (32, 64, 128) if which is None or f"pca{k}" in which or f"pca{k}w" in which]
    if ks:
        base, vbase = (xc, vc) if learned else (x, v)
        metric = "cos" if learned else "euc"
        p = PCA(base[:NP], kmax=max(ks))
        for k in ks:
            if k > min(p.k, x.shape[1] - 1):
                continue
            for wh in (False, True):
                name = f"pca{k}{'w' if wh else ''}"
                if not want(name):
                    continue
                z = p.tr(base, k, wh)
                yield name, metric, z, (None if vbase is None else p.tr(vbase, k, wh)), participation_ratio(z[:NP])


# ------------------------------------------------------------------ evaluation

PERPAIR = ["rank_ab", "rank_ba", "rnn_ab", "rnn_ba", "rstep", "jacc", "rbo", "ov10", "d_ab"]


def rbo_ext(a: np.ndarray, b: np.ndarray, p: float = 0.9) -> float:
    """Extrapolated rank-biased overlap (Webber et al. 2010, eq. 32) for two equal-length lists."""
    k = len(a)
    sa, sb, x, s = set(), set(), 0, 0.0
    for d in range(1, k + 1):
        ai, bi = a[d - 1], b[d - 1]
        if ai == bi:
            x += 1
        else:
            x += (ai in sb) + (bi in sa)
        sa.add(ai)
        sb.add(bi)
        s += x / d * p**d
    return x / k * p**k + (1 - p) / p * s


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """P(pos > neg)."""
    from scipy.stats import rankdata

    r = rankdata(np.concatenate([pos, neg]))
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def evaluate(u: Universe, metric: str, x: np.ndarray, v: np.ndarray | None, sample_pp: int | None = None):
    """Returns (per-pair array [npairs, len(PERPAIR)], dict of set-level numbers)."""
    f = METRICS[metric]
    dq = f(x[NP:], x)  # [nr, NP+nr]
    if sample_pp:
        idx = np.linspace(0, NP - 1, sample_pp).astype(int)
        dpp = f(x[idx], x[:NP])
        dpp[np.arange(len(idx)), idx] = np.inf
    else:
        dpp = f(x[:NP], x[:NP])
        np.fill_diagonal(dpp, np.inf)
    two = np.partition(dpp, 1, axis=1)[:, :2]
    med_nn = float(np.median(two[:, 0]))
    ok = (two[:, 0] > 0) & np.isfinite(two[:, 1])
    lr = np.log(two[ok, 1] / two[ok, 0])
    twonn = float(ok.sum() / max(lr.sum(), 1e-12))
    fin = dpp[np.isfinite(dpp)]
    med_all = float(np.median(fin[:: max(1, fin.size // 200000)]))
    del dpp

    dpool = np.where(u.pool[None, :] & ~u.same, dq, np.inf)
    nn_other = dpool.min(1)
    dpil = np.where(~u.same[:, :NP], dq[:, :NP], np.inf)
    top = np.argsort(dpil, axis=1, kind="stable")[:, :10]
    dab = dq[u.pa, NP + u.pb]
    dba = dq[u.pb, NP + u.pa]
    d = 0.5 * (dab + dba)
    out = np.empty((len(u.pa), len(PERPAIR)), np.float32)
    out[:, 0] = 1 + (dpool[u.pa] < dab[:, None]).sum(1)
    out[:, 1] = 1 + (dpool[u.pb] < dba[:, None]).sum(1)
    out[:, 2] = dab / np.maximum(nn_other[u.pa], 1e-12)
    out[:, 3] = dba / np.maximum(nn_other[u.pb], 1e-12)
    out[:, 4] = d / max(med_nn, 1e-12)
    for i, (a, b) in enumerate(zip(u.pa, u.pb)):
        ta, tb = top[a], top[b]
        inter = len(set(ta.tolist()) & set(tb.tolist()))
        out[i, 5] = inter / (20 - inter)
        out[i, 6] = rbo_ext(ta.tolist(), tb.tolist())
        out[i, 7] = inter / 10
    out[:, 8] = d
    setlevel = {"med_nn": med_nn, "twonn": twonn, "rel_contrast": med_nn / max(med_all, 1e-12)}
    if v is not None:
        ids = np.unique(np.concatenate([u.va, u.vb]))
        dv = f(v[ids], v[ids])
        pos = {k: i for i, k in enumerate(ids)}
        dvp = np.array([dv[pos[a], pos[b]] for a, b in zip(u.va, u.vb)])
        clean = u.primary & (u.flag == "none")
        setlevel["ver_yes_step"] = float(np.median(dvp[u.vyes]) / max(med_nn, 1e-12))
        setlevel["auc_ver_vs_repro"] = auc(dvp[u.vyes], d[clean])
        hi = u.vyes & (u.vlab >= np.nanmedian(u.vlab[u.vyes]))
        setlevel["auc_colver_vs_repro"] = auc(dvp[hi], d[clean])
    return out, setlevel


def summarise(pp: np.ndarray, mask: np.ndarray) -> dict:
    p = pp[mask]
    rk = np.concatenate([p[:, 0], p[:, 1]])
    rn = np.concatenate([p[:, 2], p[:, 3]])
    return {
        "n": int(mask.sum()),
        "r1": float((rk <= 1).mean()),
        "r5": float((rk <= 5).mean()),
        "r10": float((rk <= 10).mean()),
        "rank_med": float(np.median(rk)),
        "rank_p90": float(np.percentile(rk, 90)),
        "rnn_med": float(np.median(rn)),
        "rnn_p75": float(np.percentile(rn, 75)),
        "rnn_p90": float(np.percentile(rn, 90)),
        "rstep_med": float(np.median(p[:, 4])),
        "rstep_p90": float(np.percentile(p[:, 4], 90)),
        "rstep_lt1": float((p[:, 4] < 1).mean()),
        "jacc": float(p[:, 5].mean()),
        "rbo": float(p[:, 6].mean()),
        "ov10": float(p[:, 7].mean()),
        "ov10_med": float(np.median(p[:, 7])),
    }
