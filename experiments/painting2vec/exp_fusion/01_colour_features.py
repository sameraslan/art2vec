"""Compute the new colour descriptors (colour2.describe) for pilot, repro and versions images.

One image in memory at a time. Two stores per set: autocrop none, and autocrop frame (computed
only where the crop box differs from the whole image, otherwise copied).
Output: data/painting2vec/exp_fusion/colour2/<set>__<autocrop>.npz, row order = the feature stores'.
"""

from __future__ import annotations

import resource
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "features"))
from colour2 import describe  # noqa: E402
from preprocess import autocrop_box, load_image, stats_array  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data" / "painting2vec"
OUT = DATA / "exp_fusion" / "colour2"
OUT.mkdir(parents=True, exist_ok=True)
SETS = {"pilot": DATA / "pilot" / "images", "repro": DATA / "repro", "versions": DATA / "versions" / "images"}

if __name__ == "__main__":
    for name, d in SETS.items():
        if (OUT / f"{name}__frame.npz").exists():
            continue
        ids = (DATA / "features" / name / "composition.ids.txt").read_text().split()
        acc = {"none": {}, "frame": {}}
        cropped = np.zeros(len(ids), bool)
        t0 = time.time()
        for i, q in enumerate(ids):
            img = load_image(d / f"{q}.jpg")
            f = describe(stats_array(img))
            box = autocrop_box(img, "frame")
            if box != (0, 0, img.width, img.height):
                cropped[i] = True
                g = describe(stats_array(img.crop(box)))
            else:
                g = f
            for k, v in f.items():
                acc["none"].setdefault(k, []).append(v)
            for k, v in g.items():
                acc["frame"].setdefault(k, []).append(v)
            if i % 200 == 0:
                rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20
                print(f"{name} {i}/{len(ids)} {time.time()-t0:.0f}s peak {rss:.0f} MB", flush=True)
        for ac in acc:
            np.savez(OUT / f"{name}__{ac}.npz", cropped=cropped, **{k: np.stack(v).astype(np.float32) for k, v in acc[ac].items()})
        (OUT / f"{name}.ids.txt").write_text("\n".join(ids))
        print(name, "done", int(cropped.sum()), "cropped", flush=True)
