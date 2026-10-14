"""Part 1, second half: the trade-off plot, the source breakdown, the photograph-direction test,
and contact sheets for the finalists.

  plot     results/colour_tradeoff.png from results/colour_grid.csv
  source   results/colour_source.json: R@1 and list kept by source pair and by lab_diff, the
           leave-one-out source-shift correction, and removal of "photograph directions" learned
           from held-out reproduction pairs (within-pair covariance, 5 folds by painting)
  sheets   OUT/colour_sheet_*.jpg: neighbours of fixed seeds under each finalist
"""

from __future__ import annotations

import importlib.util
import sys

import numpy as np
import pandas as pd

import blocks
import fz

spec = importlib.util.spec_from_file_location("ce", fz.HERE / "02_colour_eval.py")
ce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ce)
ie, u, keep = ce.ie, ce.u, ce.keep

# label -> (parts, autocrop, pca k, whiten)
FINALISTS = {
    "A old best: palette hist+sw (std), no crop, PCA-64 w": (["hist_raw_std", "sw_raw_std"], "none", 64, True),
    "B palette hist+sw (shades-of-grey, std), frame crop, PCA-64 w": (["hist_sog_std", "sw_sog_std"], "frame", 64, True),
    "C tone bands + hue families (relational), PCA-32 w": (["tb8_std", "hue12_cen"], "frame", 32, True),
    "D hue families + warm/cool (coarse), PCA-16 w": (["hue12_raw", "warm_raw"], "frame", 16, True),
    "E colour layout 6x6 L,a,b (spatial only), PCA-32 w": (["layout6_std"], "frame", 32, True),
    "F palette + 4x4 a,b layout (1:1), PCA-32 w": (["hist_sog_std", "sw_sog_std", "layout4ab_std*1.41"], "frame", 32, True),
    "G palette + 6x6 a,b layout (1:1), PCA-64 w": (["hist_sog_std", "sw_sog_std", "layout6ab_std*1.41"], "frame", 64, True),
}
SEEDS = ["Q45585", "Q12418", "Q2016193", "Q220859", "Q500985", "Q185372", "Q1091086", "Q693746",
         "Q683274", "Q1044742", "Q698487", "Q587514"]
MUSEUMS = ("met", "nga", "rijksmuseum", "aic", "cleveland")


def vectors(parts, ac, k, whiten):
    xs = ce.join(parts, ac)
    fit = fz.Fit(xs[0][keep], k=min(k, xs[0].shape[1]), whiten=whiten) if k else fz.Fit(xs[0][keep])
    return [fit(x) for x in xs]


def groups():
    sa = np.array([r["source_a"] for r in u.pairs])
    sb = np.array([r["source_b"] for r in u.pairs])
    ok, nofl = ie.pair_ok, u.flag == "none"
    mus_b, mus_a = np.isin(sb, MUSEUMS), np.isin(sa, MUSEUMS)
    g = {
        "pilot Commons file v museum, unflagged": ok & nofl & (sa == "commons") & mus_b,
        "pilot Commons file v another Commons file, unflagged": ok & nofl & (sa == "commons") & ~mus_b,
        "two other Commons files (neither is the pilot image), unflagged": ok & nofl & (sa != "commons") & ~mus_a & ~mus_b,
        "museum v a second Commons file, unflagged": ok & nofl & mus_a,
    }
    for m in MUSEUMS:
        g[f"  Commons v {m}, unflagged"] = ok & nofl & (sa == "commons") & (sb == m)
    for lo, hi in ((1, 3), (3, 6), (6, 9), (9, 12), (12, 99)):
        g[f"lab_diff {lo}-{hi}, all rows"] = ok & (u.lab >= lo) & (u.lab < hi)
        g[f"lab_diff {lo}-{hi}, Commons v museum"] = ok & (u.lab >= lo) & (u.lab < hi) & (sa == "commons") & mus_b
        g[f"lab_diff {lo}-{hi}, Commons v Commons"] = ok & (u.lab >= lo) & (u.lab < hi) & ~mus_a & ~mus_b
    return g, sa, sb


def r1(pp, mask):
    if mask.sum() == 0:
        return None
    return float((np.concatenate([pp["rank_ab"][mask], pp["rank_ba"][mask]]) <= 1).mean())


