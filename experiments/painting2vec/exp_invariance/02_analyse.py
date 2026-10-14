"""Tables, breakdowns, bootstrap intervals, worst-pair lists, contact sheets and plots.

Reads results_*.csv and data/painting2vec/exp_invariance/sweep_*.npz (written by 01_sweep.py).
Writes tables.md and worst_pairs.csv beside this file, sheets under data/painting2vec/exp_invariance/.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from common import HERE, NP, OUT, PERPAIR, Universe, load_part, summarise

u = Universe()
C = {c: i for i, c in enumerate(PERPAIR)}
SW = {}
for fam in ("colour", "composition", "learned", "autocrop"):
    z = np.load(OUT / f"sweep_{fam}.npz")
    SW[fam] = (z["perpair"], {n: i for i, n in enumerate(z["names"])})
RES = {fam: pd.read_csv(HERE / f"results_{fam}.csv") for fam in SW}
PRIM = u.primary
CLEAN = u.primary & (u.flag == "none")
out: list[str] = []


def pp(fam, block, store, part, treat, ac="none"):
    a, ix = SW[fam]
    return a[ix["|".join([block, store, part, treat, ac])]]


def md(df: pd.DataFrame, title: str, note: str = "", fmt="%.3g") -> None:
    out.append(f"\n#### {title}\n")
    if note:
        out.append(note + "\n")
    cols = list(df.columns)
    out.append("| " + " | ".join(str(c) for c in cols) + " |")
    out.append("|" + "---|" * len(cols))
    for _, r in df.iterrows():
        out.append("| " + " | ".join((fmt % v if isinstance(v, (float, np.floating)) else str(v)) for v in r) + " |")


BEST = {  # label -> (family, block, store, part, treat)
    "subject: DINOv2-L cls, tile, centred cosine": ("learned", "learned", "dinov2_l__tile", "cls", "cen"),
    "subject (text-trained): SigLIP 2 embed, tile, centred": ("learned", "learned", "siglip2_b__tile", "embed", "cen"),
    "manner: CSD style, tile, PCA-64 whitened": ("learned", "learned", "csd_l__tile", "style", "pca64w"),
    "manner (alt.): DINOv2-L gram_late, tile, cosine": ("learned", "learned", "dinov2_l__tile", "gram_late", "cos"),
    "colour: std hist+sw, PCA-64 whitened": ("colour", "colour", "colour__std", "hist+sw", "pca64w"),
    "colour (as built): raw palette_hist, Hellinger": ("colour", "colour", "colour__raw", "palette_hist", "euc"),
    "composition: grid8_an, PCA-128 whitened": ("composition", "composition", "composition", "grid8_an", "pca128w"),
    "composition (as built): ALL parts, Euclidean": ("composition", "composition", "composition", "ALL", "euc"),
}

KEYS = ["n", "r1", "r5", "r10", "rank_med", "rank_p90", "rnn_med", "rnn_p75", "rnn_p90", "rstep_med", "rstep_p90", "rstep_lt1", "jacc", "rbo", "ov10"]


def boot(p, mask, B=1000, seed=0):
    """Bootstrap over paintings: 95 % interval for R@1 and top-10 overlap."""
    rs = np.random.RandomState(seed)
    idx = np.where(mask)[0]
    q = u.qid[NP + u.pa[idx]]
    uq, inv = np.unique(q, return_inverse=True)
    r1 = ((p[idx, 0] <= 1).astype(float) + (p[idx, 1] <= 1)) / 2
    ov = p[idx, 7]
    g = [np.where(inv == k)[0] for k in range(len(uq))]
    a, b = [], []
    for _ in range(B):
        s = np.concatenate([g[k] for k in rs.randint(len(uq), size=len(uq))])
        a.append(r1[s].mean())
        b.append(ov[s].mean())
    return np.percentile(a, [2.5, 97.5]), np.percentile(b, [2.5, 97.5])


# ---------------------------------------------------------------- 1. headline
rows = []
for lab, key in BEST.items():
    p = pp(*key)
    for tag, m in (("clean 214", CLEAN), ("all primary 274", PRIM), ("all rows 563", np.ones(len(PRIM), bool))):
        s = summarise(p, m)
        ci1, ci2 = boot(p, m)
        rows.append({"variant": lab, "pairs": tag, "R@1": s["r1"], "R@1 95% CI": f"{ci1[0]:.3f}-{ci1[1]:.3f}", "R@5": s["r5"], "R@10": s["r10"],
                     "median rank": s["rank_med"], "p90 rank": s["rank_p90"],
                     "d/NN-other med": s["rnn_med"], "p75": s["rnn_p75"], "p90": s["rnn_p90"],
                     "d/step med": s["rstep_med"], "p90 ": s["rstep_p90"], "share under 1 step": s["rstep_lt1"],
                     "Jaccard@10": s["jacc"], "RBO": s["rbo"], "overlap@10": s["ov10"], "overlap 95% CI": f"{ci2[0]:.3f}-{ci2[1]:.3f}"})
md(pd.DataFrame(rows), "H1. Headline: the chosen variant of each block", "Both directions pooled for ranks and d/NN-other.")

# distribution of the two ratios
rows = []
for lab, key in BEST.items():
    p = pp(*key)[CLEAN]
    rn = np.concatenate([p[:, 2], p[:, 3]])
    q = np.percentile(rn, [5, 25, 50, 75, 90, 95, 99])
    qs = np.percentile(p[:, 4], [5, 25, 50, 75, 90, 95, 99])
    rows.append({"variant": lab, "ratio": "d(A,B) / d(A, nearest other painting)", **{f"p{k}": v for k, v in zip([5, 25, 50, 75, 90, 95, 99], q)}, "max": rn.max(), "share >= 1": (rn >= 1).mean()})
    rows.append({"variant": lab, "ratio": "d(A,B) / median pilot NN distance", **{f"p{k}": v for k, v in zip([5, 25, 50, 75, 90, 95, 99], qs)}, "max": p[:, 4].max(), "share >= 1": (p[:, 4] >= 1).mean()})
md(pd.DataFrame(rows), "H2. Distribution of the margins, clean primary pairs (214)")

# ---------------------------------------------------------------- 2. colour
c = RES["colour"]
base = c[(c.treat == "euc") & (c.store != "colour__cross")]
for m, t in (("clean_r1", "R@1 (clean)"), ("clean_r10", "R@10 (clean)"), ("clean_rnn_med", "median d(A,B)/d(A, nearest other) (clean)"), ("clean_rstep_lt1", "share of pairs under one step (clean)"),
             ("clean_ov10", "top-10 overlap (clean)"), ("prim_r1", "R@1 (all primary)"), ("pr", "participation ratio on pilot"), ("twonn", "TwoNN intrinsic dimension on pilot"),
             ("auc_colver_vs_repro", "AUC: colour-different versions further apart than clean repro pairs"), ("ver_yes_step", "median version-pair distance in steps")):
    t2 = base.pivot(index="part", columns="store", values=m).reset_index()
    t2.columns = [x.replace("colour__", "") for x in t2.columns]
    md(t2, f"C. Colour, raw Euclidean, normalisation x part: {t}")
tr = c.groupby("treat")[["clean_r1", "clean_r10", "clean_rnn_med", "clean_rstep_lt1", "clean_ov10", "clean_rbo", "twonn", "auc_colver_vs_repro"]].mean().reset_index()
tr.insert(1, "n variants", c.groupby("treat").size().values)
md(tr, "C. Colour: mean over all colour features, by treatment")
sel = c[c.part.isin(["palette_hist", "palette_sw", "hist+sw", "ALL5"]) & c.store.isin(["colour__std", "colour__rank", "colour__raw"])]
md(sel.pivot_table(index=["store", "part"], columns="treat", values="clean_r1").reset_index(), "C. Colour: R@1 (clean) by treatment for the main parts")
md(sel.pivot_table(index=["store", "part"], columns="treat", values="clean_ov10").reset_index(), "C. Colour: top-10 overlap (clean) by treatment for the main parts")
hs = c[c.treat.isin(["tv_l1", "plain_euc", "hist_hellinger", "hist_emd", "summary5", "hist_circ_emd", "sinkhorn_emd"]) | ((c.treat == "euc") & c.part.isin(["palette_hist", "palette_sw", "palette_kmeans", "lightness", "chroma", "hue"]))]
hs = hs[hs.store.isin(["colour__raw", "colour__std"])]
md(hs[["store", "part", "treat", "clean_r1", "clean_r10", "clean_rnn_med", "clean_ov10", "twonn", "auc_colver_vs_repro"]].sort_values(["store", "part", "treat"]),
   "C. Histogram distances (raw and std normalisation)", "euc on a stored part is Hellinger for the square-rooted histograms; tv_l1 and plain_euc undo the square root; hist_emd is 1-D Wasserstein on the 16 bins; hist_circ_emd is circular; sinkhorn_emd is the entropic approximation of the palette EMD; palette_sw is itself a sliced-Wasserstein embedding.")
x = c[c.store == "colour__cross"]
md(x[x.treat.isin(["euc", "pca64w"])][["part", "treat", "dim", "clean_r1", "clean_r10", "clean_rnn_med", "clean_ov10", "twonn", "auc_colver_vs_repro"]], "C. Cross-normalisation combinations")
top = c.sort_values("clean_r1", ascending=False).head(12)
md(top[["store", "part", "treat", "dim", "clean_r1", "clean_r10", "clean_rank_med", "clean_rnn_med", "clean_rnn_p90", "clean_rstep_lt1", "clean_ov10", "clean_rbo", "twonn", "auc_colver_vs_repro"]], "C. The twelve most photograph-proof colour variants (by clean R@1, of 596)")

# ---------------------------------------------------------------- 3. composition
k = RES["composition"]
main = k[k.treat.isin(["euc", "zs", "cen", "pca64w", "pca128w"])]
for m, t in (("clean_r1", "R@1 (clean)"), ("clean_ov10", "top-10 overlap (clean)"), ("clean_rnn_med", "median d(A,B)/d(A, nearest other) (clean)"), ("prim_r1", "R@1 (all primary)"), ("auc_ver_vs_repro", "AUC versions vs repro"), ("ver_yes_step", "median version-pair distance, in steps")):
    md(main.pivot(index="part", columns="treat", values=m).reset_index(), f"K. Composition, part x treatment: {t}")
md(k[k.treat == "euc"][["part", "dim", "pr", "twonn", "rel_contrast", "clean_r1", "clean_r5", "clean_r10", "clean_rank_med", "clean_rnn_med", "clean_rnn_p90", "clean_rstep_lt1", "clean_jacc", "clean_rbo", "clean_ov10"]], "K. Composition, raw Euclidean, every part")

# ---------------------------------------------------------------- 4. learned
l = RES["learned"]
l["model"] = l.store.str.split("__").str[0]
l["view"] = l.store.str.split("__").str[1]
for t in ("cos", "cen", "pca64w"):
    for m, ti in (("clean_r1", "R@1 (clean)"), ("prim_r1", "R@1 (all primary)"), ("clean_rnn_p90", "p90 of d(A,B)/d(A, nearest other) (clean)"), ("clean_rstep_lt1", "share under one step (clean)"), ("clean_ov10", "top-10 overlap (clean)")):
        md(l[l.treat == t].pivot(index=["model", "part"], columns="view", values=m).reset_index(), f"L. Learned, treatment {t}: {ti}")
md(l[l.treat == "cos"].pivot(index=["model", "part"], columns="view", values="auc_ver_vs_repro").reset_index(), "L. Learned, cosine: AUC versions vs repro")
md(l[l.treat == "cos"].pivot(index=["model", "part"], columns="view", values="twonn").reset_index(), "L. Learned, cosine: TwoNN intrinsic dimension on pilot")
tr = l.groupby("treat")[["clean_r1", "prim_r1", "clean_rnn_med", "clean_rstep_lt1", "clean_ov10", "clean_rbo", "twonn"]].mean().reset_index()
md(tr, "L. Learned: mean over the 56 store x part features, by treatment")
tr = k.groupby("treat")[["clean_r1", "prim_r1", "clean_rnn_med", "clean_rstep_lt1", "clean_ov10", "clean_rbo", "twonn"]].mean().reset_index()
md(tr, "K. Composition: mean over features, by treatment")
md(l[l.model.isin(["dinov2_b"])].groupby("view")[["clean_r1", "prim_r1", "clean_rnn_med", "clean_ov10"]].mean().reset_index(), "L. DINOv2-B: mean over parts and treatments, by view")

# ---------------------------------------------------------------- 5. breakdowns of the chosen variants
groups = {"all primary": PRIM, "no flag": CLEAN}
for f in ("low_diff_maybe_same_master", "high_diff_check_frame_or_crop", "bw_reproduction"):
    groups[f"flag {f} (primary)"] = PRIM & (u.flag == f)
    groups[f"flag {f} (all rows)"] = u.flag == f
for sp in ("commons|commons2", "commons|met", "commons|nga", "commons|rijksmuseum", "commons|aic", "commons|cleveland"):
    groups[f"{sp} (primary)"] = PRIM & (u.srcpair == sp)
groups["commons vs museum (primary)"] = PRIM & ~np.isin(u.srcpair, ["commons|commons2", "commons|commons3"])
groups["commons vs museum, no flag"] = CLEAN & ~np.isin(u.srcpair, ["commons|commons2", "commons|commons3"])
groups["commons vs commons, no flag"] = CLEAN & np.isin(u.srcpair, ["commons|commons2", "commons|commons3"])
for a, b in ((1, 3), (3, 6), (6, 9), (9, 12), (12, 99)):
    groups[f"lab_diff {a}-{b} (primary)"] = PRIM & (u.lab >= a) & (u.lab < b)
rows = []
for lab, key in BEST.items():
    p = pp(*key)
    for g, m in groups.items():
        s = summarise(p, m)
        rows.append({"variant": lab.split(",")[0], "group": g, "n": s["n"], "R@1": s["r1"], "R@10": s["r10"], "p90 rank": s["rank_p90"], "d/NN med": s["rnn_med"], "d/NN p90": s["rnn_p90"], "under 1 step": s["rstep_lt1"], "overlap@10": s["ov10"]})
b = pd.DataFrame(rows)
for m in ("R@1", "overlap@10", "d/NN med"):
    t = b.pivot(index="group", columns="variant", values=m).loc[list(groups)].reset_index()
    t.insert(1, "n", [int(groups[g].sum()) for g in groups])
    md(t, f"B. Breakdown by flag, source pair and pixel difference: {m}")

# noise floor
rows = []
for lab, key in BEST.items():
    p = pp(*key)
    r = {"variant": lab}
    for g in ("no flag", "all primary", "commons vs museum, no flag", "flag high_diff_check_frame_or_crop (all rows)", "flag bw_reproduction (all rows)"):
        ov = p[groups[g], 7]
        r[f"{g}: mean share lost"] = 1 - ov.mean()
        if g in ("no flag", "all primary"):
            r[f"{g}: median lost"] = 1 - np.median(ov)
            r[f"{g}: pairs losing 5+ of 10"] = (ov <= 0.5).mean()
    rows.append(r)
md(pd.DataFrame(rows), "N. Noise floor: share of a top-10 pilot neighbour list that changes with the photograph")

# ---------------------------------------------------------------- 6. auto-crop
a = RES["autocrop"]
cg = {m: np.abs(load_part(d, "composition", "grid8_an") - load_part("repro", "composition", "grid8_an")).max(1) > 1e-6
      for m, d in (("border", "repro_autocrop_border"), ("frame", "repro_autocrop_frame"))}
out.append(f"\nImages whose features changed under auto-crop: border {int(cg['border'].sum())}, frame {int(cg['frame'].sum())} of {u.nr}.")
touched = {m: cg[m][u.pa] | cg[m][u.pb] for m in cg}
AC = [("colour", "colour__std", "hist+sw", "pca64w"), ("colour", "colour__std", "hist+sw", "euc"), ("colour", "colour__raw", "palette_hist", "euc"), ("colour", "colour__std", "palette_hist", "euc"),
      ("composition", "composition", "grid8_an", "euc"), ("composition", "composition", "grid8_an", "pca64w"), ("composition", "composition", "grid8_ap", "euc"), ("composition", "composition", "ALL", "euc"),
      ("composition", "composition", "saliency", "euc"), ("composition", "composition", "aspect", "euc"),
      ("learned", "dinov2_b__pad", "cls", "cen"), ("learned", "dinov2_b__pad", "patch_mean", "cen"), ("learned", "dinov2_b__pad", "gram_late", "cen"), ("learned", "dinov2_b__pad", "meanstd_early", "cen")]
agroups = {"all primary": PRIM, "no flag": CLEAN, "high_diff flag (primary)": PRIM & (u.flag == "high_diff_check_frame_or_crop"), "high_diff flag (all rows)": u.flag == "high_diff_check_frame_or_crop",
           "commons vs commons (primary)": PRIM & np.isin(u.srcpair, ["commons|commons2", "commons|commons3"]), "commons vs met": PRIM & (u.srcpair == "commons|met"),
           "commons vs nga": PRIM & (u.srcpair == "commons|nga"), "commons vs rijksmuseum": PRIM & (u.srcpair == "commons|rijksmuseum"),
           "commons vs aic/cleveland": PRIM & np.isin(u.srcpair, ["commons|aic", "commons|cleveland"]),
           "frame mode cropped either image (all rows)": touched["frame"], "frame mode cropped neither (all rows)": ~touched["frame"]}
rows = []
for blk, store, part, treat in AC:
    for g, m in agroups.items():
        r = {"feature": f"{store.replace('colour__', 'colour ')} {part} {treat}", "group": g, "n": int(m.sum())}
        for mode in ("none", "border", "frame"):
            name = "|".join([blk, store, part, treat, mode])
            if name not in SW["autocrop"][1]:
                continue
            s = summarise(SW["autocrop"][0][SW["autocrop"][1][name]], m)
            r[f"R@1 {mode}"] = s["r1"]
            r[f"d/NN med {mode}"] = s["rnn_med"]
            r[f"ov10 {mode}"] = s["ov10"]
        rows.append(r)
act = pd.DataFrame(rows)
order = ["feature", "group", "n"] + [f"{k} {m}" for k in ("R@1", "d/NN med", "ov10") for m in ("none", "border", "frame")]
md(act[[c_ for c_ in order if c_ in act.columns]].fillna(""), "A. Auto-crop none / border / frame", "The pilot gallery is not auto-cropped (no such store exists); both photographs of the pair and the other museums' reproductions are.")

# per-pair change, composition grid8_an Euclidean
def acd(blk, store, part, treat, mode):
    return SW["autocrop"][0][SW["autocrop"][1]["|".join([blk, store, part, treat, mode])]]


ch = {}
for nm, key in (("comp", ("composition", "composition", "grid8_an", "euc")), ("col", ("colour", "colour__std", "hist+sw", "euc")), ("dino", ("learned", "dinov2_b__pad", "cls", "cen"))):
    for mode in ("border", "frame"):
        if nm == "dino" and mode == "border":
            continue
        ch[f"{nm}_{mode}"] = np.log2(np.maximum(acd(*key, mode)[:, C["d_ab"]], 1e-9) / np.maximum(acd(*key, "none")[:, C["d_ab"]], 1e-9))
chd = pd.DataFrame(ch)
chd["qid"] = u.qid[NP + u.pa]
chd["a"] = [u.repro_ids[i] for i in u.pa]
chd["b"] = [u.repro_ids[i] for i in u.pb]
chd["flag"] = u.flag
chd["touched"] = touched["frame"]
chd["rank_none"] = np.maximum(acd("composition", "composition", "grid8_an", "euc", "none")[:, 0], acd("composition", "composition", "grid8_an", "euc", "none")[:, 1])
chd["rank_frame"] = np.maximum(acd("composition", "composition", "grid8_an", "euc", "frame")[:, 0], acd("composition", "composition", "grid8_an", "euc", "frame")[:, 1])
t = chd[chd.touched]
rows = []
for col in ch:
    v = t[col].values
    rows.append({"measure": col, "pairs with a crop": len(v), "closer by >10 %": (v < np.log2(0.9)).mean(), "within 10 %": (np.abs(v) <= np.log2(1 / 0.9)).mean(), "further by >10 %": (v > np.log2(1.1)).mean(),
                 "median log2 change": np.median(v), "p10": np.percentile(v, 10), "p90": np.percentile(v, 90)})
md(pd.DataFrame(rows), "A. Change in d(A,B) under auto-crop, pairs where frame mode cropped either image (log2 of cropped / uncropped distance)")
dd = chd[chd.touched].sort_values("comp_frame").drop_duplicates("qid")
helped, hurt = dd.head(10), dd.tail(10).iloc[::-1]
chd.to_csv(OUT / "autocrop_change.csv", index=False)
pd.concat([helped.assign(kind="helped"), hurt.assign(kind="hurt")]).to_csv(HERE / "autocrop_sheet_pairs.csv", index=False, float_format="%.3f")

# ---------------------------------------------------------------- 7. worst pairs
wrows = []
SHEETS = {}
for lab, key in BEST.items():
    if "as built" in lab or "text-trained" in lab:
        continue
    p = pp(*key)
    d = pd.DataFrame({"block": lab.split(",")[0], "qid": u.qid[NP + u.pa], "a": [u.repro_ids[i] for i in u.pa], "b": [u.repro_ids[i] for i in u.pb], "flag": u.flag, "lab_diff": u.lab,
                      "rank_ab": p[:, 0], "rank_ba": p[:, 1], "rnn": np.maximum(p[:, 2], p[:, 3]), "rstep": p[:, 4], "ov10": p[:, 7],
                      "title": [r["title"] for r in u.pairs]})
    d["worst_rank"] = d[["rank_ab", "rank_ba"]].max(axis=1)
    w = d.sort_values(["worst_rank", "rnn"], ascending=False).drop_duplicates("qid").head(15)
    wrows.append(w)
    SHEETS[lab.split(":")[0].replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")] = w
    if lab.startswith("colour:"):
        w2 = d[CLEAN].sort_values(["worst_rank", "rnn"], ascending=False).drop_duplicates("qid").head(15)
        wrows.append(w2.assign(block="colour (no-flag pairs only)"))
        SHEETS["colour_clean"] = w2
        mid = d[CLEAN & (d.worst_rank > 1).values].sample(15, random_state=0)
        wrows.append(mid.assign(block="colour (random no-flag failures)"))
        SHEETS["colour_random_fail"] = mid
pd.concat(wrows).to_csv(HERE / "worst_pairs.csv", index=False, float_format="%.3f")

(HERE / "tables.md").write_text("\n".join(out) + "\n")
print("tables.md", len(out), "lines")

if "--sheets" in sys.argv:
    from sheets import pair_sheet

    for name, w in SHEETS.items():
        items = [(r.a, r.b, [f"{r.qid} {r.title}", f"{r.a.split('__')[1]} vs {r.b.split('__')[1]}  flag={r.flag} lab={r.lab_diff:.1f}",
                             f"rank {int(r.rank_ab)}/{int(r.rank_ba)} d/NN {r.rnn:.2f} steps {r.rstep:.2f} ov {r.ov10:.1f}"]) for r in w.itertuples()]
        pair_sheet(items, OUT / f"worst_{name}.jpg")
    for name, w in (("helped", helped), ("hurt", hurt)):
        items = [(r.a, r.b, [f"{r.qid} {r.a.split('__')[1]} vs {r.b.split('__')[1]} flag={r.flag}",
                             f"log2 d change: comp frame {r.comp_frame:+.2f} border {r.comp_border:+.2f}",
                             f"colour frame {r.col_frame:+.2f}  dino frame {r.dino_frame:+.2f}  rank {int(r.rank_none)}->{int(r.rank_frame)}"]) for r in w.itertuples()]
        pair_sheet(items, OUT / f"autocrop_{name}.jpg", cols=2, with_boxes=True)
    print("sheets written")

if "--plots" in sys.argv:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6), dpi=90)
    for lab, key in BEST.items():
        if "as built" in lab or "text-trained" in lab or "alt." in lab:
            continue
        p = pp(*key)[CLEAN]
        rn = np.sort(np.concatenate([p[:, 2], p[:, 3]]))
        ax[0].plot(rn, np.linspace(0, 1, len(rn)), label=lab.split(":")[0])
        ax[1].plot(np.sort(p[:, 7]), np.linspace(0, 1, len(p)), label=lab.split(":")[0])
    ax[0].axvline(1, color="k", lw=0.6)
    ax[0].set_xlim(0, 3)
    ax[0].set_xlabel("d(A,B) / d(A, nearest different painting)")
    ax[0].set_ylabel("cumulative share of clean pairs")
    ax[1].set_xlabel("share of top-10 pilot neighbours kept across photographs")
    ax[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(HERE / "margins.png")
    fig, ax = plt.subplots(figsize=(5.4, 3.8), dpi=90)
    cc = RES["colour"]
    for norm, g in cc[cc.treat.isin(["euc", "pca64w"])].groupby("store"):
        ax.scatter(g.twonn, g.clean_r1, s=10, label=norm.replace("colour__", ""))
    ax.set_xlabel("TwoNN intrinsic dimension on pilot (discrimination)")
    ax.set_ylabel("R@1, clean pairs (invariance)")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(HERE / "colour_tradeoff.png")
    print("plots written")
