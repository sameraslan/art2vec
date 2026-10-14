"""Parts 3 and 4: the lens set, its checks, and what the period filter costs.

Writes results/lenses.json, results/period.json, OUT/lens_<id>.npz (ordered top-100 lists and
distances over the kept pilot rows, plus the fused vectors) and the period contact sheets.
"""

from __future__ import annotations

import sys

import numpy as np
from scipy.stats import norm

import blocks
import fz
import leak

ev = leak.ev
keep = ev.keep_fit
KTOP = 100
SEEDS = ["Q12418", "Q45585", "Q2016193", "Q220859", "Q151047", "Q500985", "Q969377", "Q185372",
         "Q1091086", "Q693746", "Q2339059", "Q683274", "Q1044742", "Q698487", "Q587514", "Q18683017"]


def ordered_top(D, k):
    idx = np.argpartition(D, k, axis=1)[:, :k]
    o = np.argsort(np.take_along_axis(D, idx, 1), axis=1, kind="stable")
    return np.take_along_axis(idx, o, 1)


def corrections(D, k=10):
    """Three standard hubness corrections of a distance matrix (inf on the diagonal)."""
    part = np.partition(D, k - 1, axis=1)[:, :k]
    sig = part[:, k - 1]
    ls = D * D / (sig[:, None] * sig[None])  # local scaling (Zelnik-Manor and Perona), ranks as 1-exp(-.)
    np.fill_diagonal(ls, np.inf)
    rk = part.mean(1)
    csls = 2 * D - rk[:, None] - rk[None]  # CSLS (Conneau et al.)
    np.fill_diagonal(csls, np.inf)
    Df = np.where(np.isfinite(D), D, np.nan)
    mu, sd = np.nanmean(Df, 1), np.nanstd(Df, 1)
    mp = 1 - norm.sf((D - mu[:, None]) / sd[:, None]) * norm.sf((D - mu[None]) / sd[None])  # mutual proximity, Gaussian
    np.fill_diagonal(mp, np.inf)
    return {"local scaling": ls.astype(np.float32), "CSLS": csls.astype(np.float32), "mutual proximity": mp.astype(np.float32)}


def far_lists(D, min_gap, k=10):
    """Top-k among paintings at least min_gap years away. Returns (rows with a year, idx into those rows, Dm)."""
    hy = leak.HAS_YEAR
    y = leak.YEAR[hy]
    Dm = D[hy][:, hy].copy()
    gap = np.abs(y[:, None] - y[None])
    Dm[gap < min_gap] = np.inf
    ok = np.isfinite(Dm).sum(1) >= k
    return hy, ordered_top(Dm, k), ok, Dm


def list_quality(idx, rows):
    """Same broad genre and same Wikidata genre share for lists indexed within `rows` (bool over kept)."""
    sb = ev.same_broad[rows][:, rows]
    hb = ev.has_broad[rows]
    sg = ev.same_genre[rows][:, rows]
    hg = ev.has_genre[rows]
    b = np.take_along_axis(sb, idx, 1)[hb]
    g = np.take_along_axis(sg, idx, 1)[hg]
    return float(b.mean()), float(g.mean())


