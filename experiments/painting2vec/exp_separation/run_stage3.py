"""Stage 3: ablations (view, model size, PCA dimension, whitening), the redundancy table, the
permutation null for the describer correlations, and the label-assisted removal variants.

Only the block under `label_assisted` uses labels to build a vector. Those variants are evaluated on
the half of the painters that the removal was not fitted on, next to the untouched vector on the
same half.
"""
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from cands import Cands
from evals import Evaluator, _folds, cv_ridge
from lib import OUT, cosdist
from run_sweep import C, ev, res, res_path, run

B = C.base
keep = ev.keep_fit


def stats(store):
    return C.composite([(store, p) for p in ("gramlog_early", "gramlog_mid", "std_early", "std_mid")])


def ablations():
    # view and size
    for model, views in (("dinov2_b", ("center", "pad", "tile")), ("dinov2_l", ("pad", "tile"))):
        for v in views:
            st = f"{model}__{v}"
            for p in ("cls", "patch_mean", "meanstd_mid"):
                run(f"{st}/{p}", B(st, p))
            run(f"abl/{st}/stats", stats(st))
    for v in ("center", "pad", "tile"):
        run(f"siglip2_b__{v}/embed", B(f"siglip2_b__{v}", "embed"))
    for v in ("pad", "tile"):
        for p in ("style", "content"):
            run(f"csd_l__{v}/{p}", B(f"csd_l__{v}", p))
        run(f"clip_l__{v}/embed", B(f"clip_l__{v}", "embed"))
        for m in ("dinov2_b", "dinov2_l"):
            run(f"abl/csd_style[{v}] _|_ {m}_cls[{v}]", C.resid(B(f"csd_l__{v}", "style"), [B(f"{m}__{v}", "cls")]))
            run(f"abl/{m}_msmid[{v}] _|_ {m}_cls[{v}]", C.resid(B(f"{m}__{v}", "meanstd_mid"), [B(f"{m}__{v}", "cls")]))
            run(f"abl/{m}_cls[{v}] _|_ csd_style[{v}]", C.resid(B(f"{m}__{v}", "cls"), [B(f"csd_l__{v}", "style")]))
    # PCA dimension and whitening
    for st, p in (("dinov2_l__pad", "cls"), ("siglip2_b__pad", "embed"), ("csd_l__pad", "style"),
                  ("dinov2_l__pad", "meanstd_mid"), ("dinov2_l__pad", "gramlog_mid")):
        for k in (16, 32, 64, 128):
            for w in (False, True):
                if k == 64 and not w:
                    continue
                run(f"abl/{st}/{p} k={k}{' white' if w else ''}", B(st, p, k=k, whiten=w), k_probe=k)
    # pre-treatment of the statistics parts: z-score (default) against plain L2
    for p in ("gram_mid", "gramlog_mid", "meanstd_mid"):
        for pre in ("l2", "zl2", "none"):
            run(f"abl/dinov2_l__pad/{p} pre={pre}", B("dinov2_l__pad", p, pre=pre))
    # residual with a wider nuisance (128) and with whitening after
    for k in (32, 128):
        run(f"abl/csd_style _|_ dl_cls nuis k={k}", C.resid(B("csd_l__pad", "style"), [B("dinov2_l__pad", "cls", k=k)]))
        run(f"abl/dl_cls _|_ csd_style nuis k={k}", C.resid(B("dinov2_l__pad", "cls"), [B("csd_l__pad", "style", k=k)]))


LEAD = {
    "subject: DINOv2-L cls": lambda: B("dinov2_l__pad", "cls"),
    "subject: SigLIP2 embed": lambda: B("siglip2_b__pad", "embed"),
    "subject res: DINOv2-L cls _|_ CSD style": lambda: C.resid(B("dinov2_l__pad", "cls"), [B("csd_l__pad", "style")]),
    "manner: DINOv2-L stats": lambda: stats("dinov2_l__pad"),
    "manner: DINOv2-L meanstd_mid": lambda: B("dinov2_l__pad", "meanstd_mid"),
    "manner: CSD style": lambda: B("csd_l__pad", "style"),
    "manner res: CSD style _|_ DINOv2-L cls": lambda: C.resid(B("csd_l__pad", "style"), [B("dinov2_l__pad", "cls")]),
    "manner res: meanstd_mid _|_ DINOv2-L cls": lambda: C.resid(B("dinov2_l__pad", "meanstd_mid"), [B("dinov2_l__pad", "cls")]),
    "colour (lstd)": lambda: C.colour("lstd"),
    "composition": lambda: C.composition(),
}


