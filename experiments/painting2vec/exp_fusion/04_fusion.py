"""Part 2: how to make blocks comparable, and how much of a top-10 list each block controls.

Fused squared distance = sum over blocks of (w_b / s_b)^2 * d_b^2, where s_b is the block's scale
under one of five rules (blocks.scales). Control of block b at weights w = the share of the top-10
list that changes when w_b is set to 0.

Writes results/fusion.json.
"""

from __future__ import annotations

import itertools

import numpy as np

import blocks
import fz
import leak

keep = leak.ev.keep_fit
B = blocks.build()
NAMES = list(B)
D2 = {b: fz.sqdist(B[b][0][keep]) for b in NAMES}
SC = {b: blocks.scales(B[b][0][keep]) for b in NAMES}
RULES = list(next(iter(SC.values())))
ie = fz.InvEval()


def fused(rule, w):
    d = None
    for b, wb in w.items():
        if wb > 0:
            t = D2[b] * np.float32((wb / SC[b][rule]) ** 2)
            d = t if d is None else d + t
    np.fill_diagonal(d, np.inf)
    return d


def top(rule, w):
    d = fused(rule, w)
    idx = np.argpartition(d, 10, axis=1)[:, :10]
    return idx, d


def control(rule, w):
    full, _ = top(rule, w)
    out = {}
    for b in w:
        if w[b] > 0 and sum(v > 0 for v in w.values()) > 1:
            out[b] = 1 - fz.overlap(full, top(rule, {**w, b: 0})[0])
    return out


def solo(rule, w):
    full, _ = top(rule, w)
    return {b: fz.overlap(full, top(rule, {b: 1})[0]) for b in w if w[b] > 0}


def stability(rule, w):
    sc = {b: SC[b][rule] for b in NAMES}
    pp, _, _ = ie.run(blocks.fuse(B, w, sc, 0), blocks.fuse(B, w, sc, 1))
    s = ie.summ(pp, ie.clean)
    return {"r1": s["r1"], "kept10": s["ov10"]}


if __name__ == "__main__":
    out = {"blocks": {}, "rules": {}}
    for b in NAMES:
        x = B[b][0][keep]
        d = np.sqrt(D2[b][np.triu_indices(len(x), 1)])
        out["blocks"][b] = {
            "dim": x.shape[1], "participation_ratio": fz.participation_ratio(x), **SC[b],
            "median_pair": float(np.median(d)), "contrast_nn10": SC[b]["nn10"] / float(np.median(d)),
            "solo": {**leak.lists(fused("variance", {b: 1})), **stability("variance", {b: 1}),
                     **leak.versions(B[b][0][keep], B[b][2])},
        }
        print(b, {k: round(v, 3) if isinstance(v, float) else v for k, v in out["blocks"][b].items() if k != "solo"}, flush=True)
    three = ["picture", "composition", "colour"]
    G = [0.0, 0.35, 0.5, 0.71, 1.0, 1.41, 2.0]
    for rule in RULES:
        r = {}
        eq = {b: 1.0 for b in three}
        r["equal3_control"] = control(rule, eq)
        r["equal3_solo"] = solo(rule, eq)
        eq4 = {b: 1.0 for b in NAMES}
        r["equal4_control"] = control(rule, eq4)
        r["form_equal_control"] = control(rule, {"composition": 1.0, "colour": 1.0})
        # the composition : colour weight ratio at which the two control the form list equally
        lo, hi = 0.1, 10.0
        for _ in range(18):
            mid = float(np.sqrt(lo * hi))
            c = control(rule, {"composition": mid, "colour": 1.0})
            lo, hi = (lo, mid) if c["composition"] > c["colour"] else (mid, hi)
        r["form_balanced_ratio"] = mid
        r["form_balanced_control"] = c
        # the weights at which the three control the whole-picture list equally (coordinate search)
        w = dict(eq)
        for _ in range(12):
            c = control(rule, w)
            m = np.mean(list(c.values()))
            for b in ("composition", "colour"):
                w[b] *= float(np.clip((m / max(c[b], 1e-3)) ** 0.5, 0.7, 1.4))
            c = control(rule, w)
            w["picture"] *= float(np.clip((np.mean(list(c.values())) / max(c["picture"], 1e-3)) ** 0.5, 0.7, 1.4))
            mx = w["picture"]
            w = {b: v / mx for b, v in w.items()}
        r["whole_balanced_weights"] = w
        r["whole_balanced_control"] = control(rule, w)
        grid = []
        for wc, wk in itertools.product(G, G):
            w = {"picture": 1.0, "composition": wc, "colour": wk}
            idx, d = top(rule, w)
            c = control(rule, w)
            grid.append({"composition": wc, "colour": wk, "control": c, "solo": solo(rule, w)})
        r["grid"] = grid
        out["rules"][rule] = r
        print(rule, "equal3", {k: round(v, 2) for k, v in r["equal3_control"].items()},
              "| form 1:1", {k: round(v, 2) for k, v in r["form_equal_control"].items()},
              "| form balanced at comp:colour", round(r["form_balanced_ratio"], 2),
              "| whole balanced w", {k: round(v, 2) for k, v in r["whole_balanced_weights"].items()}, flush=True)
    fz.dump(out, "fusion.json")
