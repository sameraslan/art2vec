"""Part 1, follow-up: palette + low-resolution colour layout hybrids, and how much each shares with
the composition and picture blocks (top-10 overlap). Writes results/colour_hybrids.csv."""
import importlib.util

import numpy as np
import pandas as pd

import blocks
import fz

spec = importlib.util.spec_from_file_location("ce", fz.HERE / "02_colour_eval.py")
ce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ce)
keep = ce.keep


def raw(n, ac):
    return [fz.colour2(s, n, ac) for s in fz.SETS]


B = blocks.build(("picture", "composition"))
REFTOP = {b: fz.topk(fz.sqdist(B[b][0][keep]), 10) for b in B}


def layout_ab(n, src, ac):
    return [x.reshape(len(x), n * n, 3)[:, :, 1:].reshape(len(x), -1) for x in raw(src, ac)]


def joinw(items, ac):
    """items: list of (name or arrays, weight). Equal total variance, then weight."""
    out = [[], [], []]
    for it, w in items:
        p = ce.pre(it, ac) if isinstance(it, str) else it
        f = p[0][keep]
        s = float(np.sqrt(((f - f.mean(0)) ** 2).sum(1).mean())) or 1.0
        for i in range(3):
            out[i].append(p[i] * (w / s))
    return [np.concatenate(o, 1) for o in out]


rows = []
ac = "frame"
PAL = [("hist_sog_std", 1.0), ("sw_sog_std", 1.0)]
CASES = {
    "palette (sog,std)": PAL,
    "layout4 Lab": [("layout4_std", 1.0)],
    "layout4 ab": [(layout_ab(4, "layout4_std", ac), 1.0)],
    "layout6 ab": [(layout_ab(6, "layout6_std", ac), 1.0)],
    "palette + layout4 ab (1:1)": PAL + [(layout_ab(4, "layout4_std", ac), 1.41)],
    "palette + layout4 ab (1:2)": PAL + [(layout_ab(4, "layout4_std", ac), 2.0)],
    "palette + layout4 ab (2:1)": PAL + [(layout_ab(4, "layout4_std", ac), 1.0)],
    "palette + layout6 ab (1:1)": PAL + [(layout_ab(6, "layout6_std", ac), 1.41)],
    "palette + layout4 Lab (1:1)": PAL + [("layout4_std", 1.41)],
    "palette + layout4 ab sog,sca (1:1)": PAL + [(layout_ab(4, "layout4_sog_sca", ac), 1.41)],
    "palette + layout2 ab (1:1)": PAL + [([x.reshape(len(x), 2, 2, 2, 2, 3).mean((2, 4))[..., 1:].reshape(len(x), -1) for x in raw("layout4_std", ac)], 1.41)],
}
for name, items in CASES.items():
    xs = joinw(items, ac)
    for k, wh in ((None, False), (32, True), (64, True), (64, False)):
        if k and k > xs[0].shape[1]:
            continue
        fit = fz.Fit(xs[0][keep], k=k, whiten=wh)
        row, pp = ce.evaluate(xs, fit)
        top = fz.topk(fz.sqdist(fit(xs[0])[keep]), 10)
        rows.append({"feature": name, "treat": "euc" if not k else f"pca{k}{'w' if wh else ''}", "dim": row["dim"],
                     "r1_clean": row["r1_clean"], "kept10": row["ov10_clean"], "r1_primary": row["r1_primary"],
                     "under_step": row["under_step_clean"], "rnn_p90": row["rnn_p90_clean"],
                     "twonn": row["twonn"], "pal_raw": row["pal_raw"], "auc_colver": row["auc_colver"],
                     "shared_with_composition": fz.overlap(top, REFTOP["composition"]),
                     "shared_with_picture": fz.overlap(top, REFTOP["picture"])})
df = pd.DataFrame(rows)
df.to_csv(fz.RES / "colour_hybrids.csv", index=False, float_format="%.4f")
pd.set_option("display.width", 250)
print(df.round(3).to_string(index=False))