def plot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    df = pd.read_csv(fz.RES / "colour_grid.csv")

    def fam(f):
        if f.startswith(("GREEDY",)):
            return "greedy combination"
        if "layout" in f:
            return "spatial layout"
        if f.startswith(("old:", "BASE", "hist", "sw_", "coarse")) or "hist+sw" in f:
            return "full palette (histogram, sliced Wasserstein)"
        if f.startswith(("hue", "warm")):
            return "hue families, warm/cool"
        if f.startswith(("tb", "tone")):
            return "tone bands"
        if f.startswith(("copula", "lc_", "lq", "cq", "rank")):
            return "ranks and quantiles"
        if f.startswith("pal"):
            return "small palette"
        return "other combination"

    df["family"] = df.feature.map(fam)
    cols = {"full palette (histogram, sliced Wasserstein)": "#4c78a8", "hue families, warm/cool": "#e45756",
            "tone bands": "#f58518", "ranks and quantiles": "#72b7b2", "small palette": "#b279a2",
            "spatial layout": "#54a24b", "greedy combination": "#222222", "other combination": "#9d9d9d"}
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), sharex=True)
    for name, c in cols.items():
        d = df[df.family == name]
        ax[0].scatter(d.r1_clean, d.pal_raw, s=14, c=c, alpha=0.7, label=name, linewidths=0)
        ax[1].scatter(d.r1_clean, d.twonn, s=14, c=c, alpha=0.7, linewidths=0)
    for a in ax:
        a.axvline(0.85, color="#888", lw=1, ls="--")
        a.set_xlabel("same painting, other photograph: R@1 on clean pairs")
        a.spines[["top", "right"]].set_visible(False)
    ax[0].axhline(1.0, color="#888", lw=1, ls=":")
    ax[0].set_ylabel("palette distance to the 10 neighbours / to random paintings\n(1 = neighbours share no more palette than chance)")
    ax[1].set_ylabel("intrinsic dimension (TwoNN)")
    ax[0].text(0.855, ax[0].get_ylim()[0] + 0.01, "target 0.85", color="#666", fontsize=9)
    ax[0].legend(fontsize=8, frameon=False, loc="lower left")
    fig.suptitle("Colour descriptors: surviving the photograph against still being colour", fontsize=12)
    fig.tight_layout()
    fig.savefig(fz.RES / "colour_tradeoff.png", dpi=130)


def source():
    g, sa, sb = groups()
    out = {"n": {k: int(v.sum()) for k, v in g.items()}, "variants": {}}
    for label, (parts, ac, k, wh) in FINALISTS.items():
        xp, xr, _ = vectors(parts, ac, k, wh)
        pp, _, _ = ie.run(xp, xr)
        o = {"by_group_r1": {k_: r1(pp, m) for k_, m in g.items()},
             "by_group_kept10": {k_: (float(pp["ov10"][m].mean()) if m.sum() else None) for k_, m in g.items()}}
        # leave-one-out source shift: subtract from every museum file the mean (museum - Commons)
        # difference of the OTHER paintings from that museum
        xr2 = xr.copy()
        prim = np.where(u.primary & ie.pair_ok & np.isin(sb, MUSEUMS))[0]
        for m in MUSEUMS:
            ii = [i for i in prim if sb[i] == m]
            if len(ii) < 5:
                continue
            diff = np.stack([xr[u.pb[i]] - xr[u.pa[i]] for i in ii])
            for j, i in enumerate(ii):
                xr2[u.pb[i]] = xr[u.pb[i]] - np.delete(diff, j, 0).mean(0)
            o.setdefault("source_shift_share", {})[m] = float((diff.mean(0) ** 2).sum() / (diff**2).sum(1).mean())
        pp2, _, _ = ie.run(xp, xr2)
        mm = ie.clean & np.isin(sb, MUSEUMS)
        o["museum_pairs_r1_before_after_shift_removed"] = [r1(pp, mm), r1(pp2, mm)]
        # photograph directions learned from held-out pairs
        qids = np.array([r["qid"] for r in u.pairs])
        uq = np.unique(qids[ie.clean])
        rng = np.random.default_rng(0)
        fold = dict(zip(uq[rng.permutation(len(uq))], np.arange(len(uq)) % 5))
        res = {}
        for name, kind, par in (("remove top 2", "proj", 2), ("remove top 4", "proj", 4), ("remove top 8", "proj", 8),
                                ("within-pair whitening, shrink 0.5", "wccn", 0.5), ("within-pair whitening, shrink 0.2", "wccn", 0.2)):
            hit, kept, tot = 0, 0.0, 0
            for f in range(5):
                tr = ie.clean & np.array([fold.get(q, -1) != f for q in qids])
                te = ie.clean & np.array([fold.get(q, -1) == f for q in qids])
                d = (xr[u.pb[tr]] - xr[u.pa[tr]]).astype(np.float64)
                Sw = d.T @ d / len(d)
                w, V = np.linalg.eigh(Sw)
                if kind == "proj":
                    Pm = np.eye(len(w)) - V[:, -par:] @ V[:, -par:].T
                else:
                    w2 = (1 - par) * w + par * w.mean()
                    Pm = (V / np.sqrt(w2)) @ V.T
                Pm = Pm.astype(np.float32)
                ppf, _, _ = ie.run(xp @ Pm, xr @ Pm)
                hit += (np.concatenate([ppf["rank_ab"][te], ppf["rank_ba"][te]]) <= 1).sum()
                kept += ppf["ov10"][te].sum()
                tot += te.sum()
            res[name] = {"r1": float(hit / (2 * tot)), "kept10": float(kept / tot)}
        o["photograph_directions_cv"] = res
        o["clean"] = ie.summ(pp, ie.clean)
        out["variants"][label] = o
        print(label, {k_: (round(v, 3) if v is not None else None) for k_, v in o["by_group_r1"].items() if not k_.startswith("lab")})
        print("   shift", o["museum_pairs_r1_before_after_shift_removed"], o.get("source_shift_share"))
        print("   directions", res, flush=True)
    fz.dump(out, "colour_source.json")


