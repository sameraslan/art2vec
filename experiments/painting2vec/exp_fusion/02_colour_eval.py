"""Part 1: invariance and discrimination of every colour descriptor, old and new.

For each descriptor x autocrop x treatment: R@1 and top-10 kept on the repro pairs (invariance
protocol, 28 excluded rows out of every pool), and discrimination on the kept pilot rows:
participation ratio, TwoNN dimension, "palette agreement" of the top 10 (reference distance to the
neighbours over reference distance to random paintings; the reference is the sliced-Wasserstein
distance between the unnormalised OKLab pixel distributions), and the AUC with which the distance
puts colour-different versions further apart than two photographs of one painting.

Writes results/colour_grid.csv, results/colour_greedy.json and OUT/colour_pp.npz (per-pair ranks).
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import blocks
import fz

ie = fz.InvEval()
u, keep = ie.u, ie.keep
HISTS = ("hist", "hue12", "hue6", "lc_copula", "copula")


def is_hist(name):
    return name.startswith(HISTS)


def pre(name, ac):
    """(pilot, repro, versions) arrays for a part: sqrt for histograms (Hellinger), else as stored.
    `old:<store>/<part>` reads the invariance experiment's stores (autocrop none only)."""
    if name.startswith("old:"):
        st, part = name[4:].split("/")
        return [fz.store(s, st, part) for s in fz.SETS]
    return [blocks.colour_part(s, name, ac) for s in fz.SETS]


def join(names, ac):
    """Equal-total-variance concatenation (scale fitted on the kept pilot rows); "name*w" weights a part."""
    out = [[], [], []]
    for nm in names:
        name, w = (nm.split("*") + ["1"])[:2] if not nm.startswith("old:") else (nm, "1")
        p = pre(name, ac)
        f = p[0][keep]
        s = float(np.sqrt(((f - f.mean(0)) ** 2).sum(1).mean())) or 1.0
        for i in range(3):
            out[i].append(p[i] * (float(w) / s))
    return [np.concatenate(o, 1) for o in out]


REF = {}
for nm in ("raw", "std"):
    r = np.sqrt(fz.sqdist(fz.store("pilot", f"colour__{nm}", "palette_sw")[keep]))
    REF[nm] = (r, float(r[~np.eye(len(r), dtype=bool)].mean()))


def treatments(xs):
    d = xs[0].shape[1]
    yield "euc", fz.Fit(xs[0][keep])
    yield "z", fz.Fit(xs[0][keep], pre="z")
    for k in sorted({min(k, d) for k in (8, 16, 32, 64)}):
        yield f"pca{k}w", fz.Fit(xs[0][keep], k=k, whiten=True)


def evaluate(xs, fit):
    xp, xr, xv = (fit(x) for x in xs)
    pp, sl, dpp = ie.run(xp, xr)
    row = {"dim": xp.shape[1], **sl}
    for nm, mask in (("clean", ie.clean), ("primary", ie.primary)):
        s = ie.summ(pp, mask)
        row.update({f"{k}_{nm}": v for k, v in s.items()})
    idx = np.argpartition(dpp, 10, axis=1)[:, :10]
    for nm, (r, base) in REF.items():
        row[f"pal_{nm}"] = float(np.take_along_axis(r, idx, 1).mean() / base)
    ids = np.unique(np.concatenate([u.va, u.vb]))
    pos = {k: i for i, k in enumerate(ids)}
    dv = np.sqrt(fz.sqdist(xv[ids]))
    dvp = np.array([dv[pos[a], pos[b]] for a, b in zip(u.va, u.vb)])
    hi = u.vyes & (u.vlab >= np.nanmedian(u.vlab[u.vyes]))
    row["auc_colver"] = fz.inv.auc(dvp[hi], pp["d"][ie.clean])
    return row, pp


def r1(xs, fit):
    xp, xr = fit(xs[0]), fit(xs[1])
    pp, _, _ = ie.run(xp, xr)
    return ie.summ(pp, ie.clean)["r1"]


