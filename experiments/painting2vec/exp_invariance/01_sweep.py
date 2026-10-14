"""Run every feature part x variant x treatment. Writes
  data/painting2vec/exp_invariance/sweep_<family>.npz   per-pair numbers, [variants, 563, 9]
  experiments/painting2vec/exp_invariance/results_<family>.csv   one row per variant

usage: python 01_sweep.py colour|composition|learned|autocrop
"""

from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

from common import HERE, NP, OUT, PERPAIR, Universe, concat_scaled, evaluate, load_univ, summarise, treatments

NORMS = ["raw", "greyworld", "lstd", "std", "rank"]
CPARTS = ["palette_hist", "palette_sw", "palette_kmeans", "lightness", "chroma", "hue"]
COMP_PARTS = ["grid8_an", "grid8_ap", "grid4_an", "grid4_ap", "symmetry", "balance", "edges", "spectrum", "saliency", "aspect"]
LEARNED = {
    "dinov2_b": (["center", "pad", "tile"], ["cls", "patch_mean", "meanstd_early", "gram_early", "meanstd_mid", "gram_mid", "meanstd_late", "gram_late"]),
    "dinov2_l": (["pad", "tile"], ["cls", "patch_mean", "meanstd_early", "gram_early", "meanstd_mid", "gram_mid", "meanstd_late", "gram_late"]),
    "siglip2_b": (["center", "pad", "tile"], ["embed", "patch_mean"]),
    "clip_l": (["pad", "tile"], ["embed", "backbone"]),
    "csd_l": (["pad", "tile"], ["style", "content", "backbone"]),
}

u = Universe()
rows, perpair, names = [], [], []
PRIM = u.primary
CLEAN = u.primary & (u.flag == "none")


def record(block, store, part, treat, metric, x, v, pr, autocrop="none", **kw):
    pp, sl = evaluate(u, metric, x, v, **kw)
    r = {"block": block, "store": store, "part": part, "treat": treat, "metric": metric, "autocrop": autocrop,
         "dim": x.shape[1], "pr": pr, **sl}
    for tag, m in (("prim", PRIM), ("clean", CLEAN)):
        r.update({f"{tag}_{k}": val for k, val in summarise(pp, m).items()})
    rows.append(r)
    perpair.append(pp)
    names.append("|".join([block, store, part, treat, autocrop]))


def run_vec(block, store, part, x, v, learned, which=None, autocrop="none"):
    for name, metric, xt, vt, pr in treatments(x, v, learned, which):
        record(block, store, part, name, metric, xt, vt, pr, autocrop)


def colour_parts(norm, repro_dir="repro", versions=True):
    return {p: load_univ(f"colour__{norm}", p, repro_dir, versions) for p in CPARTS}


COLOUR_COMBOS = {
    "hist+sw": ["palette_hist", "palette_sw"],
    "L+C+H": ["lightness", "chroma", "hue"],
    "hist+L+C+H": ["palette_hist", "lightness", "chroma", "hue"],
    "sw+H": ["palette_sw", "hue"],
    "hist+H": ["palette_hist", "hue"],
    "ALL5": ["palette_hist", "palette_sw", "lightness", "chroma", "hue"],
}


def sq(a):
    return None if a is None else a * a


def colour(repro_dir="repro", autocrop="none", full=True):
    hists = {}
    for norm in NORMS:
        P = colour_parts(norm, repro_dir, versions=True)
        store = f"colour__{norm}"
        which = None if full else {"euc", "cen", "pca64w"}
        for p in CPARTS:
            x, v = P[p]
            if norm == "rank" and p == "lightness":
                continue  # constant by construction
            run_vec("colour", store, p, x, v, False, which, autocrop)
        for cname, cp in COLOUR_COMBOS.items():
            cp = [p for p in cp if not (norm == "rank" and p == "lightness")]
            x, v = concat_scaled([P[p] for p in cp])
            run_vec("colour", store, cname, x, v, False, which, autocrop)
        if full:
            # histogram-specific distances
            x, v = P["palette_hist"]
            record("colour", store, "palette_hist", "tv_l1", "l1", sq(x), sq(v), np.nan, autocrop)
            record("colour", store, "palette_hist", "plain_euc", "euc", sq(x), sq(v), np.nan, autocrop)
            for p, nb in (("lightness", 16), ("chroma", 16)):
                if norm == "rank" and p == "lightness":
                    continue
                x, v = P[p]
                record("colour", store, p, "hist_hellinger", "euc", x[:, :nb], v[:, :nb], np.nan, autocrop)
                record("colour", store, p, "hist_emd", "l1", np.cumsum(sq(x[:, :nb]), 1), np.cumsum(sq(v[:, :nb]), 1), np.nan, autocrop)
                record("colour", store, p, "summary5", "euc", x[:, nb:], v[:, nb:], np.nan, autocrop)
            x, v = P["hue"]
            record("colour", store, "hue", "hist_hellinger", "euc", x[:, :24], v[:, :24], np.nan, autocrop)
            record("colour", store, "hue", "hist_circ_emd", "circ_emd", sq(x[:, :24]), sq(v[:, :24]), np.nan, autocrop)
            x, v = P["palette_kmeans"]
            record("colour", store, "palette_kmeans", "sinkhorn_emd", "sinkhorn", x, v, np.nan, autocrop, sample_pp=300)
        hists[norm] = {p: P[p] for p in ("palette_hist", "palette_sw", "hue", "lightness", "chroma")}
        print(norm, len(rows), time.strftime("%X"), flush=True)
    # cross-normalisation combinations
    cross = {
        "hist[raw+std]": [("raw", "palette_hist"), ("std", "palette_hist")],
        "hist[greyworld+lstd]": [("greyworld", "palette_hist"), ("lstd", "palette_hist")],
        "hist[greyworld+std]": [("greyworld", "palette_hist"), ("std", "palette_hist")],
        "hist[all5]": [(n, "palette_hist") for n in NORMS],
        "sw[greyworld+std]": [("greyworld", "palette_sw"), ("std", "palette_sw")],
        "hist[std]+sw[std]+hue[greyworld]": [("std", "palette_hist"), ("std", "palette_sw"), ("greyworld", "hue")],
        "hist[std]+L[raw]+C[raw]": [("std", "palette_hist"), ("raw", "lightness"), ("raw", "chroma")],
        "hist[std]+L[greyworld]+C[greyworld]+H[greyworld]": [("std", "palette_hist"), ("greyworld", "lightness"), ("greyworld", "chroma"), ("greyworld", "hue")],
    }
    which = None if full else {"euc", "cen", "pca64w"}
    for cname, spec in cross.items():
        x, v = concat_scaled([hists[n][p] for n, p in spec])
        run_vec("colour", "colour__cross", cname, x, v, False, which, autocrop)