def cka(X, Y):
    X = X - X.mean(0)
    Y = Y - Y.mean(0)
    return float(np.linalg.norm(X.T @ Y) ** 2 / (np.linalg.norm(X.T @ X) * np.linalg.norm(Y.T @ Y)))


def redundancy():
    Z = {k: f()[0][ev.keep].astype(np.float64) for k, f in LEAD.items()}
    names = list(Z)
    top = {}
    for k in names:
        D = cosdist(Z[k].astype(np.float32))
        np.fill_diagonal(D, np.inf)
        top[k] = np.argpartition(D, 10, axis=1)[:, :10]
        del D
    rf = np.random.default_rng(0).integers(0, 5, ev.n)
    out = {"names": names, "jaccard_mean": {}, "jaccard_zero": {}, "shared_mean": {}, "cka": {}, "r2": {}}
    for a in names:
        for b in names:
            if a == b:
                continue
            inter = np.array([len(set(x) & set(y)) for x, y in zip(top[a], top[b])])
            out["jaccard_mean"][f"{a}|{b}"] = float((inter / (20 - inter)).mean())
            out["shared_mean"][f"{a}|{b}"] = float(inter.mean())
            out["jaccard_zero"][f"{a}|{b}"] = float((inter == 0).mean())
            out["cka"][f"{a}|{b}"] = cka(Z[a], Z[b])
            # variance-weighted cross-validated R2 of b predicted from a
            Y = Z[b] - Z[b].mean(0)
            P = cv_ridge(Z[a], Y, rf, alpha=10.0)
            out["r2"][f"{a}|{b}"] = float(1 - ((Y - P) ** 2).sum() / (Y**2).sum())
    json.dump(out, open(OUT / "redundancy.json", "w"), indent=1)
    for key in ("shared_mean", "cka", "r2"):
        print(key)
        for a in names:
            print(f"{a[:38]:38s}", " ".join(f"{out[key].get(f'{a}|{b}', float('nan')):6.2f}" for b in names))


def mantel_null(n_perm=500):
    """Null spread of the describer rank correlations when the 60 paintings are shuffled."""
    Zp = B("dinov2_l__pad", "cls")[0][ev.keep]
    D = cosdist(Zp[ev.d_idx])
    iu = ev.d_iu
    n = ev.d_n
    rng = np.random.default_rng(0)
    out = {}
    for name, v in (("subj", ev.d_subj), ("man3", ev.d_man3)):
        L = np.zeros((n, n)); L[iu] = v; L = L + L.T
        r = rankdata(D[iu])
        null = []
        for _ in range(n_perm):
            p = rng.permutation(n)
            null.append(np.corrcoef(r, rankdata(L[p][:, p][iu]))[0, 1])
        out[name] = {"null_sd": float(np.std(null)), "null_p95": float(np.percentile(np.abs(null), 95))}
    # local nn3 ratio null: random neighbours
    json.dump(out, open(OUT / "mantel_null.json", "w"), indent=1)
    print(out)


# ---------------------------------------------------------------------------- label-assisted


def leace(X, Zl):
    """Least-squares concept erasure, fitted on X [n, d] and labels Zl [n, c]: returns (mean, P)
    so that (x - mean) @ P has zero covariance with Zl on the fitting rows."""
    mu = X.mean(0)
    Xc = X - mu
    Zc = Zl - Zl.mean(0)
    S = Xc.T @ Xc / len(X)
    w, V = np.linalg.eigh(S)
    w = np.maximum(w, 1e-10)
    Wh = (V / np.sqrt(w)) @ V.T
    Wi = (V * np.sqrt(w)) @ V.T
    A = Wh @ (Xc.T @ Zc / len(X))
    U, s, _ = np.linalg.svd(A, full_matrices=False)
    U = U[:, s > 1e-8 * s.max()]
    P = np.eye(X.shape[1]) - Wh @ U @ U.T @ Wi
    return mu, P, U.shape[1]


