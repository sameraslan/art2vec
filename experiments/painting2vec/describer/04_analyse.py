"""All tables for the describer study. Reads raw/*.json, key.csv, sample.csv, image_stats.csv.

  uv run --no-project --with numpy --with pandas --with scipy python experiments/painting2vec/describer/04_analyse.py > experiments/painting2vec/describer/tables.md
"""
import importlib.util
import json
import re
import unicodedata

import numpy as np
import pandas as pd
from scipy import stats

HERE = "experiments/painting2vec/describer"
spec = importlib.util.spec_from_file_location("v", f"{HERE}/03_validate.py")
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
FELT, THINGS, MANNER, COUNTS = v.FELT, v.THINGS, v.MANNER, v.COUNTS
CONDS = ["orig", "retest", "mirror", "told"]

# Wikidata depicts label -> checklist category. Only labels naming a visible thing are mapped.
DEPICTS = {
    "sky": ["sky"], "clouds": ["cloud", "sea of clouds"], "sun_or_moon": ["Moon"],
    "water": ["body of water", "lake", "sea", "watercourse", "Aras River", "coastline", "shore"],
    "trees": ["tree", "broad-leaved tree", "Cupressus", "woodland", "Dracaena draco"],
    "mountains_or_hills": ["mountain", "Alpilles", "Great St Bernard Pass"],
    "rocks": ["rock", "stone", "cave"], "field_or_grass": ["grass", "lawn", "glade"],
    "flowers": ["flower", "flowering plant", "daisy", "lily", "rose", "Paeonia", "Dianthus", "Aquilegia",
                "Convallaria majalis", "Leucanthemum vulgare", "Leucojum", "Malva", "Vinca", "Erysimum"],
    "fruit_or_food": ["fruit", "bread", "cherry", "grape", "orange", "potato", "Fragaria", "picnic", "eating"],
    "snow_or_ice": ["snow", "winter"], "fire_or_smoke": ["torch", "oil lamp"],
    "window_or_door": ["door"], "furniture": ["chair", "bed", "armrest"], "bridge": ["bridge"],
    "boat_or_ship": ["ship", "raft"], "cart_or_carriage": ["carriage"], "horse": ["horse"],
    "dog": ["dog", "Spanish Mastiff", "herding dog"], "bird": ["bird", "owl", "peafowl", "Pyrrhula"],
    "other_animal": ["deer", "elephant", "giraffe", "lion", "rabbit", "snake", "unicorn", "house mouse",
                     "Mustela erminea", "Mustela putorius furo", "mule", "buffalo"],
    "man": ["man", "soldier", "monk", "physician", "jester", "beard", "chinstrap beard", "male toplessness", "herder"],
    "woman": ["woman", "naked woman", "nun", "majo / maja"],
    "child": ["child", "girl", "Christ Child", "Child Saint John"],
    "nude": ["nudity", "naked woman", "toplessness", "male toplessness", "clothed female, naked male",
             "clothed male, naked female", "pubic hair", "vulva", "buttocks", "nipple", "breast"],
    "crowd": ["crowd"], "dead_or_wounded_body": ["corpse", "blood", "major trauma"],
    "soldier_or_armour": ["soldier", "Roman soldier", "body armor", "cuirass", "Schutterij", "bodyguard"],
    "weapon": ["sword", "spear", "rifle", "arrow"], "book_or_paper": ["paper", "scroll", "Bible"],
    "musical_instrument": ["lute", "violin", "psaltery"], "curtain_or_drapery": ["drapery"],
    "hat_or_headdress": ["hat", "headgear", "straw hat", "top hat", "boater", "headband"],
    "jewellery_or_crown": ["earring", "pearl", "necklace", "bracelet", "pendant", "choker", "crown", "armband"],
    "halo": ["aureola"], "wings": ["angel"], "cross": ["crucifixion"], "skull_or_skeleton": ["human skeleton", "bone"],
}
# names that are knowledge about the picture, not things in it (searched in main_action and tags)
NAMES = ("christ jesus virgin madonna mary magdalene saint st god venus zephyr socrates napoleon bonaparte newton "
         "durga jacob oedipus seneca zenobia liberty marianne medusa martha infanta apostle resurrection "
         "crucifixion lamentation martyr trinity shah emperor king queen akbar hemu yoritomo samurai shogun "
         "mahisha baptist joseph adam eve paradise eden hell heaven").split()


