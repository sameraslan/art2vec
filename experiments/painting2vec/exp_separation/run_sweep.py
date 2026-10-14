"""Stage 1: every stored part (pad view) and the derived first/second-order parts, default treatment.

Default treatment: L2 rows for first-order tokens and heads, per-dimension z-score for statistics
parts; centre on the kept-pilot mean; PCA to 64; cosine distance.
"""
import json
import sys
import time

import numpy as np

from cands import COLOUR_PARTS, COMP_PARTS, Cands
from evals import Evaluator
from lib import OUT

ev = Evaluator()
C = Cands(ev.keep_fit)
res_path = OUT / "metrics.json"
res = json.loads(res_path.read_text()) if res_path.exists() else {}


def run(name, pair, **kw):  # kw: probes, k_probe
    if name in res and "--force" not in sys.argv:
        return
    t = time.time()
    P, V = pair
    res[name] = ev.evaluate(P[ev.keep], V, **kw)
    res_path.write_text(json.dumps(res, indent=1))
    print(f"{name:45s} {time.time()-t:5.1f}s genre {res[name]['genre_p10']:.3f} painterAUCdiff {res[name]['painter_auc_diffgenre']:.3f}", flush=True)


if __name__ == "__main__":
    print("kept", ev.n, "chance", ev.chance, "describer n", ev.d_n)
    json.dump({"chance": ev.chance, "n_kept": ev.n, "describer_n": ev.d_n,
               "excluded": ev.meta_all.qid[~ev.keep].tolist(),
               "hand_counts": ev.pairs.groupby(["relation", "composition_match", "hand"]).size().reset_index(name="n").to_dict("records")},
              open(OUT / "setup.json", "w"), indent=1)
    dparts = ["cls", "patch_mean"] + [f"{a}_{l}" for a in ("mean", "std", "meanstd", "gram", "gramlog") for l in ("early", "mid", "late")]
    for store in ("dinov2_b__pad", "dinov2_l__pad"):
        for p in dparts:
            run(f"{store}/{p}", C.base(store, p))
    for store, parts in (("siglip2_b__pad", ["embed", "patch_mean"]), ("clip_l__pad", ["embed", "backbone"]),
                         ("csd_l__pad", ["style", "content", "backbone"])):
        for p in parts:
            run(f"{store}/{p}", C.base(store, p))
    for norm in ("raw", "greyworld", "lstd", "std", "rank"):
        run(f"colour__{norm}/all", C.colour(norm))
    for p in COLOUR_PARTS:
        run(f"colour__lstd/{p}", C.base("colour__lstd", p))
    run("composition/all", C.composition())
    for p in COMP_PARTS:
        run(f"composition/{p}", C.base("composition", p))
    # a random baseline: 64 Gaussian dimensions
    rng = np.random.default_rng(0)
    run("random/gauss64", (rng.normal(size=(2000, 64)).astype(np.float32), rng.normal(size=(355, 64)).astype(np.float32)))
