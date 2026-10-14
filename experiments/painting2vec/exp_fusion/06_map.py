"""Part 5: one 2D layout per lens, aligned across lenses.

openTSNE, exact neighbours, Euclidean on the fused vectors, perplexity 30, seed 0. The default lens
starts from PCA. Every other lens is laid out twice: `fresh` (its own PCA start) and `aligned`
(started from the default lens's finished layout and optimised without early exaggeration).
Reports how much of the true top-10 list survives in 2D. Writes OUT/map_<id>.npy, results/map.json.
"""

from __future__ import annotations

import numpy as np
from openTSNE import TSNEEmbedding, affinity, initialization
from sklearn.manifold import trustworthiness

import blocks
import fz

SEED = 0


def aff(Z, perplexity=30):
    return affinity.PerplexityBasedNN(Z, perplexity=perplexity, metric="euclidean", method="exact", n_jobs=1, random_state=SEED)


def layout(A, init, early=True):
    e = TSNEEmbedding(np.array(init, dtype=np.float64), A, negative_gradient_method="bh", n_jobs=1, random_state=SEED)
    if early:
        e = e.optimize(n_iter=250, exaggeration=12, momentum=0.5)
    return np.asarray(e.optimize(n_iter=500, momentum=0.8))


def top2d(Y, k):
    D = fz.sqdist(Y.astype(np.float32))
    np.fill_diagonal(D, np.inf)
    return np.argpartition(D, k, axis=1)[:, :k]


def preserve(idx10, Y):
    out = {}
    for k in (10, 30, 100):
        t = top2d(Y, k)
        out[f"top10_in_2d_top{k}"] = float(np.mean([len(set(a) & set(b)) for a, b in zip(idx10.tolist(), t.tolist())]) / 10)
    return out


def procrustes_fit(Y, ref):
    """Rotate, reflect and scale Y onto ref (both centred)."""
    a, b = Y - Y.mean(0), ref - ref.mean(0)
    u, s, vt = np.linalg.svd(a.T @ b)
    R = u @ vt
    return (a @ R) * (s.sum() / (a**2).sum()) + ref.mean(0)


def displacement(Y, ref):
    span = np.linalg.norm(np.percentile(ref, 97.5, axis=0) - np.percentile(ref, 2.5, axis=0))
    return float(np.median(np.linalg.norm(Y - ref, axis=1)) / span)


if __name__ == "__main__":
    out = {}
    lids = list(blocks.LENSES)
    data = {l: np.load(fz.OUT / f"lens_{l}.npz") for l in lids}
    Z0 = data[lids[0]]["Z"]
    base_raw = layout(aff(Z0), initialization.pca(Z0, random_state=SEED))
    base = base_raw / np.abs(base_raw).max()
    np.save(fz.OUT / f"map_{lids[0]}.npy", base.astype(np.float32))
    out[lids[0]] = {"aligned": {**preserve(data[lids[0]]["idx"][:, :10], base),
                                "trustworthiness10": float(trustworthiness(Z0, base, n_neighbors=10))}}
    for p in (10, 50):
        Y = layout(aff(Z0, p), initialization.pca(Z0, random_state=SEED))
        out[lids[0]][f"perplexity{p}"] = preserve(data[lids[0]]["idx"][:, :10], Y)
    print(lids[0], out[lids[0]], flush=True)
    for l in lids[1:]:
        Z, idx = data[l]["Z"], data[l]["idx"][:, :10]
        A = aff(Z)
        fresh = layout(A, initialization.pca(Z, random_state=SEED))
        al = layout(A, base_raw, early=False)  # a finished-size start; no early exaggeration
        al = al / np.abs(al).max()
        np.save(fz.OUT / f"map_{l}.npy", al.astype(np.float32))
        out[l] = {
            "aligned": {**preserve(idx, al), "trustworthiness10": float(trustworthiness(Z, al, n_neighbors=10)),
                        "median_move_vs_default": displacement(procrustes_fit(al, base), base),
                        "default_2d_top10_kept": fz.overlap(top2d(base, 10), top2d(al, 10))},
            "fresh": {**preserve(idx, fresh), "trustworthiness10": float(trustworthiness(Z, fresh, n_neighbors=10)),
                      "median_move_vs_default": displacement(procrustes_fit(fresh, base), base),
                      "default_2d_top10_kept": fz.overlap(top2d(base, 10), top2d(fresh, 10))},
        }
        print(l, out[l], flush=True)
    fz.dump(out, "map.json")