def norm(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()


def icc_a1(x, y):
    """ICC(A,1): two-way random, absolute agreement, single rating."""
    d = np.column_stack([x, y]).astype(float); n, k = d.shape
    gm = d.mean(); msr = k * ((d.mean(1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((d.mean(0) - gm) ** 2).sum() / (k - 1)
    mse = ((d - d.mean(1, keepdims=True) - d.mean(0, keepdims=True) + gm) ** 2).sum() / ((n - 1) * (k - 1))
    den = msr + (k - 1) * mse + k * (msc - mse) / n
    return np.nan if den <= 0 else (msr - mse) / den


def kappa(x, y, weighted=False, levels=None):
    x, y = np.asarray(x), np.asarray(y)
    levels = sorted(set(x) | set(y)) if levels is None else levels
    ix = {l: i for i, l in enumerate(levels)}; n = len(levels)
    if n < 2:
        return np.nan
    o = np.zeros((n, n))
    for a, b in zip(x, y):
        o[ix[a], ix[b]] += 1
    o /= o.sum(); e = np.outer(o.sum(1), o.sum(0))
    w = np.array([[((i - j) / (n - 1)) ** 2 if weighted else float(i != j) for j in range(n)] for i in range(n)])
    return np.nan if (w * e).sum() == 0 else 1 - (w * o).sum() / (w * e).sum()


def spear(x, y):
    return np.nan if np.std(x) == 0 or np.std(y) == 0 else stats.spearmanr(x, y)[0]


def md(df, fmt="{:.2f}"):
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind == "f":
            df[c] = df[c].map(lambda z: "" if pd.isna(z) else fmt.format(z))
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(z) for z in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out) + "\n"


def load():
    key = pd.read_csv(f"{HERE}/key.csv").set_index("code")
    rows = []
    for b in range(20):
        for r in json.load(open(f"{HERE}/raw/batch_{b:02d}.json"))["records"]:
            k = key.loc[r["code"]]
            row = {"qid": k.qid, "cond": k.condition, "batch": b, "code": r["code"]}
            row.update({f"f_{w}": r["felt"][w] for w in FELT})
            row.update({f"m_{w}": r["manner"][w] for w in MANNER})
            row.update({f"t_{w}": r["subject"]["things"][w] for w in THINGS})
            s, g = r["subject"], r["recognition"]
            row.update(people=COUNTS.index(s["people"]), animals=COUNTS.index(s["animals"]), setting=s["setting"],
                       action=s["main_action"], tags="|".join(s["tags"]), rec=g["recognised"], rec_title=g["title"],
                       rec_painter=g["painter"], conf=g["confidence"], school=g["guess_school"], century=g["guess_century"])
            rows.append(row)
    return pd.DataFrame(rows)


def pair_table(W, cols, a, b, binary=False):
    """Per-item agreement between two conditions; W[cond] is a qid-indexed frame."""
    out = []
    for c in cols:
        x, y = W[a][c].to_numpy(), W[b][c].to_numpy()
        r = {"item": c[2:], "mean": np.r_[x, y].mean()}
        if binary:
            r.update(n_pos=int(max(x.sum(), y.sum())), agree=(x == y).mean(), kappa=kappa(x, y, levels=[0, 1]))
        else:
            r.update(icc=icc_a1(x, y), spearman=spear(x, y), w_kappa=kappa(x, y, True, list(range(int(max(x.max(), y.max())) + 1))),
                     exact=(x == y).mean(), mad=np.abs(x - y).mean())
        out.append(r)
    return pd.DataFrame(out)


def profile(W, cols, a, b):
    """Per-painting agreement of the whole section: r of the two profiles, mean abs diff, and
    whether b's record of the same painting is the nearest of the 60 to a's record (L1)."""
    A, B = W[a][cols].to_numpy(float), W[b][cols].to_numpy(float)
    r = np.array([np.corrcoef(A[i], B[i])[0, 1] if A[i].std() and B[i].std() else np.nan for i in range(len(A))])
    D = np.abs(A[:, None, :] - B[None, :, :]).mean(-1)
    same = np.diag(D); other = (D.sum(1) - same) / (len(A) - 1)
    top1 = (D.argmin(1) == np.arange(len(A))).mean()
    Az, Bz = A - A.mean(0), B - B.mean(0)  # centred on the item means: removes the profile every painting shares
    rz = np.array([np.corrcoef(Az[i], Bz[i])[0, 1] for i in range(len(A))])
    return {"pair": f"{a} vs {b}", "profile_r": np.nanmean(r), "centred_r": np.nanmean(rz), "mad_same": same.mean(),
            "mad_other_painting": other.mean(), "top1_match": top1}


def loo_r2(X, y, ridge=1.0):
    X = (X - X.mean(0)) / (X.std(0) + 1e-9); n = len(y); pred = np.zeros(n)
    for i in range(n):
        m = np.arange(n) != i
        Xi = np.column_stack([np.ones(m.sum()), X[m]]); P = np.eye(Xi.shape[1]) * ridge; P[0, 0] = 0
        beta = np.linalg.solve(Xi.T @ Xi + P, Xi.T @ y[m]); pred[i] = np.r_[1, X[i]] @ beta
    ss = ((y - y.mean()) ** 2).sum()
    return np.nan if ss == 0 else 1 - ((y - pred) ** 2).sum() / ss


def main():
    d = load()
    s = pd.read_csv(f"{HERE}/sample.csv").set_index("qid")
    st = pd.read_csv(f"{HERE}/image_stats.csv").set_index("qid")
    s["group"] = np.where(s.fame != "obscure", s.fame, np.where(s.stratum == "sitelink_rank", "obscure_european_floor", "obscure_non_european"))
    qids = list(s.index)
    W = {c: d[d.cond == c].set_index("qid").loc[qids] for c in CONDS}
    F, M, T = [f"f_{w}" for w in FELT], [f"m_{w}" for w in MANNER], [f"t_{w}" for w in THINGS]
    d.drop(columns=["code"]).to_csv(f"{HERE}/records_long.csv", index=False)
    print(f"records: {len(d)} of 240; batches valid: 20 of 20\n")

    # ---------- 1. test-retest
    print("## T1. Test-retest, felt words (orig vs retest, two different describers, n = 60)\n")
    t = pair_table(W, F, "orig", "retest"); print(md(t))
    print(f"median ICC {t.icc.median():.2f}, mean {t.icc.mean():.2f}, range {t.icc.min():.2f} to {t.icc.max():.2f}; "
          f"mean exact agreement {t.exact.mean():.2f}; mean absolute difference {t['mad'].mean():.2f} scale points\n")
    felt_tr = t.set_index("item")
    print("## T2. Test-retest, manner, colour and composition scales (0-4)\n")
    t = pair_table(W, M, "orig", "retest"); print(md(t))
    print(f"median ICC {t.icc.median():.2f}, mean {t.icc.mean():.2f}; mean exact agreement {t.exact.mean():.2f}; mean absolute difference {t['mad'].mean():.2f}\n")
    print("## T3. Test-retest, subject checklist (Cohen's kappa per item)\n")
    t = pair_table(W, T, "orig", "retest", binary=True); print(md(t))
    x, y = W["orig"][T].to_numpy().ravel(), W["retest"][T].to_numpy().ravel()
    jac = lambda a, b: [(p & q).sum() / max((p | q).sum(), 1) for p, q in zip(W[a][T].to_numpy().astype(bool), W[b][T].to_numpy().astype(bool))]
    print(f"pooled over all 60 x 46 cells: agreement {(x == y).mean():.3f}, kappa {kappa(x, y, levels=[0, 1]):.2f}; "
          f"per-painting Jaccard of the marked sets: mean {np.mean(jac('orig', 'retest')):.2f}, median {np.median(jac('orig', 'retest')):.2f}; "
          f"items with kappa >= 0.8: {(t.kappa >= 0.8).sum()} of {int(t.kappa.notna().sum())} that have any positive; mean marks per painting {W['orig'][T].sum(axis=1).mean():.1f}\n")
    rows = []
    for a, b in [("orig", "retest"), ("orig", "mirror"), ("orig", "told")]:
        tagj = [len(set(p.split("|")) & set(q.split("|"))) / max(len(set(p.split("|")) | set(q.split("|"))), 1) for p, q in zip(W[a].tags, W[b].tags)]
        rows.append({"pair": f"{a} vs {b}", "people_exact": (W[a].people.values == W[b].people.values).mean(),
                     "people_w_kappa": kappa(W[a].people, W[b].people, True, list(range(5))),
                     "animals_exact": (W[a].animals.values == W[b].animals.values).mean(),
                     "animals_w_kappa": kappa(W[a].animals, W[b].animals, True, list(range(5))),
                     "setting_exact": (W[a].setting.values == W[b].setting.values).mean(), "setting_kappa": kappa(W[a].setting, W[b].setting),
                     "checklist_kappa": kappa(W[a][T].to_numpy().ravel(), W[b][T].to_numpy().ravel(), levels=[0, 1]),
                     "checklist_jaccard": np.mean(jac(a, b)), "free_tag_jaccard": np.mean(tagj)})
    print("## T4. Subject fields by pair of presentations\n"); print(md(pd.DataFrame(rows)))

    # ---------- 2. whole-section agreement by pair
    print("## T5. Whole-section agreement per painting, by pair of presentations\n")
    for name, cols in [("felt (24 words, 0-3)", F), ("manner (13 scales, 0-4)", M), ("checklist (46 items, 0/1)", T)]:
        rows = [profile(W, cols, a, b) for a, b in [("orig", "retest"), ("orig", "mirror"), ("retest", "mirror"), ("orig", "told"), ("retest", "told")]]
        print(f"{name}\n"); print(md(pd.DataFrame(rows), "{:.3f}"))

    # ---------- 3. condition shifts per felt word
    print("## T6. Signed shift per felt word against the mean of the two plain presentations (n = 60)\n")
    base = (W["orig"][F].to_numpy(float) + W["retest"][F].to_numpy(float)) / 2
    rows = []
    for j, w in enumerate(FELT):
        r = {"word": w, "noise_mad": felt_tr.loc[w, "mad"], "retest_minus_orig": (W["retest"][F[j]] - W["orig"][F[j]]).mean()}
        for c in ["mirror", "told"]:
            diff = W[c][F[j]].to_numpy(float) - base[:, j]
            r[f"{c}_shift"] = diff.mean()
            r[f"{c}_p"] = stats.wilcoxon(diff)[1] if np.any(diff != 0) else 1.0
            r[f"{c}_mad_vs_orig"] = np.abs(W[c][F[j]].to_numpy() - W["orig"][F[j]].to_numpy()).mean()
        rows.append(r)
    t = pd.DataFrame(rows); print(md(t))
    print(f"mean over words of |shift|: mirror {t.mirror_shift.abs().mean():.3f}, told {t.told_shift.abs().mean():.3f}, retest minus orig {t.retest_minus_orig.abs().mean():.3f}; "
          f"words with p < 0.05 (uncorrected, 24 tests each): mirror {(t.mirror_p < .05).sum()}, told {(t.told_p < .05).sum()}; with p < 0.05/24: mirror {(t.mirror_p < .05 / 24).sum()}, told {(t.told_p < .05 / 24).sum()}; "
          f"mean absolute difference from orig: retest {t.noise_mad.mean():.3f}, mirror {t.mirror_mad_vs_orig.mean():.3f}, told {t.told_mad_vs_orig.mean():.3f}\n")
    print("Same for the manner scales\n")
    baseM = (W["orig"][M].to_numpy(float) + W["retest"][M].to_numpy(float)) / 2
    rows = []
    for j, w in enumerate(MANNER):
        r = {"scale": w, "retest_minus_orig": (W["retest"][M[j]] - W["orig"][M[j]]).mean()}
        for c in ["mirror", "told"]:
            diff = W[c][M[j]].to_numpy(float) - baseM[:, j]; r[f"{c}_shift"] = diff.mean(); r[f"{c}_p"] = stats.wilcoxon(diff)[1] if np.any(diff != 0) else 1.0
        rows.append(r)
    print(md(pd.DataFrame(rows)))

    # ---------- 4. recognition
    print("## T7. Recognition by fame group (untold presentations)\n")
    truth = s.creator_name.fillna("").map(norm)
    def correct(r):
        toks = [t for t in re.split(r"[^a-z]+", norm(r.rec_painter)) if len(t) > 3 and t not in ("attributed", "workshop", "master")]
        return bool(r.rec) and any(t in truth[r.qid] for t in toks)
    d["rec_correct"] = d.apply(correct, axis=1)
    d["group"] = d.qid.map(s.group); d["fame"] = d.qid.map(s.fame)
    d["cent_err"] = (d.century - ((d.qid.map(s.inception_year) - 1) // 100 + 1)).abs()
    rows = []
    for g in ["famous", "mid", "obscure_european_floor", "obscure_non_european"]:
        r = {"group": g, "paintings": int((s.group == g).sum())}
        for c in ["orig", "retest", "mirror"]:
            x = d[(d.group == g) & (d.cond == c)]
            r[f"{c}_recognised"] = f"{int(x.rec.sum())}/{len(x)}"; r[f"{c}_right_painter"] = f"{int(x.rec_correct.sum())}/{len(x)}"; r[f"{c}_conf"] = x.conf.mean()
        x = d[(d.group == g) & (d.cond != "told")]
        r["century_exact"] = (x.cent_err == 0).mean(); r["century_within_1"] = (x.cent_err <= 1).mean()
        rows.append(r)
    print(md(pd.DataFrame(rows)))
    u = d[d.cond != "told"]
    print(f"claimed recognitions with the wrong painter (untold): {int((u.rec & ~u.rec_correct).sum())} of {int(u.rec.sum())}\n")
    nrec = u.groupby("qid").rec.sum().reindex(s.index)
    s["n_rec"] = nrec; s["recog"] = np.where(nrec == 3, "recognised 3/3", np.where(nrec == 0, "never recognised", "mixed"))
    print("recognition across the three untold presentations: " + ", ".join(f"{k}: {n}" for k, n in s.recog.value_counts().items()) + "\n")

    # ---------- 5. name effect by recognition
    print("## T8. Effect of telling the name, split by whether the painting was recognised unaided\n")
    def l1(a, b, cols): return np.abs(W[a][cols].to_numpy(float) - W[b][cols].to_numpy(float)).mean(1)
    rows = []
    for g in ["recognised 3/3", "never recognised", "mixed"]:
        m = (s.recog == g).to_numpy()
        if m.sum() == 0: continue
        r = {"paintings": g, "n": int(m.sum())}
        for nm, cols in [("felt", F), ("manner", M), ("checklist", T)]:
            noise = l1("orig", "retest", cols)[m]; told = (l1("orig", "told", cols)[m] + l1("retest", "told", cols)[m]) / 2
            mir = (l1("orig", "mirror", cols)[m] + l1("retest", "mirror", cols)[m]) / 2
            r[f"{nm}_noise"] = noise.mean(); r[f"{nm}_told"] = told.mean(); r[f"{nm}_mirror"] = mir.mean()
            r[f"{nm}_told_p"] = stats.wilcoxon(told - noise)[1] if m.sum() > 5 and np.any(told != noise) else np.nan
        rows.append(r)
    print(md(pd.DataFrame(rows), "{:.3f}"))
    print("Values are mean absolute differences per item between two presentations of one painting. noise = orig vs retest; told = told vs each plain presentation, averaged; mirror likewise. p: Wilcoxon signed-rank, told against noise.\n")
    nr = (s.recog == "never recognised").to_numpy()
    rows = []
    for j, w in enumerate(FELT):
        dn = W["told"][F[j]].to_numpy(float) - base[:, j]
        rows.append({"word": w, "never_recognised_shift": dn[nr].mean(), "recognised_shift": dn[(s.recog == "recognised 3/3").to_numpy()].mean()})
    t = pd.DataFrame(rows); t = t.reindex(t.never_recognised_shift.abs().sort_values(ascending=False).index).head(8)
    print("Largest told-minus-plain shifts among never-recognised paintings\n"); print(md(t))

    print("## T9. Mean felt profile, recognised against never recognised (plain presentations)\n")
    rc = (s.recog == "recognised 3/3").to_numpy()
    eur = (s.group == "obscure_european_floor").to_numpy()
    rows = []
    for j, w in enumerate(FELT):
        rows.append({"word": w, "recognised": base[rc, j].mean(), "never_recognised": base[nr, j].mean(),
                     "diff": base[rc, j].mean() - base[nr, j].mean(), "p_mannwhitney": stats.mannwhitneyu(base[rc, j], base[nr, j])[1]})
    print(md(pd.DataFrame(rows)))
    print(f"total felt marks per painting (sum of 24 ratings): recognised {base[rc].sum(1).mean():.1f}, never recognised {base[nr].sum(1).mean():.1f}; "
          f"count of non-zero words: recognised {(base[rc] > 0).sum(1).mean():.1f}, never recognised {(base[nr] > 0).sum(1).mean():.1f}. "
          f"By fame: famous {base[(s.fame == 'famous').to_numpy()].sum(1).mean():.1f}, mid {base[(s.fame == 'mid').to_numpy()].sum(1).mean():.1f}, "
          f"obscure European floor {base[eur].sum(1).mean():.1f}, obscure non-European {base[(s.group == 'obscure_non_european').to_numpy()].sum(1).mean():.1f}\n")

    # ---------- 6. names in the subject section
    print("## T10. Names in the subject free text (main_action and tags)\n")
    pat = re.compile(r"\b(" + "|".join(NAMES) + r")\b")
    d["named"] = (d.action + " " + d.tags.str.replace("|", " ")).map(lambda z: bool(pat.search(norm(z))))
    d["hits"] = (d.action + " " + d.tags.str.replace("|", " ")).map(lambda z: ",".join(sorted(set(pat.findall(norm(z))))))
    print(md(d.groupby("cond").agg(records=("named", "size"), with_a_name=("named", "sum")).reindex(CONDS).reset_index()))
    print("names found: " + "; ".join(f"{c}: {', '.join(sorted(set(','.join(d[(d.cond == c) & d.named].hits).split(','))))}" for c in CONDS) + "\n")

    # ---------- 7. redundancy
    print("## T11. Are felt marks predictable from colour and manner? Leave-one-out R2, target = felt mark from the orig describer (n = 60)\n")
    COL = ["m_darkness", "m_palette_breadth", "m_saturation", "m_colour_temperature", "m_contrast"]
    Xs = st.loc[qids].to_numpy(float); Xc = W["retest"][COL].to_numpy(float); Xm = W["retest"][M].to_numpy(float)
    Xsame = W["orig"][M].to_numpy(float); Xt = np.column_stack([W["retest"][T].to_numpy(float), W["retest"][["people", "animals"]].to_numpy(float)])
    rows = []
    for j, w in enumerate(FELT):
        y = W["orig"][F[j]].to_numpy(float)
        rows.append({"word": w, "sd": y.std(), "measured_colour": loo_r2(Xs, y), "colour_marks_other_describer": loo_r2(Xc, y),
                     "all_manner_other_describer": loo_r2(Xm, y, 3.0), "all_manner_same_describer": loo_r2(Xsame, y, 3.0),
                     "subject_marks_other_describer": loo_r2(Xt, y, 10.0),
                     "manner_plus_subject_other": loo_r2(np.column_stack([Xm, Xt]), y, 10.0),
                     "same_word_other_describer": loo_r2(W["retest"][[F[j]]].to_numpy(float), y, 0.0)})
    t = pd.DataFrame(rows); print(md(t))
    print("mean over words: " + ", ".join(f"{c} {t[c].mean():.2f}" for c in t.columns[2:]) + "\n")
    print("Describer colour marks against measured image statistics (Spearman, orig describer, n = 60): "
          f"darkness vs mean luma {spear(W['orig'].m_darkness, st.loc[qids].luma_mean):.2f}; saturation vs mean saturation {spear(W['orig'].m_saturation, st.loc[qids].sat_mean):.2f}; "
          f"colour_temperature vs red minus blue {spear(W['orig'].m_colour_temperature, st.loc[qids].warm_minus_cool):.2f}; palette_breadth vs hue spread {spear(W['orig'].m_palette_breadth, st.loc[qids].hue_spread):.2f}; "
          f"contrast vs luma sd {spear(W['orig'].m_contrast, st.loc[qids].luma_std):.2f}\n")

    print("## T11b. Strongest single correlate of each felt word among another describer's subject and manner marks (Spearman, n = 60)\n")
    feats = pd.concat([W["retest"][T + M + ["people", "animals"]]], axis=1)
    feats = feats.loc[:, feats.std() > 0]
    rows = []
    for j, w in enumerate(FELT):
        y = W["orig"][F[j]].to_numpy(float)
        rs = pd.Series({c: stats.spearmanr(feats[c], y)[0] for c in feats.columns}).dropna()
        o = rs.abs().sort_values(ascending=False).index[:3]
        rows.append({"word": w, "first": f"{o[0].split('_', 1)[1] if o[0][1] == '_' else o[0]} {rs[o[0]]:+.2f}",
                     "second": f"{o[1].split('_', 1)[1] if o[1][1] == '_' else o[1]} {rs[o[1]]:+.2f}",
                     "third": f"{o[2].split('_', 1)[1] if o[2][1] == '_' else o[2]} {rs[o[2]]:+.2f}",
                     "darkness": rs["m_darkness"], "saturation": rs["m_saturation"], "colour_temperature": rs["m_colour_temperature"],
                     "measured_luma": stats.spearmanr(st.loc[qids].luma_mean, y)[0]})
    print(md(pd.DataFrame(rows)))

    # ---------- 8. checklist vs Wikidata depicts
    print("## T12. Subject checklist against Wikidata depicts (P180)\n")
    has = s.depicts.notna(); labels = {q: set(str(x).split("|")) for q, x in s.depicts[has].items()}
    alll = [l for q in labels for l in labels[q]]; mapped = {l for ls in DEPICTS.values() for l in ls}
    print(f"paintings with any depicts statement: {int(has.sum())} of 60 (famous {int(has[s.fame == 'famous'].sum())}/20, mid {int(has[s.fame == 'mid'].sum())}/20, obscure {int(has[s.fame == 'obscure'].sum())}/20); "
          f"statements: {len(alll)}, median per painting {np.median([len(x) for x in labels.values()]):.0f}; distinct labels {len(set(alll))}, of which mapped to a checklist category {len(set(alll) & mapped)}; "
          f"statements that map {sum(l in mapped for l in alll)} ({sum(l in mapped for l in alll) / len(alll):.0%})\n")
    cons = ((W["orig"][T].to_numpy() + W["retest"][T].to_numpy() + W["mirror"][T].to_numpy()) >= 2).astype(int)
    cons = pd.DataFrame(cons, index=qids, columns=T)
    rows, dis = [], []
    for cat, ls in DEPICTS.items():
        ref = np.array([bool(labels[q] & set(ls)) for q in labels]); qs = list(labels)
        one = W["orig"].loc[qs, f"t_{cat}"].to_numpy().astype(bool); maj = cons.loc[qs, f"t_{cat}"].to_numpy().astype(bool)
        rows.append({"category": cat, "depicts_yes": int(ref.sum()), "describer_yes": int(maj.sum()), "both": int((ref & maj).sum()),
                     "depicts_only": int((ref & ~maj).sum()), "describer_only": int((~ref & maj).sum()), "single_describer_both": int((ref & one).sum())})
        for q, r_, m_ in zip(qs, ref, maj):
            if r_ != m_:
                dis.append({"qid": q, "title": s.title[q], "category": cat, "who_says_yes": "depicts" if r_ else "describer",
                            "depicts_labels": "|".join(sorted(labels[q] & set(ls)))})
    t = pd.DataFrame(rows); print(md(t))
    tp, fn, fp = t.both.sum(), t.depicts_only.sum(), t.describer_only.sum()
    print(f"majority of three untold describers against depicts, over {len(t)} mapped categories x {len(labels)} paintings: recall of depicts {tp}/{tp + fn} = {tp / (tp + fn):.2f}; "
          f"share of describer marks that depicts confirms {tp}/{tp + fp} = {tp / (tp + fp):.2f}; single describer recall {t.single_describer_both.sum()}/{tp + fn} = {t.single_describer_both.sum() / (tp + fn):.2f}\n")
    pd.DataFrame(dis).to_csv(f"{HERE}/depicts_disagreements.csv", index=False)
    s[["fame", "group", "title", "creator_name", "n_rec", "recog"]].to_csv(f"{HERE}/recognition_by_painting.csv")


if __name__ == "__main__":
    main()