if __name__ == "__main__":
    parts = fz.colour2_parts() + ["layout4ab_std", "layout4ab_sog_sca", "hue6_raw", "hue6_sog", "hue6_cen"]
    old = [f"old:colour__{n}/{p}" for n in ("raw", "std", "rank") for p in ("palette_hist", "palette_sw")]
    COMBOS = {
        "BASE hist+sw (std)": ["hist_raw_std", "sw_raw_std"],
        "hist+sw (sog,std)": ["hist_sog_std", "sw_sog_std"],
        "hist+sw (wp,std)": ["hist_wp_std", "sw_wp_std"],
        "hist+sw (sca)": ["hist_raw_sca", "sw_raw_sca"],
        "coarse hist (std+sca)": ["histc_raw_std", "histc_raw_sca"],
        "tone bands + hue families (cen)": ["tb8_std", "hue12_cen"],
        "tone bands + hue families (raw)": ["tb8_raw_sca", "hue12_raw"],
        "hue families + warm/cool (raw)": ["hue12_raw", "warm_raw"],
        "relational, tint kept": ["tb8_raw_sca", "hue12_raw", "hue6xL3_raw", "warm_raw", "lc_copula", "cq"],
        "relational, tint removed": ["tb8_std", "hue12_cen", "hue6xL3_cen", "warm_cen", "lc_copula", "cq", "copula4"],
        "rank only": ["copula4", "lc_copula", "hist_rank"],
        "palette k=5 ordered + spacing": ["pal5_std", "pal5_spacing"],
        "layout 4x4 ab + tone bands": ["layout4ab_std", "tb8_std"],
        "layout 4x4 + hist+sw (std)": ["layout4_std", "hist_raw_std", "sw_raw_std"],
    }
    rows, PP, names = [], [], []

    def add(label, kind, xs, ac):
        for tname, fit in treatments(xs):
            row, pp = evaluate(xs, fit)
            rows.append({"feature": label, "kind": kind, "ac": ac, "treat": tname, **row})
            PP.append(np.stack([pp["rank_ab"], pp["rank_ba"], pp["ov10"]], 1).astype(np.float32))
            names.append(f"{label}|{ac}|{tname}")

    for ac in ("none", "frame"):
        for p in parts:
            add(p, "single", pre(p, ac), ac)
        for label, ns in COMBOS.items():
            add(label, "combo", join(ns, ac), ac)
        print("grid", ac, len(rows), flush=True)
    for p in old:
        add(p, "old", pre(p, "none"), "none")
    add("old: std hist+sw", "old", join(["old:colour__std/palette_hist", "old:colour__std/palette_sw"], "none"), "none")

    # greedy forward selection on R@1 (clean pairs), whitened PCA-64; chosen on the pairs it reports
    greedy = {}
    pools = {
        "all parts": parts,
        "no spatial parts": [p for p in parts if not p.startswith("layout")],
        "no spatial, no full histogram": [p for p in parts if not p.startswith(("layout", "hist_", "sw_"))],
    }
    for ac in ("frame",):
        for pname, pool in pools.items():
            chosen, trace = [], []
            for _ in range(5):
                best = None
                for p in pool:
                    if p in chosen:
                        continue
                    xs = join(chosen + [p], ac)
                    k = min(64, xs[0].shape[1])
                    s = r1(xs, fz.Fit(xs[0][keep], k=k, whiten=True))
                    if best is None or s > best[0]:
                        best = (s, p)
                if trace and best[0] <= trace[-1][1] + 0.002:
                    break
                chosen.append(best[1])
                trace.append((best[1], best[0]))
                print("greedy", pname, trace[-1], flush=True)
            greedy[pname] = trace
            add(f"GREEDY {pname}", "greedy", join(chosen, ac), ac)
            add(f"GREEDY {pname}", "greedy", join(chosen, "none"), "none")
    fz.dump(greedy, "colour_greedy.json")
    df = pd.DataFrame(rows)
    df.to_csv(fz.RES / "colour_grid.csv", index=False, float_format="%.4f")
    np.savez(fz.OUT / "colour_pp.npz", pp=np.stack(PP), names=np.array(names))
    cols = ["feature", "ac", "treat", "dim", "r1_clean", "ov10_clean", "r1_primary", "twonn", "pr", "pal_raw", "pal_std", "auc_colver"]
    best = df.sort_values("r1_clean", ascending=False).groupby(["feature", "ac"], sort=False).head(1)
    pd.set_option("display.width", 250, "display.max_rows", 500)
    print(best[cols].to_string(index=False))
