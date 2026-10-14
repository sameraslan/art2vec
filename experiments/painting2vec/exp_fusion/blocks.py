"""The blocks, the scaling rules, the lenses, and contact sheets.

A block is three float32 arrays (pilot 2000 rows, repro 689, versions 355) compared with Euclidean
distance. Unit rows make Euclidean distance rank as cosine.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

import fz

# Colour recipe chosen in Part 1 (02_colour_eval.py, 03_colour_pick.py). Parts are colour2 names.
COLOUR = {"parts": ["hist_sog_std", "sw_sog_std", "hist_raw_sca", "sw_raw_sca"], "ac": "frame", "k": 64, "whiten": True, "unit": True}
HISTS = ("hist", "hue12", "hue6", "lc_copula", "copula")

# Scaling rule and lens set chosen in Part 2 (04_fusion.py). Weights multiply the scaled vectors.
RULE = "variance"
LENSES = {
    "whole": {"name": "Whole picture", "weights": {"picture": 1.0, "composition": 1.0, "colour": 0.5},
              "blurb": "What is shown and how it looks, with the arrangement at full weight and the palette at half."},
    "picture": {"name": "Picture only", "weights": {"picture": 1.0},
                "blurb": "What is shown and how it is painted, as one learned block. Carries period."},
    "form": {"name": "Form", "weights": {"composition": 1.4, "colour": 1.0},
             "blurb": "Arrangement and palette with the picture block off. Crosses subject and period."},
    "composition": {"name": "Composition", "weights": {"composition": 1.0},
                    "blurb": "Where light, colour and edges sit on the surface. Nothing else."},
    "colour": {"name": "Colour", "weights": {"colour": 1.0},
               "blurb": "Palette alone. About two thirds of each list depends on the photograph, so treat it as a suggestion."},
}
# Variants scored in 05_lenses.py for comparison and not exported.
VARIANTS = {
    "whole_equal": {"name": "Whole, colour at full weight", "weights": {"picture": 1.0, "composition": 1.0, "colour": 1.0}},
    "whole_nocolour": {"name": "Whole, no colour", "weights": {"picture": 1.0, "composition": 1.0}},
    "whole_texture": {"name": "Whole + texture 0.7", "weights": {"picture": 1.0, "composition": 1.0, "colour": 0.5, "texture": 0.7}},
    "picture_texture": {"name": "Picture + texture 1.0", "weights": {"picture": 1.0, "texture": 1.0}},
    "texture": {"name": "Texture alone", "weights": {"texture": 1.0}},
}


def colour_part(setname, name, ac):
    """A stored colour2 part, or a derived one: `layout<n>ab_<norm>` keeps only the a, b channels of
    the layout grid; `hue6_<norm>` merges the 12 hue families into 6. Histograms are square-rooted."""
    import re

    m = re.fullmatch(r"layout(\d)ab_(.+)", name)
    if m:
        n = int(m.group(1))
        x = fz.colour2(setname, f"layout{n}_{m.group(2)}", ac)
        return x.reshape(len(x), n * n, 3)[:, :, 1:].reshape(len(x), -1)
    if name.startswith("hue6_"):
        x = fz.colour2(setname, name.replace("hue6_", "hue12_"), ac)
        return np.sqrt(x[:, :12].reshape(len(x), 6, 2).sum(2))
    x = fz.colour2(setname, name, ac)
    return np.sqrt(np.maximum(x, 0)) if name.startswith(HISTS) else x


def colour_join(parts, ac, keep):
    """Parts ("name" or "name*weight") each divided by the root of its total variance on the kept
    pilot rows, multiplied by its weight, and joined. Returns [pilot, repro, versions]."""
    out = [[], [], []]
    for p in parts:
        name, w = (p.split("*") + ["1"])[:2]
        xs = [colour_part(s, name, ac) for s in fz.SETS]
        f = xs[0][keep]
        s = float(np.sqrt(((f - f.mean(0)) ** 2).sum(1).mean())) or 1.0
        for i in range(3):
            out[i].append(xs[i] * (float(w) / s))
    return [np.concatenate(o, 1) for o in out]


def colour_block(recipe=None):
    r = recipe or COLOUR
    keep = fz.meta().keep.values
    xs = colour_join(r["parts"], r["ac"], keep)
    fit = fz.Fit(xs[0][keep], k=min(r["k"], xs[0].shape[1]) if r["k"] else None, whiten=r["whiten"], unit_out=r.get("unit", False))
    return [fit(x) for x in xs]


def build(names=("picture", "composition", "colour", "texture")):
    keep = fz.meta().keep.values
    B = {}
    for n in names:
        if n == "picture":  # DINOv2-L cls, tile, L2, centre, PCA 64, no whitening, cosine
            xs = [fz.store(s, "dinov2_l__tile", "cls") for s in fz.SETS]
            fit = fz.Fit(xs[0][keep], pre="l2", k=64, unit_out=True)
        elif n == "texture":  # DINOv2-L gram_late, same treatment
            xs = [fz.store(s, "dinov2_l__tile", "gram_late") for s in fz.SETS]
            fit = fz.Fit(xs[0][keep], pre="l2", k=64, unit_out=True)
        elif n == "composition":  # grid8_an, PCA 128 whitened, unit rows (cosine): see 04b_hub_treatments.py
            xs = [fz.store(s, "composition", "grid8_an") for s in fz.SETS]
            fit = fz.Fit(xs[0][keep], k=128, whiten=True, unit_out=True)
        elif n == "colour":
            B[n] = colour_block()
            continue
        B[n] = [fit(x) for x in xs]
    return B


def scales(xk: np.ndarray) -> dict[str, float]:
    """Divisors (in distance units) under each rule, from the kept pilot rows of one block."""
    xc = xk - xk.mean(0)
    d2 = fz.sqdist(xk)
    iu = np.triu_indices(len(xk), 1)
    off = d2[iu]
    np.fill_diagonal(d2, np.inf)
    part = np.sqrt(np.partition(d2, 9, axis=1)[:, :10])
    ev = np.linalg.eigvalsh((xc.T @ xc).astype(np.float64) / len(xc))
    return {
        "variance": float(np.sqrt((xc**2).sum(1).mean())),  # equal total variance (the root's rule)
        "mfa": float(np.sqrt(ev[-1])),  # first singular value (Multiple Factor Analysis)
        "nn1": float(np.median(part.min(1))),  # equal median nearest-neighbour distance
        "nn10": float(np.median(part.max(1))),  # equal median 10th-neighbour distance
        "spread": float(np.sqrt(off.std())),  # equal sd of squared distance over all pairs
    }


def fuse(B, weights: dict[str, float], sc: dict[str, float], which=0):
    """Concatenate blocks, each divided by its scale and multiplied by its weight. `which` = 0 pilot,
    1 repro, 2 versions. Squared distance in the result = sum_b (w_b / s_b)^2 d_b^2."""
    return np.concatenate([B[b][which] * (w / sc[b]) for b, w in weights.items() if w > 0], 1)


# ---------------------------------------------------------------- sheets

_T = 150


def _thumb(path, T=_T):
    im = Image.open(path).convert("RGB")
    im.thumbnail((T - 4, T - 4), Image.LANCZOS)
    cell = Image.new("RGB", (T, T), (60, 60, 60))
    cell.paste(im, ((T - im.width) // 2, (T - im.height) // 2))
    return cell


def sheet(path, rows, T=_T, caption=None):
    """rows: list of (label, seed_qid, [neighbour qids]). caption(qid) -> short text or None."""
    k = max(len(r[2]) for r in rows)
    ch = 12 if caption else 0
    im = Image.new("RGB", (T * (k + 1) + 8, (T + ch) * len(rows)), (20, 20, 20))
    d = ImageDraw.Draw(im)
    pdir = fz.DATA / "pilot" / "images"
    for ri, (label, seed, ids) in enumerate(rows):
        y = ri * (T + ch)
        im.paste(_thumb(pdir / f"{seed}.jpg", T), (0, y))
        d.rectangle([0, y, 8 + 6 * len(label), y + 12], fill=(255, 255, 255))
        d.text((3, y), label, fill=(0, 0, 0))
        if caption:
            d.text((3, y + T), str(caption(seed))[:24], fill=(255, 220, 120))
        for ci, q in enumerate(ids):
            x = T + 8 + ci * T
            im.paste(_thumb(pdir / f"{q}.jpg", T), (x, y))
            if caption:
                d.text((x + 3, y + T), str(caption(q))[:24], fill=(200, 200, 200))
    im.save(path, quality=85)
