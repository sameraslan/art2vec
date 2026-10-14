"""Two cheap intake gates, tested on the repro set: greyscale, and aspect ratio against the catalogue."""
import numpy as np
import pandas as pd
from common import DATASET, NP, Universe, load_part

u = Universe()
meta = pd.read_csv(DATASET / "pilot_meta.csv", usecols=["qid", "height_cm", "width_cm"]).set_index("qid")
asp = load_part("repro", "composition", "aspect")[:, 0]
chroma_mean = load_part("repro", "colour__raw", "chroma")[:, 16]
grey_share = load_part("repro", "colour__raw", "hue")[:, 24]
q = u.qid[NP:]
h = pd.to_numeric(meta.height_cm.reindex(q).astype(str).str.split("|").str[0], errors="coerce").values
w = pd.to_numeric(meta.width_cm.reindex(q).astype(str).str.split("|").str[0], errors="coerce").values
dev = np.abs(asp - np.log(w / h))
print("images with catalogue size:", int(np.isfinite(dev).sum()), "of", len(dev))
# image-level labels from the pair flags: the non-commons side of a flagged primary pair
rows = []
for i, r in enumerate(u.pairs):
    rows.append({"flag": u.flag[i], "kind": r["pair_kind"], "dev_a": dev[u.pa[i]], "dev_b": dev[u.pb[i]], "dev_max": np.nanmax([dev[u.pa[i]], dev[u.pb[i]]]),
                 "ch_min": min(chroma_mean[u.pa[i]], chroma_mean[u.pb[i]]), "grey_max": max(grey_share[u.pa[i]], grey_share[u.pb[i]])})
d = pd.DataFrame(rows)
for t in (0.03, 0.05, 0.1):
    print(f"aspect differs from catalogue by more than {t} (log units), share of pairs by flag:")
    print((d.assign(hit=d.dev_max > t).groupby("flag").hit.agg(["mean", "sum", "size"])).round(3).to_string())
for t in (0.01, 0.015, 0.02):
    print(f"mean chroma of either image under {t}:")
    print((d.assign(hit=d.ch_min < t).groupby("flag").hit.agg(["mean", "sum", "size"])).round(3).to_string())
print("pilot images: mean chroma under 0.01 / 0.015 / 0.02:", [(load_part("pilot", "colour__raw", "chroma")[:, 16] < t).sum() for t in (0.01, 0.015, 0.02)])
