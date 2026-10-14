"""Small follow-up numbers quoted in the README."""
import csv
import numpy as np
import pandas as pd
from common import DATASET, NP, OUT, Universe

u = Universe()
z = np.load(OUT / "sweep_autocrop.npz")
ix = {n: i for i, n in enumerate(z["names"])}
P = z["perpair"]
print("rank transitions under auto-crop (worst of the two directions), all 563 rows")
for key in ("composition|composition|grid8_an|euc", "colour|colour__std|hist+sw|pca64w", "learned|dinov2_b__pad|cls|cen"):
    a = P[ix[key + "|none"]]
    w0 = np.maximum(a[:, 0], a[:, 1])
    for mode in ("border", "frame"):
        if key + "|" + mode not in ix:
            continue
        b = P[ix[key + "|" + mode]]
        w1 = np.maximum(b[:, 0], b[:, 1])
        print(f"  {key} {mode}: fixed (>1 -> 1) {int(((w0 > 1) & (w1 == 1)).sum())}, broken (1 -> >1) {int(((w0 == 1) & (w1 > 1)).sum())}, "
              f"rank improved {int((w1 < w0).sum())}, worsened {int((w1 > w0).sum())}")
# version siblings inside the pilot
pil = set(u.pilot_ids)
rq = set(u.qid[NP:])
vp = [r for r in csv.DictReader(open(DATASET / "version_pairs.csv")) if r["qid_a"] in pil and r["qid_b"] in pil]
print("version pairs with both members in the pilot:", len(vp), "of which touch a repro painting:", sum((r["qid_a"] in rq) or (r["qid_b"] in rq) for r in vp))
# clean failures of the subject pick
l = np.load(OUT / "sweep_learned.npz")
lx = {n: i for i, n in enumerate(l["names"])}
p = l["perpair"][lx["learned|dinov2_l__tile|cls|cen|none"]]
clean = u.primary & (u.flag == "none")
for i in np.where(clean & ((p[:, 0] > 1) | (p[:, 1] > 1)))[0]:
    print("subject clean failure:", u.pairs[i]["qid"], u.pairs[i]["title"], u.pairs[i]["source_b"], p[i, :5].round(2))
w = pd.read_csv("worst_pairs.csv")
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 200)
print(w[["block", "qid", "a", "b", "flag", "lab_diff", "rank_ab", "rank_ba", "rnn", "ov10", "title"]].assign(a=w.a.str.split("__").str[1], b=w.b.str.split("__").str[1], title=w.title.str[:38]).to_string(index=False))