if __name__ == "__main__":
    B = blocks.build()
    sc = {b: blocks.scales(B[b][0][keep])[blocks.RULE] for b in B}
    res, tops, Ds, alltops = {}, {}, {}, {}
    ie = fz.InvEval()
    qid = leak.M.qid.to_numpy()
    for lid, L in {**blocks.LENSES, **blocks.VARIANTS}.items():
        w = L["weights"]
        Zp = blocks.fuse(B, w, sc, 0)
        Zk, Zr, Zv = Zp[keep], blocks.fuse(B, w, sc, 1), blocks.fuse(B, w, sc, 2)
        D = np.sqrt(fz.sqdist(Zk))
        np.fill_diagonal(D, np.inf)
        idx = ordered_top(D, KTOP)
        alltops[lid] = idx[:, :10]
        if lid in blocks.LENSES:
            tops[lid], Ds[lid] = idx, D
            np.savez(fz.OUT / f"lens_{lid}.npz", idx=idx.astype(np.int32),
                     dist=np.take_along_axis(D, idx, 1).astype(np.float32), Z=Zk.astype(np.float32))
        r = {"name": L["name"], "weights": w, **leak.lists(D), **leak.versions(Zk, Zv)}
        pp, _, _ = ie.run(Zp, Zr)
        s, sp = ie.summ(pp, ie.clean), ie.summ(pp, ie.primary)
        r.update({"repro_r1": s["r1"], "repro_kept10": s["ov10"], "repro_under_step": s["under_step"],
                  "repro_r1_all_primary": sp["r1"], "repro_kept10_all_primary": sp["ov10"]})
        r["hubs"], _ = leak.hubs(idx[:, :10])
        r["probes"] = leak.probes(Zk) if lid in blocks.LENSES else {}
        # genre make-up: for seeds of each broad genre, what share of their neighbours share it
        mk = {}
        for g, j in ev.broad_vocab.items():
            hasg = np.array([g in s_ for s_ in leak.M.broad_set])
            nb = np.array([[g in leak.M.broad_set[t] for t in row] for row in idx[hasg, :10]])
            mk[g] = {"n": int(hasg.sum()), "base": float(hasg.mean()), "neighbours": float(nb.mean())}
        r["genre_makeup"] = mk
        res[lid] = r
        print(lid, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k not in ("hubs", "probes", "genre_makeup", "weights")}, flush=True)
        print("   probes", {k: round(v, 3) for k, v in r["probes"].items()}, flush=True)
    res["_overlap"] = {a: {b: fz.overlap(alltops[a], alltops[b]) for b in alltops} for a in alltops}
    print("overlap", res["_overlap"])

    # hubness corrections, on every lens
    hub = {}
    for lid in tops:
        D = Ds[lid]
        hub[lid] = {"none": {**leak.lists(D), "overlap_with_plain": 1.0}}
        for cname, Dc in corrections(D).items():
            hub[lid][cname] = {**leak.lists(Dc), "overlap_with_plain": fz.overlap(ordered_top(Dc, 10), tops[lid][:, :10])}
        print("hub", lid, {c: (round(v["hub_skew"], 2), round(v["hub_zero"], 3), v["hub_max"], round(v["broad_p10"], 3), round(v["overlap_with_plain"], 2)) for c, v in hub[lid].items()}, flush=True)
    res["_hubness"] = hub
    fz.dump(res, "lenses.json")

    # ------------------------------------------------------------ Part 4: period
    per = {}
    hy = leak.HAS_YEAR
    y = leak.YEAR[hy]
    qy = qid[hy]
    rng = np.random.default_rng(0)
    for lid in tops:
        D = Ds[lid]
        Dy = D[hy][:, hy]
        plain = ordered_top(Dy, 10)
        d10 = np.take_along_axis(Dy, plain, 1)[:, 9]
        order = np.argsort(Dy, axis=1)
        gap = np.abs(y[:, None] - y[None])
        r = {"plain": dict(zip(("broad_p10", "genre_p10"), list_quality(plain, hy)))}
        dyp = np.abs(y[plain] - y[:, None])
        r["plain"].update({"within25": float((dyp <= 25).mean()), "within50": float((dyp <= 50).mean()),
                           "within100": float((dyp <= 100).mean()), "beyond150": float((dyp >= 150).mean()),
                           "lists_entirely_within50": float((dyp <= 50).all(1).mean()),
                           "lists_with_a_150y_neighbour": float((dyp >= 150).any(1).mean()),
                           "median_gap": float(np.median(np.median(dyp, 1)))})
        for g in (50, 150, 300):
            _, idx, ok, Dm = far_lists(D, g)
            b, ge = list_quality(idx[ok], hy) if ok.all() else (np.nan, np.nan)
            if not ok.all():
                sub = np.where(ok)[0]
                sb = ev.same_broad[hy][:, hy]
                hb = ev.has_broad[hy]
                b = float(np.take_along_axis(sb, idx, 1)[ok & hb].mean())
                ge = float(np.take_along_axis(ev.same_genre[hy][:, hy], idx, 1)[ok & ev.has_genre[hy]].mean())
            dfar = np.take_along_axis(Dm, idx, 1)
            far_ok = gap >= g
            # rank in the full ordering of the 1st and the 10th far neighbour
            csum = np.cumsum(np.take_along_axis(far_ok, order, 1), 1)
            r1 = (csum < 1).sum(1) + 1
            r10 = (csum < 10).sum(1) + 1
            # chance: random far candidates
            sbm = ev.same_broad[hy][:, hy]
            chance = float(((sbm & far_ok).sum(1) / np.maximum(far_ok.sum(1), 1))[ev.has_broad[hy]].mean())
            r[f"far{g}"] = {
                "paintings_with_10": float(ok.mean()), "broad_p10": b, "genre_p10": ge, "broad_chance": chance,
                "dist_ratio_1st": float(np.median(dfar[ok, 0] / np.take_along_axis(Dy, plain, 1)[ok, 0])),
                "dist_ratio_10th": float(np.median(dfar[ok, 9] / d10[ok])),
                "rank_of_1st_median": float(np.median(r1[ok])), "rank_of_10th_median": float(np.median(r10[ok])),
                "ten_within_top100": float((r10[ok] <= 100).mean()), "ten_within_top300": float((r10[ok] <= 300).mean()),
                "same_tradition": float((leak.TRAD[hy][idx[ok]] == leak.TRAD[hy][ok][:, None]).mean()),
            }
        per[lid] = r
        print("period", lid, {k: {a: round(b, 3) for a, b in v.items()} for k, v in r.items()}, flush=True)
    fz.dump(per, "period.json")

    # contact sheets: plain against 150 years away, three lenses
    ycap = {q: ("?" if not np.isfinite(v) else int(v)) for q, v in zip(qid, leak.YEAR)}
    pos = {q: i for i, q in enumerate(qy)}
    far = {lid: far_lists(Ds[lid], 150, 8)[1] for lid in tops}
    pl = {lid: ordered_top(Ds[lid][hy][:, hy], 8) for lid in tops}
    seeds = [s for s in SEEDS if s in pos]
    extra = [q for q in qy[rng.permutation(len(qy))[:14]] if q not in seeds]
    names = {}
    for si, s in enumerate(seeds + extra):
        i = pos[s]
        rows = []
        for lid in tops:
            rows.append((f"{lid}", s, [qy[j] for j in pl[lid][i]]))
            rows.append((f"{lid} >=150y", s, [qy[j] for j in far[lid][i]]))
        f = fz.OUT / f"period_{si+1:02d}_{s}.jpg"
        blocks.sheet(f, rows, T=130, caption=lambda q: ycap[q])
        names[s] = {r[0]: r[2] for r in rows}
    fz.dump(names, "period_sheets.json")
    print("sheets", len(names))
