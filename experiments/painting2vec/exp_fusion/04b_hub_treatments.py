"""Part 2, follow-up: the whitened hand-built blocks are hub machines. Which treatment keeps the
photograph-proofing without the hubs? Writes results/hub_treatments.csv."""
import numpy as np
import pandas as pd

import blocks
import fz
import leak

keep = leak.ev.keep_fit
ie = fz.InvEval()
rows = []


def run(block, name, xs, **kw):
    fit = fz.Fit(xs[0][keep], **kw)
    xp, xr, xv = (fit(x) for x in xs)
    D = np.sqrt(fz.sqdist(xp[keep]))
    np.fill_diagonal(D, np.inf)
    pp, _, _ = ie.run(xp, xr)
    s = ie.summ(pp, ie.clean)
    L = leak.lists(D)
    V = leak.versions(xp[keep], xv)
    rows.append({"block": block, "treatment": name, "dim": xp.shape[1], "repro_r1": s["r1"], "kept10": s["ov10"],
                 "under_step": s["under_step"], "hub_skew": L["hub_skew"], "in_no_list": L["hub_zero"], "hub_max": L["hub_max"],
                 "broad_p10": L["broad_p10"], "year_gap": L["year_gap"], "ver_top1": V["ver_top1"]})
    print(rows[-1], flush=True)


comp = [fz.store(s, "composition", "grid8_an") for s in fz.SETS]
col = blocks.colour_join(blocks.COLOUR["parts"], blocks.COLOUR["ac"], keep)
for block, xs in (("composition", comp), ("colour", col)):
    run(block, "as stored, Euclidean", xs)
    run(block, "z-score, Euclidean", xs, pre="z")
    for k in (16, 32, 64, 128):
        if k > xs[0].shape[1]:
            continue
        run(block, f"PCA-{k}, Euclidean", xs, k=k)
        run(block, f"PCA-{k} whitened, Euclidean", xs, k=k, whiten=True)
        run(block, f"PCA-{k} whitened, unit rows (cosine)", xs, k=k, whiten=True, unit_out=True)
        run(block, f"PCA-{k}, unit rows (cosine)", xs, k=k, unit_out=True)
pd.DataFrame(rows).to_csv(fz.RES / "hub_treatments.csv", index=False, float_format="%.4f")