def composition(repro_dir="repro", autocrop="none", full=True):
    P = {p: load_univ("composition", p, repro_dir) for p in COMP_PARTS}
    which = None if full else {"euc", "cen", "zs", "pca64w"}
    for p in COMP_PARTS:
        x, v = P[p]
        w = {"euc"} if p == "aspect" else which
        run_vec("composition", "composition", p, x, v, False, w, autocrop)
    for g in ("grid8_an", "grid8_ap", "grid4_an", "grid4_ap"):
        x, v = P[g]
        n = x.shape[1] // 3
        for i, ch in enumerate("LCE"):
            run_vec("composition", "composition", f"{g}[{ch}]", x[:, i * n:(i + 1) * n], v[:, i * n:(i + 1) * n], False,
                    {"euc", "cen", "zs"}, autocrop)
    glob = ["symmetry", "balance", "edges", "spectrum", "saliency"]
    combos = {
        "grids_an": ["grid8_an", "grid4_an"],
        "grids_ap": ["grid8_ap", "grid4_ap"],
        "grid8_an+ap": ["grid8_an", "grid8_ap"],
        "globals": glob,
        "globals-saliency": ["symmetry", "balance", "edges", "spectrum"],
        "grid8_an+globals": ["grid8_an"] + glob,
        "grid8_ap+globals": ["grid8_ap"] + glob,
        "grid8_an+globals+aspect": ["grid8_an"] + glob + ["aspect"],
        "grid8_an+saliency": ["grid8_an", "saliency"],
        "grid8_an+aspect": ["grid8_an", "aspect"],
        "ALL": COMP_PARTS,
        "ALL-aspect": COMP_PARTS[:-1],
    }
    for cname, cp in combos.items():
        x, v = concat_scaled([P[p] for p in cp])
        run_vec("composition", "composition", cname, x, v, False, which, autocrop)


def learned(models=None, repro_dir="repro", autocrop="none", full=True):
    which = None if full else {"cos", "cen", "pca64w"}
    for model, (views, parts) in LEARNED.items():
        if models and model not in models:
            continue
        for view in views:
            if autocrop != "none" and (model, view) != ("dinov2_b", "pad"):
                continue
            store = f"{model}__{view}"
            for p in parts:
                x, v = load_univ(store, p, repro_dir)
                run_vec("learned", store, p, x, v, True, which, autocrop)
                del x, v
            print(store, len(rows), time.strftime("%X"), flush=True)


def sanity():
    """The repro commons rows must equal the pilot rows (they are hard links to the same file)."""
    rep = []
    for store, part in (("composition", "grid8_an"), ("colour__raw", "palette_hist"), ("dinov2_b__pad", "cls"), ("csd_l__pad", "style")):
        x, _ = load_univ(store, part, versions=False)
        pix = {q: i for i, q in enumerate(u.pilot_ids)}
        dif = [float(np.abs(x[NP + i] - x[pix[u.qid[NP + i]]]).max()) for i in range(u.nr) if u.src[NP + i] == "commons"]
        rep.append((store, part, len(dif), max(dif), float(np.abs(x[:NP]).mean())))
    return rep


if __name__ == "__main__":
    fam = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if fam == "sanity":
        for r in sanity():
            print(r)
        sys.exit()
    if fam == "colour":
        colour()
    elif fam == "composition":
        composition()
    elif fam == "learned":
        learned()
    elif fam == "autocrop":
        # same variants under none / border / frame, with A taken from the repro store in each case
        for mode, d in (("none", "repro"), ("border", "repro_autocrop_border"), ("frame", "repro_autocrop_frame")):
            colour(d, mode, full=False)
            composition(d, mode, full=False)
            if mode == "frame":
                learned({"dinov2_b"}, d, mode, full=False)
        # dinov2_b pad with autocrop none is in the learned sweep; repeat here for a like-for-like table
        which = {"cos", "cen", "pca64w"}
        for p in LEARNED["dinov2_b"][1]:
            x, v = load_univ("dinov2_b__pad", p, "repro")
            run_vec("learned", "dinov2_b__pad", p, x, v, True, which, "none")
    df = pd.DataFrame(rows)
    df.to_csv(HERE / f"results_{fam}.csv", index=False, float_format="%.4g")
    np.savez_compressed(OUT / f"sweep_{fam}.npz", perpair=np.stack(perpair), names=np.array(names), cols=np.array(PERPAIR))
    print(fam, len(rows), "variants", round(time.time() - t0), "s")
