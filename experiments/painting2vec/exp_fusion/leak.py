"""Checks on a neighbour space. Labels are read here, to score, and nowhere else."""

from __future__ import annotations

import numpy as np
from scipy.stats import skew

import fz
import evals  # exp_separation/evals.py (on sys.path through fz)

ev = evals.Evaluator()
M = ev.m  # kept pilot rows, in order
N = ev.n
YEAR = ev.year
HAS_YEAR = ev.has_year
TRAD = M.tradition.to_numpy(dtype=object)


def with_inf(D):
    D = D.copy()
    np.fill_diagonal(D, np.inf)
    return D


def lists(D):
    """D [n, n] distances (any monotone form) with inf on the diagonal."""
    o = {}
    s = ev._subject(D)
    o["genre_p10"], o["broad_p10"], o["depicts_j10"] = s["genre_p10"], s["broad_p10"], s["depicts_j10"]
    n = ev._neigh(D)
    o["painter10"], o["year_gap"], o["year_gap_rand"] = n["painter_repeat10"], n["year_spread10"], n["year_spread_rand"]
    o["hub_skew"], o["hub_zero"], o["hub_max"] = n["hub_skew"], n["hub_zero"], n["hub_max"]
    hy = HAS_YEAR
    idx = ev.topk(D, hy)
    y = YEAR[hy]
    dy = np.abs(y[idx] - y[:, None])
    o["within50"] = float((dy <= 50).mean())
    o["within50_rand"] = float((np.abs(y[:, None] - y[None]) <= 50).mean())
    o["beyond150"] = float((dy >= 150).mean())
    idx = ev.topk(D)
    o["same_tradition10"] = float((TRAD[idx] == TRAD[:, None]).mean())
    return o


def hubs(idx, n=8):
    cnt = np.bincount(idx.ravel(), minlength=N)
    o = np.argsort(-cnt)[:n]
    return [
        {"qid": M.qid[i], "title": str(M.title[i])[:50], "painter": str(M.creator_name[i])[:30],
         "year": None if not np.isfinite(YEAR[i]) else int(YEAR[i]), "tradition": TRAD[i], "in_lists": int(cnt[i])}
        for i in o
    ], {"hub_skew": float(skew(cnt)), "hub_zero": float((cnt == 0).mean()), "hub_max": int(cnt.max())}


def versions(Zk, Zv):
    """Rank of the version partner among the kept pilot paintings (the pair itself removed) plus the
    partner; Euclidean. Mean of the two directions, as in the separation experiment."""
    pr = ev.pairs
    Dvp = np.sqrt(fz.sqdist(Zv, Zk))
    Dvv = np.sqrt(fz.sqdist(Zv))
    r = []
    for qa, qb in zip(pr.qid_a, pr.qid_b):
        a, b = ev.v_pos[qa], ev.v_pos[qb]
        rr = []
        for x, y in ((a, b), (b, a)):
            d = Dvp[x].copy()
            for q in (qa, qb):
                if q in ev.p_pos:
                    d[ev.p_pos[q]] = np.inf
            rr.append(1 + int((d < Dvv[x, y]).sum()))
        r.append(np.mean(rr))
    r = np.array(r)
    yes = (pr.composition_match == "yes").values
    series = (pr.relation == "series_motif").values
    var = (pr.composition_match == "variant").values & ~series
    return {
        "ver_top1": float((r[yes] <= 1).mean()), "ver_top10": float((r[yes] <= 10).mean()),
        "ver_variant_med": float(np.median(r[var])), "ver_series_med": float(np.median(r[series])),
    }


def probes(Zk, k=64):
    """Linear probes on the first k principal components of the space (kept rows)."""
    f = fz.Fit(Zk, k=min(k, Zk.shape[1]))
    p = ev._probes(f(Zk))
    return {
        "year_r2_eu": p["probe_year_r2_eu"], "fame_r2": p["probe_fame_r2"], "fame_rho": p["probe_fame_rho"],
        "fame_within_rho": p["probe_fame_within_rho"], "museum_acc": p["probe_museum_acc"],
        "museum_base": p["probe_museum_base"], "museum_base_plus": p["probe_museum_base_plus"],
        "museum_majority": p["probe_museum_majority"], "painter_acc": p["probe_painter_acc"],
    }