def sheets():
    m = fz.meta()
    qk = m.qid.values[keep]
    pos = {q: i for i, q in enumerate(qk)}
    lists = {}
    for label, (parts, ac, k, wh) in FINALISTS.items():
        xp = vectors(parts, ac, k, wh)[0][keep]
        D = fz.sqdist(xp)
        lists[label] = fz.topk(D, 8)
    # reference rows: the picture block, so colour neighbours can be told from picture neighbours
    B = blocks.build(("picture",))
    lists["Z picture block"] = fz.topk(fz.sqdist(B["picture"][0][keep]), 8)
    names = {}
    for si, s in enumerate(SEEDS):
        rows = [(lab.split(" ")[0], s, [qk[j] for j in idx[pos[s]]]) for lab, idx in lists.items()]
        blocks.sheet(fz.OUT / f"colour_sheet_{si+1:02d}_{s}.jpg", rows, T=130)
        names[s] = {lab: [qk[j] for j in idx[pos[s]]] for lab, idx in lists.items()}
    fz.dump(names, "colour_sheets.json")


def props():
    """If colour is only shown and filtered on: do coarse properties agree between two photographs?
    Spearman correlation across the clean pairs, agreement of pilot-tercile bins, and agreement of
    the dominant hue family (6 families)."""
    from scipy.stats import spearmanr

    P = {
        "mean lightness": [fz.store(s, "colour__raw", "lightness")[:, 16] for s in ("pilot", "repro")],
        "lightness spread (sd)": [fz.store(s, "colour__raw", "lightness")[:, 17] for s in ("pilot", "repro")],
        "mean chroma (how saturated)": [fz.store(s, "colour__raw", "chroma")[:, 16] for s in ("pilot", "repro")],
        "warm/cool balance": [fz.colour2(s, "warm_raw", "frame")[:, 0] for s in ("pilot", "repro")],
        "warm share of coloured pixels": [fz.colour2(s, "warm_raw", "frame")[:, 1] for s in ("pilot", "repro")],
        "lights warmer than darks": [fz.colour2(s, "warm_raw", "frame")[:, 3] for s in ("pilot", "repro")],
        "achromatic share": [fz.colour2(s, "warm_raw", "frame")[:, 4] for s in ("pilot", "repro")],
    }
    m = ie.clean
    out = {}
    for k, (p, r) in P.items():
        a, b = r[u.pa[m]], r[u.pb[m]]
        cuts = np.percentile(p[keep], [100 / 3, 200 / 3])
        cuts5 = np.percentile(p[keep], [20, 40, 60, 80])
        out[k] = {"spearman": float(spearmanr(a, b).statistic),
                  "same_tercile": float((np.digitize(a, cuts) == np.digitize(b, cuts)).mean()),
                  "same_or_adjacent_quintile": float((np.abs(np.digitize(a, cuts5) - np.digitize(b, cuts5)) <= 1).mean())}
    h = blocks.colour_part("repro", "hue6_raw", "frame") ** 2
    a, b = h[u.pa[m]], h[u.pb[m]]
    out["dominant hue family (of 6)"] = {"same": float((a.argmax(1) == b.argmax(1)).mean()),
                                         "dominant_in_other_top2": float(np.mean([x.argmax() in np.argsort(-y)[:2] for x, y in zip(a, b)]))}
    hp = blocks.colour_part("pilot", "hue6_raw", "frame")[keep] ** 2
    out["dominant hue family (of 6)"]["largest_family_share_in_pilot"] = float(np.bincount(hp.argmax(1), minlength=6).max() / len(hp))
    fz.dump(out, "colour_props.json")
    for k, v in out.items():
        print(k, {a: round(b, 3) for a, b in v.items()})


if __name__ == "__main__":
    for a in sys.argv[1:] or ["plot", "source", "props", "sheets"]:
        {"plot": plot, "source": source, "sheets": sheets, "props": props}[a]()
