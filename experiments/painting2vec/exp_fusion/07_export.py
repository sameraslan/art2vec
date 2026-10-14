"""Part 6: export for the static proof-of-concept page in data/painting2vec/demo/.

Everything the page shows is precomputed here: per lens an ordered top-100 neighbour list, an
ordered top-10 list among paintings at least 150 years away, and a map position. The browser does
no distance maths; its filters only hide entries of these lists.

  data/paintings.json     one row per painting (the 1,972 kept pilot paintings), column-wise
  data/lenses.json        the lens set, weights, scaling rule, counts
  data/lens_<id>.json     {"xy": [x0, y0, x1, y1, ...], "nn": [[...100], ...], "far": [[...10], ...]}
  thumbs/<qid>.jpg        256 px on the long side
  large/<qid>.jpg         512 px on the long side (the detail view)
  atlas.jpg               64 px cells, 45 per row, for drawing the map quickly
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from PIL import Image

import blocks
import fz

ATLAS_CELL, ATLAS_COLS, FAR_GAP = 64, 45, 150


def clean(v):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return None
    return v


def palette(im, k=5):
    q = im.resize((64, 64)).quantize(k, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[: 3 * k]
    cnt = sorted(q.getcolors(), reverse=True)
    return ["#%02x%02x%02x" % tuple(pal[3 * i : 3 * i + 3]) for _, i in cnt]


if __name__ == "__main__":
    m = fz.meta()
    m = m[m.keep].reset_index(drop=True)
    n = len(m)
    demo = fz.DEMO
    for d in ("data", "thumbs", "large"):
        (demo / d).mkdir(parents=True, exist_ok=True)
    year = m.inception_year.values.astype(float)

    # images
    rows = -(-n // ATLAS_COLS)
    atlas = Image.new("RGB", (ATLAS_COLS * ATLAS_CELL, rows * ATLAS_CELL), (24, 24, 24))
    tw, th, pals = [], [], []
    for i, q in enumerate(m.qid):
        im = Image.open(fz.DATA / "pilot" / "images" / f"{q}.jpg").convert("RGB")
        big = im.copy()
        big.thumbnail((512, 512), Image.LANCZOS)
        if not (demo / "large" / f"{q}.jpg").exists():
            big.save(demo / "large" / f"{q}.jpg", quality=80, optimize=True)
        t = big.copy()
        t.thumbnail((256, 256), Image.LANCZOS)
        if not (demo / "thumbs" / f"{q}.jpg").exists():
            t.save(demo / "thumbs" / f"{q}.jpg", quality=82, optimize=True)
        tw.append(t.width)
        th.append(t.height)
        pals.append(palette(t))
        a = t.copy()
        a.thumbnail((ATLAS_CELL, ATLAS_CELL), Image.LANCZOS)
        atlas.paste(a, ((i % ATLAS_COLS) * ATLAS_CELL, (i // ATLAS_COLS) * ATLAS_CELL))
        if i % 400 == 0:
            print("images", i, flush=True)
    atlas.save(demo / "atlas.jpg", quality=80, optimize=True)

    def col(name, f=lambda v: v):
        return [clean(f(v)) if not (isinstance(v, float) and np.isnan(v)) else None for v in m[name].tolist()]

    P = {
        "n": n,
        "atlas": {"cell": ATLAS_CELL, "cols": ATLAS_COLS},
        "qid": m.qid.tolist(),
        "title": col("title"),
        "painter": col("creator_name"),
        "painter_id": col("creator_qid"),
        "year": [None if not np.isfinite(v) else int(v) for v in year],
        "medium": col("materials", lambda s: s.replace("|", ", ")),
        "height_cm": col("height_cm"),
        "width_cm": col("width_cm"),
        "collection": col("collection_name"),
        "country": col("country_name"),
        "tradition": col("tradition"),
        "genre": col("genres", lambda s: s.replace("|", ", ")),
        "tw": tw,
        "th": th,
        "palette": pals,
    }
    (demo / "data" / "paintings.json").write_text(json.dumps(P, ensure_ascii=False, separators=(",", ":")))

    lenses = []
    hy = np.isfinite(year)
    for lid, L in blocks.LENSES.items():
        z = np.load(fz.OUT / f"lens_{lid}.npz")
        idx, Z = z["idx"], z["Z"]
        xy = np.load(fz.OUT / f"map_{lid}.npy")
        D = fz.sqdist(Z)
        np.fill_diagonal(D, np.inf)
        gap = np.abs(year[:, None] - year[None])
        D[~(gap >= FAR_GAP)] = np.inf  # also removes paintings with no year (nan compares false)
        far = np.argsort(D, axis=1, kind="stable")[:, :10]
        ok = np.isfinite(np.take_along_axis(D, far, 1))
        far = [[int(j) for j, o in zip(r, k) if o] for r, k in zip(far, ok)]
        out = {"xy": [round(float(v), 4) for v in xy.ravel()], "nn": idx.tolist(), "far": far}
        (demo / "data" / f"lens_{lid}.json").write_text(json.dumps(out, separators=(",", ":")))
        lenses.append({"id": lid, "name": L["name"], "blurb": L["blurb"], "weights": L["weights"]})
    info = {
        "default": next(iter(blocks.LENSES)), "lenses": lenses, "k": int(idx.shape[1]), "far_gap_years": FAR_GAP,
        "scaling_rule": blocks.RULE, "n": n,
        "note": "Neighbour lists and map positions are precomputed; filters hide entries and never change distances.",
    }
    (demo / "data" / "lenses.json").write_text(json.dumps(info, indent=1))
    import shutil

    shutil.copy(fz.HERE / "demo_page" / "index.html", demo / "index.html")
    print("exported", n, "paintings,", len(lenses), "lenses to", demo)
