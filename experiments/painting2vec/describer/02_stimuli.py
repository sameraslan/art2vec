"""Anonymised stimuli, the batch plan and measured colour statistics.

Four presentations per painting:
  orig    the picture as stored
  mirror  6 % cropped from each edge, then flipped left-right
  told    the picture as stored, and the describer is told title, painter and year
  retest  the picture as stored, again, for a different describer

Every stimulus is re-encoded from pixels only (no EXIF, no ICC, no comment) under a random
code. 20 batches of 12: each batch holds 3 presentations of each kind (one famous, one mid,
one obscure painting per kind) and never two presentations of one painting.

  uv run --no-project --with pillow --with numpy --with pandas python experiments/painting2vec/describer/02_stimuli.py
"""
import json
import os
import string

import numpy as np
import pandas as pd
from PIL import Image, ImageOps

SEED = 20261008
HERE = "experiments/painting2vec/describer"
DATA = os.path.abspath("data/painting2vec/describer")
CONDS = ["orig", "mirror", "told", "retest"]
OFFSET = {"orig": 0, "mirror": 1, "told": 3, "retest": 7}  # distinct differences mod 20
NB = 20


def stats(im):
    a = np.asarray(im.convert("RGB").resize((96, 96)), dtype=np.float32) / 255.0
    luma = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    sat = a.max(-1) - a.min(-1)
    hsv = np.asarray(im.convert("HSV").resize((96, 96)), dtype=np.float32)
    hue = hsv[..., 0] / 255.0 * 2 * np.pi
    w = sat + 1e-6
    hx, hy = (np.cos(hue) * w).sum() / w.sum(), (np.sin(hue) * w).sum() / w.sum()
    return {
        "luma_mean": luma.mean(), "luma_std": luma.std(), "dark_frac": (luma < 0.2).mean(),
        "sat_mean": sat.mean(), "warm_minus_cool": (a[..., 0] - a[..., 2]).mean(),
        "hue_spread": 1 - np.hypot(hx, hy),  # circular variance of hue, weighted by saturation
    }


def main():
    rng = np.random.RandomState(SEED)
    s = pd.read_csv(f"{HERE}/sample.csv")
    os.makedirs(f"{DATA}/stimuli", exist_ok=True)
    os.makedirs(f"{DATA}/batches", exist_ok=True)
    os.makedirs(f"{DATA}/out", exist_ok=True)

    # groups of three: one painting from each fame level
    s["group"] = -1
    for f in ["famous", "mid", "obscure"]:
        idx = s.index[s.fame == f].to_numpy()
        s.loc[idx, "group"] = rng.permutation(NB)

    codes = set()
    rows, st = [], []
    for _, p in s.iterrows():
        src = Image.open(f"data/painting2vec/pilot/images/{p.qid}.jpg").convert("RGB")
        st.append({"qid": p.qid, **stats(src)})
        for c in CONDS:
            while True:
                code = "".join(rng.choice(list(string.ascii_lowercase + string.digits), 7))
                if code not in codes:
                    codes.add(code)
                    break
            im = src
            if c == "mirror":
                w, h = src.size
                dx, dy = round(0.06 * w), round(0.06 * h)
                im = ImageOps.mirror(src.crop((dx, dy, w - dx, h - dy)))
            out = Image.new("RGB", im.size)
            out.putdata(list(im.getdata()))  # pixels only: nothing carried over from the source file
            out.save(f"{DATA}/stimuli/{code}.jpg", "JPEG", quality=90)
            rows.append({"code": code, "qid": p.qid, "fame": p.fame, "condition": c,
                         "batch": (p.group + OFFSET[c]) % NB})
    key = pd.DataFrame(rows)
    key["order"] = -1
    for b in range(NB):
        idx = key.index[key.batch == b].to_numpy()
        assert len(idx) == 12 and key.loc[idx, "qid"].is_unique
        key.loc[idx, "order"] = rng.permutation(12)
    key = key.sort_values(["batch", "order"])
    key.to_csv(f"{HERE}/key.csv", index=False)
    pd.DataFrame(st).round(4).to_csv(f"{HERE}/image_stats.csv", index=False)

    meta = s.set_index("qid")
    for b in range(NB):
        items = []
        for _, r in key[key.batch == b].iterrows():
            it = {"code": r.code, "path": f"{DATA}/stimuli/{r.code}.jpg", "told": None}
            if r.condition == "told":
                m = meta.loc[r.qid]
                painter = m.creator_name if isinstance(m.creator_name, str) else "unknown"
                it["told"] = {"title": m.title, "painter": painter.replace("|", " / "),
                              "year": int(m.inception_year)}
            items.append(it)
        with open(f"{DATA}/batches/batch_{b:02d}.json", "w") as f:
            json.dump({"batch": b, "output_path": f"{DATA}/out/batch_{b:02d}.json", "images": items},
                      f, ensure_ascii=False, indent=1)
    print(key.groupby(["batch", "condition"]).size().unstack().to_string())
    print(key.groupby(["batch", "fame"]).size().unstack().min().to_dict())


if __name__ == "__main__":
    main()
