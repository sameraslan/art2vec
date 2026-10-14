"""Anonymised stimuli and the batch plan.

Items (352): 240 new pilot paintings; the original 60 again (their v1 marks are the ones analysed, this pass
supplies the fields v2 adds and a v1-against-v2 check); 22 version partners that are not in the pilot; the
second photograph of 30 paintings. Every stimulus is re-encoded from pixels only under a random code.
30 batches of 11 or 12. Two images of one painting, or of two versions of one composition, never share a batch.

  uv run --no-project --with pillow --with numpy --with pandas python experiments/painting2vec/exp_describer_blocks/02_stimuli.py
"""
import json
import os
import string

import numpy as np
import pandas as pd
from PIL import Image

SEED = 20261009
HERE = "experiments/painting2vec/exp_describer_blocks"
DATA = os.path.abspath("data/painting2vec/exp_describer_blocks")
NB = 30


def main():
    rng = np.random.RandomState(SEED)
    s = pd.read_csv(f"{HERE}/sample.csv")
    ex = pd.read_csv(f"{HERE}/version_extras.csv")
    ph = pd.read_csv(f"{HERE}/photo_pairs_used.csv")
    vp = pd.read_csv(f"{HERE}/version_pairs_used.csv")
    for d in ("stimuli", "batches", "out"):
        os.makedirs(f"{DATA}/{d}", exist_ok=True)

    items = []
    for _, r in s.iterrows():
        kind = "orig60_v2" if "orig60" in r.why.split("|") else "pilot"
        items.append({"qid": r.qid, "kind": kind, "src": f"data/painting2vec/pilot/images/{r.qid}.jpg"})
    for q in ex.qid:
        items.append({"qid": q, "kind": "version_extra", "src": f"data/painting2vec/versions/images/{q}.jpg"})
    for _, r in ph.iterrows():
        items.append({"qid": r.qid, "kind": "photo_b", "src": f"data/painting2vec/repro/{r.file_b}"})
    it = pd.DataFrame(items)

    # conflict groups: same painting, or linked by a version pair
    parent = {q: q for q in it.qid}
    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for a, b in zip(vp.qid_a, vp.qid_b):
        parent[find(a)] = find(b)
    it["grp"] = it.qid.map(find)

    # deal each kind round-robin over the batches, then repair conflicts by re-drawing
    for attempt in range(1000):
        it["batch"] = -1
        start = 0
        for k in ["photo_b", "version_extra", "orig60_v2", "pilot"]:
            idx = rng.permutation(it.index[it.kind == k].to_numpy())
            it.loc[idx, "batch"] = (start + np.arange(len(idx))) % NB
            start += len(idx)
        if not it.duplicated(["batch", "grp"]).any():
            break
    else:
        raise SystemExit("no conflict-free plan")

    codes = set()
    def code():
        while True:
            c = "".join(rng.choice(list(string.ascii_lowercase + string.digits), 7))
            if c not in codes:
                codes.add(c)
                return c
    it["code"] = [code() for _ in range(len(it))]
    it["order"] = -1
    for b in range(NB):
        idx = it.index[it.batch == b].to_numpy()
        it.loc[idx, "order"] = rng.permutation(len(idx))
    it = it.sort_values(["batch", "order"])
    sizes = []
    for _, r in it.iterrows():
        src = Image.open(r.src).convert("RGB")
        if max(src.size) > 1024:
            src.thumbnail((1024, 1024), Image.LANCZOS)
        out = Image.new("RGB", src.size)
        out.putdata(list(src.getdata()))  # pixels only
        out.save(f"{DATA}/stimuli/{r.code}.jpg", "JPEG", quality=90)
        sizes.append(src.size)
    it["px_w"], it["px_h"] = [x[0] for x in sizes], [x[1] for x in sizes]
    it[["code", "qid", "kind", "batch", "order", "px_w", "px_h"]].to_csv(f"{HERE}/key.csv", index=False)
    for b in range(NB):
        imgs = [{"code": r.code, "path": f"{DATA}/stimuli/{r.code}.jpg"} for _, r in it[it.batch == b].iterrows()]
        with open(f"{DATA}/batches/batch_{b:02d}.json", "w") as f:
            json.dump({"batch": b, "output_path": f"{DATA}/out/batch_{b:02d}.json", "images": imgs}, f, indent=1)
    print(it.groupby(["batch", "kind"]).size().unstack(fill_value=0).assign(n=lambda d: d.sum(1)).to_string())
    print("attempts", attempt + 1, "| mean megapixels", round(float((it.px_w * it.px_h).mean()) / 1e6, 3))


if __name__ == "__main__":
    main()