def label_assisted():
    m = ev.meta_all
    groups = np.where(m.painter.to_numpy(dtype=object) != "", m.painter.to_numpy(dtype=object), m.qid.to_numpy(dtype=object))
    half = _folds(groups, n_splits=2, seed=1)
    fit = keep & (half == 0)
    evB = Evaluator(subset=(half == 1))
    out = {}
    year = m.inception_year.values.astype(float)
    painter = m.painter.to_numpy(dtype=object)
    cnt = pd.Series(painter[fit & (painter != "")]).value_counts()
    big = cnt[cnt >= 5].index.values
    cands = {
        "DINOv2-L cls": B("dinov2_l__pad", "cls"),
        "SigLIP2 embed": B("siglip2_b__pad", "embed"),
        "CLIP-L embed": B("clip_l__pad", "embed"),
        "CSD style": B("csd_l__pad", "style"),
        "CSD style _|_ DINOv2-L cls": C.resid(B("csd_l__pad", "style"), [B("dinov2_l__pad", "cls")]),
    }
    for name, (P_, V_) in cands.items():
        X = P_.astype(np.float64)
        Xv = V_.astype(np.float64)
        out[f"{name} | untouched"] = evB.evaluate(P_[evB.keep], V_)
        # year: year and year squared
        f = fit & np.isfinite(year)
        yz = (year[f] - 1600) / 200
        mu, Pm, r = leace(X[f], np.column_stack([yz, yz**2]))
        out[f"{name} | minus year (label-assisted, rank {r})"] = evB.evaluate(((X - mu) @ Pm)[evB.keep].astype(np.float32), ((Xv - mu) @ Pm).astype(np.float32))
        # painter: one-hot of the fitting half's painters with 5+ works
        f = fit & np.isin(painter, big)
        oh = pd.get_dummies(painter[f]).values.astype(float)
        mu, Pm, r = leace(X[f], oh)
        out[f"{name} | minus painter (label-assisted, rank {r})"] = evB.evaluate(((X - mu) @ Pm)[evB.keep].astype(np.float32), ((Xv - mu) @ Pm).astype(np.float32))
        # both
        f = fit & np.isin(painter, big) & np.isfinite(year)
        oh = pd.get_dummies(painter[f]).values.astype(float)
        yz = (year[f] - 1600) / 200
        mu, Pm, r = leace(X[f], np.column_stack([oh, yz, yz**2]))
        out[f"{name} | minus painter and year (label-assisted, rank {r})"] = evB.evaluate(((X - mu) @ Pm)[evB.keep].astype(np.float32), ((Xv - mu) @ Pm).astype(np.float32))
        print(name, "done", flush=True)
    out["_setup"] = {"n_eval": int(evB.n), "n_fit": int(fit.sum()), "painters_fit_5plus": int(len(big)),
                     "p8_in_eval": int(evB.p8.sum()), "describer_in_eval": int(evB.d_n)}
    json.dump(out, open(OUT / "label_assisted.json", "w"), indent=1)


def csd_heads():
    """How different are CSD's two heads from each other and from plain CLIP?"""
    Z = {"CSD style": B("csd_l__pad", "style"), "CSD content": B("csd_l__pad", "content"),
         "CSD backbone": B("csd_l__pad", "backbone"), "CLIP-L embed": B("clip_l__pad", "embed"),
         "CLIP-L backbone": B("clip_l__pad", "backbone")}
    Z = {k: v[0][ev.keep].astype(np.float64) for k, v in Z.items()}
    top = {}
    for k in Z:
        D = cosdist(Z[k].astype(np.float32))
        np.fill_diagonal(D, np.inf)
        top[k] = np.argpartition(D, 10, axis=1)[:, :10]
    rf = np.random.default_rng(0).integers(0, 5, ev.n)
    out = []
    names = list(Z)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            inter = np.array([len(set(x) & set(y)) for x, y in zip(top[a], top[b])])
            Y = Z[b] - Z[b].mean(0)
            P = cv_ridge(Z[a], Y, rf, alpha=10.0)
            out.append({"a": a, "b": b, "shared_top10": float(inter.mean()), "cka": cka(Z[a], Z[b]),
                        "r2_b_from_a": float(1 - ((Y - P) ** 2).sum() / (Y**2).sum())})
            print(out[-1])
    json.dump(out, open(OUT / "csd_heads.json", "w"), indent=1)


if __name__ == "__main__":
    what = sys.argv[1]
    {"abl": ablations, "red": redundancy, "null": mantel_null, "lab": label_assisted, "csd": csd_heads}[what]()
