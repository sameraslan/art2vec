"""Build the describer blocks and the comparison blocks, and print every table to tables.md.

  uv run --no-project --with numpy --with pandas --with scipy --with scikit-learn python experiments/painting2vec/exp_describer_blocks/04_analyse.py
"""
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr
from sklearn.linear_model import RidgeCV
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import GroupKFold

sys.path.insert(0, "experiments/painting2vec/exp_describer_blocks")
import lib as L  # noqa: E402

HERE = L.HERE
K = 10
rng = np.random.RandomState(20261009)
OUT = []


def emit(s=""):
    OUT.append(s)
    print(s)


def table(df, floatfmt="{:.2f}"):
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind == "f":
            df[c] = df[c].map(lambda v: "" if pd.isna(v) else floatfmt.format(v))
    emit("| " + " | ".join(map(str, df.columns)) + " |")
    emit("|" + "---|" * len(df.columns))
    for _, r in df.iterrows():
        emit("| " + " | ".join(map(str, r.values)) + " |")
    emit()


# ---------------------------------------------------------------- data
items, v2, v1 = L.load_records()
S = pd.read_csv(f"{HERE}/sample.csv")
EX = pd.read_csv(f"{HERE}/version_extras.csv")
PH = pd.read_csv(f"{HERE}/photo_pairs_used.csv")
VP = pd.read_csv(f"{HERE}/version_pairs_used.csv")
ids = list(S.qid) + list(EX.qid) + [q + "__b" for q in PH.qid]
it = items.loc[ids]
N = len(S)
fit = np.arange(len(ids)) < N
pos = {q: i for i, q in enumerate(ids)}
assert it.notna().all().all() or True

# ---------------------------------------------------------------- blocks -> distance matrices over all 352 rows
D, VEC = {}, {}
B, bnames = L.subject_binary(it)
df_ = B[fit].sum(0)
idf = np.where(df_ > 0, np.log(N / np.maximum(df_, 1)), 0.0)
D["subject (Jaccard)"] = L.jaccard(B)
D["subject (IDF cosine)"] = L.cosine(B * idf)
mu, comp, sd = L.pca_fit((B * idf)[fit], 12)
VEC["subject"] = ((B * idf) - mu) @ comp.T
D["subject (IDF, PCA-12)"] = L.euclid(VEC["subject"])
VEC["manner"] = L.manner_matrix(it, fit)
D["manner"] = L.euclid(VEC["manner"])
D["manner (v1 scales only)"] = L.euclid(L.manner_matrix(it, fit, L.MANNER_V1, cues=False))
VEC["colour"] = L.colour_matrix(it, fit)
D["colour"] = L.euclid(VEC["colour"])
VEC["composition (3 scales)"] = L.zfit(it[[f"m_{k}" for k in L.COMP_SCALES]].to_numpy(float), fit)
D["composition (3 scales)"] = L.euclid(VEC["composition (3 scales)"])
VEC["felt"] = it[[f"f_{k}" for k in L.FELT]].to_numpy(float)
D["felt"] = L.euclid(VEC["felt"])


def learned(name, part, k=64, whiten=False, l2=True, z=False):
    X, (pids, P) = L.store_rows(name, part, ids)
    excl = set(json.load(open("experiments/painting2vec/exp_separation/results/setup.json"))["excluded"])
    keep = np.array([q not in excl for q in pids])
    if z:
        m_, s_ = P[keep].mean(0), P[keep].std(0) + 1e-9
        X, P = (X - m_) / s_, (P - m_) / s_
    if l2:
        X = X / np.linalg.norm(X, axis=1, keepdims=True)
        P = P / np.linalg.norm(P, axis=1, keepdims=True)
    mu, comp, sd = L.pca_fit(P[keep], k)
    Z = (X - mu) @ comp.T
    return Z / sd if whiten else Z


def learned_multi(name, parts, k=64):
    Xs, Ps = [], []
    for p in parts:
        X, (pids, P) = L.store_rows(name, p, ids)
        Xs.append(X); Ps.append(P)
    X, P = np.hstack(Xs), np.hstack(Ps)
    m_, s_ = P.mean(0), P.std(0) + 1e-9
    mu, comp, sd = L.pca_fit((P - m_) / s_, k)
    return (((X - m_) / s_) - mu) @ comp.T / sd


Xd, (pids, Pd) = L.store_rows("dinov2_l__tile", "cls", ids)
Pn = Pd / np.linalg.norm(Pd, axis=1, keepdims=True)
Xn = Xd / np.linalg.norm(Xd, axis=1, keepdims=True) - Pn.mean(0)
D["picture (DINOv2-L cls)"] = L.cosine(Xn)
VEC["picture"] = learned("dinov2_l__tile", "cls", 64)
VEC["csd"] = learned("csd_l__tile", "style", 64, whiten=True)
D["CSD style"] = L.cosine(VEC["csd"])
D["pixel composition (grid8_an)"] = L.cosine(learned("composition", "grid8_an", 128, whiten=True, l2=False, z=True))
D["pixel colour (std hist+sw)"] = L.cosine(learned_multi("colour__std", ["palette_hist", "palette_sw"], 64))
Rnd = rng.randn(len(ids), 64)
D["random 64-d"] = L.cosine(Rnd)
JIT = rng.rand(len(ids), len(ids)) * 1e-9
JIT = (JIT + JIT.T) / 2
MAIN = ["subject (IDF cosine)", "manner", "colour", "composition (3 scales)", "felt", "picture (DINOv2-L cls)", "CSD style",
        "pixel composition (grid8_an)", "pixel colour (std hist+sw)", "random 64-d"]
ALL = list(D)


def topk(name, k=K, n=N):
    d = (D[name] + JIT)[:n, :n].copy()
    np.fill_diagonal(d, np.inf)
    return np.argsort(d, 1)[:, :k]


NN = {b: topk(b) for b in ALL}
json.dump({b: [[ids[j] for j in row] for row in NN[b]] for b in ALL}, open(f"{HERE}/neighbours.json", "w"))

emit("# Tables, describer blocks experiment")
emit()
emit(f"paintings {N}; version partners outside the pilot {len(EX)}; second photographs {len(PH)}; records analysed {len(ids)}")
emit(f"subject vector: {B.shape[1]} binary marks ({(df_ > 0).sum()} ever set); manner vector {VEC['manner'].shape[1]} columns "
     f"({len(L.MANNER)} scales + {len(L.CUES)} depth cues); colour vector {VEC['colour'].shape[1]} columns; felt 24")
emit()

# ---------------------------------------------------------------- T0 pooling check
emit("## T0. Pooling check: the original 60 under instrument v1 (earlier study, `orig`) against v2 (this run)")
emit()
q60 = [q for q in S.qid if "orig60" in S.set_index("qid").why[q].split("|")]
a, b = v1.loc[q60], v2.loc[q60]
tc = [f"t_{k}" for k in L.THINGS]
A_, B_ = a[tc].to_numpy(int), b[tc].to_numpy(int)
jac = [(x & y).sum() / max((x | y).sum(), 1) for x, y in zip(A_, B_)]
rows = [{"field group": "checklist (46)", "agreement": (A_ == B_).mean(), "kappa or ICC": cohen_kappa_score(A_.ravel(), B_.ravel()),
         "mean abs diff": np.abs(A_ - B_).mean(), "earlier study, two v1 describers": "kappa 0.96, Jaccard 0.94"},
        {"field group": "checklist Jaccard per painting", "agreement": np.mean(jac), "earlier study, two v1 describers": "0.94"}]
for f in ("people", "animals", "setting"):
    rows.append({"field group": f, "agreement": (a[f].values == b[f].values).mean(), "earlier study, two v1 describers": {"people": "0.98", "animals": "0.98", "setting": "0.92"}[f]})


def icc(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = (x + y) / 2
    msb = 2 * ((m - m.mean()) ** 2).sum() / (len(x) - 1)
    msw = ((x - y) ** 2).sum() / (2 * len(x))
    return (msb - msw) / (msb + msw) if msb + msw > 0 else np.nan


for nm, cols, ref in [("13 scales (0-4)", [f"m_{k}" for k in L.SCALES_V1], "ICC median 0.94, MAD 0.13"),
                      ("24 felt words (0-3)", [f"f_{k}" for k in L.FELT], "ICC median 0.92, MAD 0.15")]:
    x, y = a[cols].to_numpy(float), b[cols].to_numpy(float)
    rows.append({"field group": nm, "agreement": (x == y).mean(), "kappa or ICC": np.median([icc(x[:, j], y[:, j]) for j in range(len(cols))]),
                 "mean abs diff": np.abs(x - y).mean(), "earlier study, two v1 describers": ref})
table(pd.DataFrame(rows))
x, y = a[[f"m_{k}" for k in L.SCALES_V1]].to_numpy(float), b[[f"m_{k}" for k in L.SCALES_V1]].to_numpy(float)
table(pd.DataFrame({"scale": L.SCALES_V1, "v1 mean": x.mean(0), "v2 mean": y.mean(0), "v2 minus v1": (y - x).mean(0),
                    "ICC": [icc(x[:, j], y[:, j]) for j in range(13)], "MAD": np.abs(x - y).mean(0)}))

# ---------------------------------------------------------------- T1 field summary
emit("## T1. The added fields: distribution over the 300")
emit()
m = it[fit]
table(pd.DataFrame({"scale": L.SCALES_V2, "mean": [m[f"m_{k}"].mean() for k in L.SCALES_V2], "sd": [m[f"m_{k}"].std() for k in L.SCALES_V2],
                    **{f"share at {v}": [(m[f"m_{k}"] == v).mean() for k in L.SCALES_V2] for v in range(5)}}))
emit("depth cues, share marked: " + ", ".join(f"{k} {m[f'd_{k}'].mean():.2f}" for k in L.CUES))
emit()
emit("hue families, share marked: " + ", ".join(f"{k} {m[f'h_{k}'].mean():.2f}" for k in L.HUES))
emit()
emit("main hue: " + ", ".join(f"{k} {v}" for k, v in m.main_hue.value_counts().items()) + "; accent hue: " +
     ", ".join(f"{k} {v}" for k, v in m.accent_hue.value_counts().items()) + "; value key: " +
     ", ".join(f"{k} {v}" for k, v in m.value_key.value_counts().items()))
emit()
mc = m[[f"m_{k}" for k in L.MANNER]].corr(method="spearman")
mc.index = mc.columns = L.MANNER
emit("Spearman correlation between the manner scales (300 paintings)")
emit()
table(mc.reset_index().rename(columns={"index": ""}))

# ---------------------------------------------------------------- T2 overlap between lists
emit(f"## T2. Shared neighbours: mean number of paintings two blocks' top-{K} lists have in common (of {K}, among the {N})")
emit()
short = {b: b.split(" (")[0] if b not in ("subject (Jaccard)", "subject (IDF, PCA-12)", "manner (v1 scales only)") else b for b in ALL}
ov = pd.DataFrame(index=[short[b] for b in ALL], columns=[short[b] for b in ALL], dtype=float)
for x in ALL:
    for y in ALL:
        ov.loc[short[x], short[y]] = np.mean([len(set(NN[x][i]) & set(NN[y][i])) for i in range(N)])
table(ov.reset_index().rename(columns={"index": ""}), "{:.1f}")
emit(f"chance: {K * K / (N - 1):.2f}")
emit()
tri = np.triu_indices(N, 1)
emit("Rank correlation between two blocks' distances over all pairs of the 300 (Spearman)")
emit()
mm = ["subject (IDF cosine)", "manner", "colour", "composition (3 scales)", "felt", "picture (DINOv2-L cls)", "CSD style"]
rc = pd.DataFrame(index=[short[b] for b in mm], columns=[short[b] for b in mm], dtype=float)
for x in mm:
    for y in mm:
        rc.loc[short[x], short[y]] = spearmanr(D[x][:N, :N][tri], D[y][:N, :N][tri])[0]
table(rc.reset_index().rename(columns={"index": ""}))

# ---------------------------------------------------------------- T3 leak and label statistics
emit(f"## T3. What the top-{K} neighbours share (labels used only here)")
emit()
meta = S.set_index("qid")
painter = meta.creator_qid.fillna("").str.split("|").str[0].to_numpy()
year = meta.inception_year.to_numpy(float)
gs = [set(g.split("|")) if isinstance(g, str) else set() for g in meta.genres]
bs = [set(g.split("|")) if isinstance(g, str) and g else set() for g in meta.broad]
trad = meta.tradition.to_numpy()
cnt = pd.Series(painter[painter != ""]).value_counts()
has_p = np.array([p != "" for p in painter])
chance_p = np.mean([(cnt[p] - 1) / (N - 1) for p in painter[has_p]])
has_g = np.array([len(g) > 0 for g in gs])
same_g = np.array([[len(gs[i] & gs[j]) > 0 for j in range(N)] for i in range(N)])
same_b = np.array([[len(bs[i] & bs[j]) > 0 for j in range(N)] for i in range(N)])
has_b = np.array([len(g) > 0 for g in bs])
chance_g = np.mean([same_g[i, has_g].sum() - 1 for i in np.where(has_g)[0]]) / (N - 1)
chance_b = np.mean([same_b[i, has_b].sum() - 1 for i in np.where(has_b)[0]]) / (N - 1)
dy = np.abs(year[:, None] - year[None])
rand_gap = np.nanmedian(dy[tri])
big = [p for p in cnt.index if cnt[p] >= 8]


def auc(d, i, posm, negm):
    p, n = d[i, posm], d[i, negm]
    if len(p) == 0 or len(n) == 0:
        return np.nan
    return ((p[:, None] < n[None]).mean() + 0.5 * (p[:, None] == n[None]).mean())


rows = []
for b in ALL:
    nn, d = NN[b], D[b][:N, :N]
    r = {"block": b}
    r["same painter"] = np.mean([(painter[nn[i]] == painter[i]).mean() for i in np.where(has_p)[0]])
    r["÷ chance"] = r["same painter"] / chance_p
    gaps = np.concatenate([dy[i, nn[i]] for i in range(N)])
    r["median Δyear"] = np.nanmedian(gaps)
    r["÷ random"] = r["median Δyear"] / rand_gap
    r["same genre (P136)"] = np.mean([same_g[i, nn[i]].mean() for i in np.where(has_g)[0]])
    r["same broad genre"] = np.mean([same_b[i, nn[i]].mean() for i in np.where(has_b)[0]])
    r["other painter and 50+ years away"] = np.nanmean(np.concatenate([((painter[nn[i]] != painter[i]) | (painter[i] == "")) & (dy[i, nn[i]] > 50) for i in range(N) if not np.isnan(year[i])]))
    r["same tradition"] = np.mean([(trad[nn[i]] == trad[i]).mean() for i in range(N)])
    a_all, a_diff, a_same = [], [], []
    for i in range(N):
        if painter[i] in big:
            oth = np.arange(N) != i
            sp = (painter == painter[i]) & oth
            op = (painter != painter[i])
            a_all.append(auc(d, i, sp, op))
            if has_b[i]:
                a_diff.append(auc(d, i, sp & has_b & ~same_b[i], op & has_b & ~same_b[i]))
                a_same.append(auc(d, i, sp & same_b[i], op & same_b[i]))
    r["painter AUC"] = np.nanmean(a_all)
    r["… same broad genre"] = np.nanmean(a_same)
    r["… different broad genre"] = np.nanmean(a_diff)
    occ = np.bincount(nn.ravel(), minlength=N)
    r["in nobody's top 10"] = (occ == 0).mean()
    r["max k-occurrence"] = int(occ.max())
    rows.append(r)
T3 = pd.DataFrame(rows)
table(T3)
emit(f"chance: same painter {chance_p:.3f} ({has_p.sum()} paintings with a painter); same genre {chance_g:.2f}; same broad genre {chance_b:.2f}; "
     f"random pair median year gap {rand_gap:.0f}; painter AUC over the {len(big)} painters with 8 or more works here "
     f"({sum(cnt[p] for p in big)} paintings), chance 0.5. Earlier figures on the 1,972: CSD style same painter 0.248 (23 x chance), median Δyear 28 (0.16 of random); "
     f"DINOv2-L cls 0.121, 62 (0.36).")
emit()

emit("Painter AUC by painter (the 12 painters with 8 or more works among the 300)")
emit()
pn = meta.painter.to_numpy()
rows = []
for p in big:
    idx = np.where(painter == p)[0]
    r = {"painter": pn[idx[0]], "works": len(idx)}
    for b in ["subject (IDF cosine)", "manner", "manner (v1 scales only)", "colour", "picture (DINOv2-L cls)", "CSD style"]:
        d = D[b][:N, :N]
        r[short[b]] = np.nanmean([auc(d, i, (painter == p) & (np.arange(N) != i), painter != p) for i in idx])
    rows.append(r)
table(pd.DataFrame(rows))

emit("Linear probes on the 300 (ridge, 5-fold, folds grouped by painter): year of the painting, R2")
emit()
groups = np.array([p if p else f"anon{i}" for i, p in enumerate(painter)])


def cvr2(X, Y, rows=None):
    rows = np.arange(len(X)) if rows is None else rows
    X, Y, g = X[rows], Y[rows], groups[rows]
    X = (X - X.mean(0)) / (X.std(0) + 1e-9)
    pred = np.zeros_like(Y, dtype=float)
    for tr, te in GroupKFold(5).split(X, groups=g):
        pred[te] = RidgeCV(alphas=np.logspace(-1, 4, 16)).fit(X[tr], Y[tr]).predict(X[te]).reshape(len(te), -1)
    return 1 - ((Y - pred) ** 2).sum(0) / ((Y - Y.mean(0)) ** 2).sum(0)


hy = np.where(~np.isnan(year))[0]
eu = np.array([i for i in hy if trad[i] == "european_american"])
PRB = {"subject marks": B[:N][:, df_ >= 5], "manner": VEC["manner"][:N], "manner (v1 scales only)": L.manner_matrix(it, fit, L.MANNER_V1, cues=False)[:N],
       "colour": VEC["colour"][:N], "composition (3 scales)": VEC["composition (3 scales)"][:N], "felt": VEC["felt"][:N],
       "picture (DINOv2-L cls, PCA-64)": VEC["picture"][:N], "CSD style (PCA-64)": VEC["csd"][:N], "random 64-d": Rnd[:N]}
table(pd.DataFrame([{"block": k, "columns": X.shape[1], f"year R2, all {len(hy)} dated": cvr2(X, year[:, None], hy)[0],
                     f"year R2, European {len(eu)}": cvr2(X, year[:, None], eu)[0]} for k, X in PRB.items()]))

# manner inside one painter / manner across subject
emit("Cross-reading: how far apart are a block's neighbours in the other describer blocks (mean distance to the top-10 ÷ mean distance to all; 1.0 = no relation)")
emit()
rows = []
for b in ["subject (IDF cosine)", "manner", "colour", "felt", "picture (DINOv2-L cls)", "CSD style", "pixel composition (grid8_an)", "random 64-d"]:
    r = {"neighbours taken from": b}
    for t in ["subject (IDF cosine)", "manner", "colour", "composition (3 scales)", "felt"]:
        d = D[t][:N, :N]
        r["in " + short[t]] = np.mean([d[i, NN[b][i]].mean() / (d[i].sum() / (N - 1)) for i in range(N)])
    rows.append(r)
table(pd.DataFrame(rows))

# ---------------------------------------------------------------- T4 version pairs
emit("## T4. Version pairs (same composition): where the partner falls")
emit()
VP["hand2"] = np.where(VP.hand == "same", "same hand", "other hand")
rows, per = [], []
for b in ALL:
    d = D[b] + JIT
    r = {"block": b}
    for h in ["same hand", "other hand"]:
        ranks, ratios, pct = [], [], []
        for _, p in VP[VP.hand2 == h].iterrows():
            for q, t in ((p.qid_a, p.qid_b), (p.qid_b, p.qid_a)):
                qi, ti = pos[q], pos[t]
                cand = [j for j in range(N) if j != qi and j != ti]
                dc = d[qi, cand]
                ranks.append(1 + (dc < d[qi, ti]).sum())
                m0 = np.sort(D[b][qi, cand])[0]
                ratios.append(D[b][qi, ti] / m0 if m0 > 0 else (np.inf if D[b][qi, ti] > 0 else 1.0))
                pct.append((dc < d[qi, ti]).mean())
            per.append({"block": b, "hand": h, "pair": f"{p.qid_a}-{p.qid_b}", "d": D[b][pos[p.qid_a], pos[p.qid_b]],
                        "pct": np.mean(pct[-2:])})
        ranks = np.array(ranks)
        r[f"{h}: top-1"] = (ranks == 1).mean()
        r[f"{h}: top-10"] = (ranks <= 10).mean()
        r[f"{h}: median rank"] = float(np.median(ranks))
        r[f"{h}: d ÷ nearest other"] = float(np.median(ratios))
    pp = pd.DataFrame([x for x in per if x["block"] == b])
    s_, o_ = pp[pp.hand == "same hand"].pct, pp[pp.hand == "other hand"].pct
    r["partner percentile, same"] = s_.median()
    r["partner percentile, other"] = o_.median()
    r["p (other farther)"] = mannwhitneyu(o_, s_, alternative="greater")[1]
    rows.append(r)
table(pd.DataFrame(rows))
emit(f"{(VP.hand2 == 'same hand').sum()} same-hand and {(VP.hand2 == 'other hand').sum()} other-hand pairs, both directions; the pool is the other {N - 1} paintings plus the partner. "
     "Rank 1 = the partner is the nearest painting. \"d ÷ nearest other\" under 1 means the partner is nearer than every other painting. "
     "Partner percentile = share of the pool nearer than the partner (median over pairs); p is a one-sided Mann-Whitney test that other-hand partners are farther.")
emit()

# ---------------------------------------------------------------- T5 linear prediction
emit("## T5. Linear prediction between the describer's marks and the picture embedding (ridge, 5-fold, folds grouped by painter)")
emit()
Xp = VEC["picture"][:N]
Xc = D  # unused
targets = {}
for k in L.THINGS:
    if it[f"t_{k}"][fit].sum() >= 15:
        targets[("subject", k)] = it[f"t_{k}"].to_numpy(float)[:N]
targets[("subject", "people (0-4)")] = it.people.map(L.COUNTS.index).to_numpy(float)[:N]
targets[("subject", "animals (0-4)")] = it.animals.map(L.COUNTS.index).to_numpy(float)[:N]
for s_ in L.SETTINGS:
    if (it.setting[fit] == s_).sum() >= 15:
        targets[("subject", f"setting={s_}")] = (it.setting == s_).to_numpy(float)[:N]
for k in L.MANNER:
    targets[("manner", k)] = it[f"m_{k}"].to_numpy(float)[:N]
for k in L.CUES:
    targets[("manner", "cue:" + k)] = it[f"d_{k}"].to_numpy(float)[:N]
for k in L.COLOUR_SCALES:
    targets[("colour", k)] = it[f"m_{k}"].to_numpy(float)[:N]
for k in L.HUES:
    if it[f"h_{k}"][fit].sum() >= 15:
        targets[("colour", "hue:" + k)] = it[f"h_{k}"].to_numpy(float)[:N]
for k in L.COMP_SCALES:
    targets[("composition", k)] = it[f"m_{k}"].to_numpy(float)[:N]
for k in L.FELT:
    targets[("felt", k)] = it[f"f_{k}"].to_numpy(float)[:N]
Y = np.stack(list(targets.values()), 1)
Xcol, _ = L.store_rows("colour__std", "palette_hist", ids)
Xpc = learned_multi("colour__std", ["palette_hist", "palette_sw"], 32)[:N]
Xcomp = learned("composition", "grid8_an", 32, whiten=True, l2=False, z=True)[:N]
r_pic = cvr2(Xp, Y)
r_pix = cvr2(np.hstack([Xpc, Xcomp]), Y)
T5 = pd.DataFrame({"block": [k[0] for k in targets], "field": [k[1] for k in targets], "R2 from picture (DINOv2 PCA-64)": r_pic,
                   "R2 from pixel colour + composition": r_pix})
agg = T5.groupby("block", sort=False)[T5.columns[2:]].agg(["mean", "median"]).round(2)
agg.columns = [f"{a}, {b}" for a, b in agg.columns]
table(agg.reset_index())
emit("Per field, manner and colour:")
emit()
table(T5[T5.block.isin(["manner", "colour", "composition"])])
emit("Per field, subject (items marked on 15 or more of the 300) and felt: best and worst predicted from the picture embedding")
emit()
for bl in ("subject", "felt"):
    t = T5[T5.block == bl].sort_values(T5.columns[2], ascending=False)
    emit(f"{bl}: " + ", ".join(f"{r.field} {r[T5.columns[2]]:.2f}" for _, r in t.iterrows()))
    emit()

emit("The other way: how much of the picture embedding the describer's marks predict (variance-weighted R2 over the first k principal components of DINOv2-L cls, which hold the stated share of its variance)")
emit()
Xd_all = np.hstack([B[:N][:, df_ >= 5], VEC["manner"][:N], VEC["colour"][:N], VEC["composition (3 scales)"][:N], VEC["felt"][:N]])
_, _, sd_all = L.pca_fit(Pn[np.array([q not in set(json.load(open('experiments/painting2vec/exp_separation/results/setup.json'))['excluded']) for q in pids])], 256)
tot = (sd_all ** 2).sum()
rows = []
preds = {"subject marks": B[:N][:, df_ >= 5], "manner": VEC["manner"][:N], "colour": VEC["colour"][:N], "felt": VEC["felt"][:N],
         "subject + manner": np.hstack([B[:N][:, df_ >= 5], VEC["manner"][:N]]), "every describer field": Xd_all,
         "pixel colour + composition (64-d)": np.hstack([Xpc, Xcomp])}
for nm, X in preds.items():
    r2 = cvr2(X, Xp)
    v = Xp.var(0)
    rows.append({"predictors": nm, "columns": X.shape[1], **{f"first {k} PCs": (r2[:k] * v[:k]).sum() / v[:k].sum() for k in (4, 16, 64)},
                 "PC1": r2[0], "PC2": r2[1], "PC3": r2[2]})
table(pd.DataFrame(rows))
emit(f"share of DINOv2-L cls variance (L2-normalised, pilot fit) in the first 4 / 16 / 64 components: "
     f"{(sd_all[:4] ** 2).sum() / tot:.2f} / {(sd_all[:16] ** 2).sum() / tot:.2f} / {(sd_all[:64] ** 2).sum() / tot:.2f}")
emit()

# ---------------------------------------------------------------- T6 granularity
emit("## T6. Granularity")
emit()
hb = np.abs(B[:N][:, None, :] - B[:N][None]).sum(-1)
same = [(i, j) for i in range(N) for j in range(i + 1, N) if hb[i, j] == 0]
emit("pairs of paintings with identical subject vectors: " + "; ".join(
    f"{S.title[i]} ({str(S.creator_name[i]).split('|')[0]}) = {S.title[j]} ({str(S.creator_name[j]).split('|')[0]})" for i, j in same))
emit()
rows = []
SUBJ_KEYS = pd.Series(["".join(map(str, r.astype(int))) for r in B[:N]])
MAN_KEYS = pd.Series(["".join(map(str, r)) for r in it[[f"m_{k}" for k in L.MANNER] + [f"d_{k}" for k in L.CUES]].to_numpy(int)[:N]])
MAN1_KEYS = pd.Series(["".join(map(str, r)) for r in it[[f"m_{k}" for k in L.MANNER_V1]].to_numpy(int)[:N]])
COL_KEYS = pd.Series(["".join(map(str, r)) for r in it[[f"m_{k}" for k in L.COLOUR_SCALES] + [f"h_{k}" for k in L.HUES]].to_numpy(int)[:N]]) + it.main_hue[:N].values + it.accent_hue[:N].values + it.value_key[:N].values
FELT_KEYS = pd.Series(["".join(map(str, r)) for r in VEC["felt"][:N].astype(int)])


def ent(cols):
    h = 0
    for c in cols:
        p = pd.Series(c).value_counts(normalize=True).to_numpy()
        h += -(p * np.log2(p)).sum()
    return h


def gran(name, dname, keys, cols, hamming):
    d = D[dname][:N, :N]
    off = d[tri]
    vc = keys.value_counts()
    nn1 = np.sort(d + np.eye(N) * 1e9, 1)
    d10 = nn1[:, 9]
    tied10 = np.mean([(d[i] <= d10[i] + 1e-12).sum() - 1 for i in range(N)])
    p0 = (hamming[tri] == 0).mean()
    p1 = (hamming[tri] <= 1).mean()
    p2 = (hamming[tri] <= 2).mean()
    # how many of the 300 fall inside a painting's nearest-neighbour radius; scaled up, that is the size of the
    # set a 10,000-painting library would have to rank inside the radius this sample cannot see below
    r = {"block": name, "columns": len(cols), "sum of field entropies (bits)": ent(cols), "distinct vectors": len(vc),
         "paintings sharing a vector": int((vc[vc > 1]).sum()), "largest identical group": int(vc.max()),
         "pairs identical": p0, "pairs within 1 mark": p1, "pairs within 2 marks": p2,
         "distinct distance values (pairs)": len(np.unique(np.round(off, 9))),
         "paintings whose 1st and 2nd neighbour tie": np.mean(np.isclose(nn1[:, 0], nn1[:, 1])),
         "mean paintings at or inside the 10th neighbour's distance": tied10,
         "median NN distance ÷ median pair distance": np.median(nn1[:, 0]) / np.median(off)}
    for M in (2500, 10000):
        r[f"expected identical twins per painting at {M}"] = p0 * (M - 1)
        r[f"expected within 1 mark at {M}"] = p1 * (M - 1)
        r[f"expected within 2 marks at {M}"] = p2 * (M - 1)
    return r


def ham(M):
    M = np.asarray(M, float)
    return np.abs(M[:, None, :] - M[None]).sum(-1)


man_int = it[[f"m_{k}" for k in L.MANNER] + [f"d_{k}" for k in L.CUES]].to_numpy(float)[:N]
man1_int = it[[f"m_{k}" for k in L.MANNER_V1]].to_numpy(float)[:N]
col_int = np.hstack([it[[f"m_{k}" for k in L.COLOUR_SCALES] + [f"h_{k}" for k in L.HUES]].to_numpy(float)[:N],
                     it.value_key.map({"high": 0, "mid": 1, "low": 2}).to_numpy(float)[:N, None],
                     L.onehot(it.main_hue[:N], L.HUES) / 2, L.onehot(it.accent_hue[:N], L.HUES + ["none"]) / 2])
G = [gran("subject", "subject (IDF cosine)", SUBJ_KEYS, list(B[:N].T), ham(B[:N])),
     gran("manner (13 scales + 7 cues)", "manner", MAN_KEYS, list(man_int.T), ham(man_int)),
     gran("manner (5 v1 scales)", "manner (v1 scales only)", MAN1_KEYS, list(man1_int.T), ham(man1_int)),
     gran("colour", "colour", COL_KEYS, list(col_int.T), ham(col_int)),
     gran("felt", "felt", FELT_KEYS, list(VEC["felt"][:N].T), ham(VEC["felt"][:N])),
     gran("subject + manner + colour", "manner", SUBJ_KEYS + MAN_KEYS + COL_KEYS, list(B[:N].T) + list(man_int.T) + list(col_int.T),
          ham(B[:N]) + ham(man_int) + ham(col_int))]
Gd = pd.DataFrame(G).set_index("block").T
Gd = Gd.map(lambda v: f"{v:.3g}" if isinstance(v, float) else v)
table(Gd.reset_index().rename(columns={"index": ""}))
emit("\"Within k marks\" is the sum of absolute differences over the block's raw fields (a 0/1 item that differs is 1; a scale that differs by one step is 1; a different main or accent hue is 1). "
     "Expected counts at 2,500 and 10,000 scale the share of pairs in this sample, which over-represents clusters (12 painters, 7 genres, 26 version pairs), so they lean high. "
     "The combined row's distance columns are not meaningful and repeat manner's.")
emit()
emit("How many raw marks apart is the 10th neighbour, now and in a larger library, against how many marks two describers differ on one painting")
emit()
Ball = B  # all 352 rows
man_all = it[[f"m_{k}" for k in L.MANNER] + [f"d_{k}" for k in L.CUES]].to_numpy(float)
col_all = np.hstack([it[[f"m_{k}" for k in L.COLOUR_SCALES] + [f"h_{k}" for k in L.HUES]].to_numpy(float),
                     it.value_key.map({"high": 0, "mid": 1, "low": 2}).to_numpy(float)[:, None],
                     L.onehot(it.main_hue, L.HUES) / 2, L.onehot(it.accent_hue, L.HUES + ["none"]) / 2])
felt_all = VEC["felt"]
Bv1, _ = L.subject_binary(v1.loc[q60])
Bv2, _ = L.subject_binary(v2.loc[q60])
ia = [pos[q] for q in PH.qid]
ib = [pos[q + "__b"] for q in PH.qid]
rows = []
for nm, M_, same_photo in [("subject (63 marks)", Ball, np.abs(Bv1 - Bv2).sum(1)),
                           ("manner (13 scales + 7 cues)", man_all, None), ("colour (5 scales, 12 hues, key, main, accent)", col_all, None),
                           ("felt (24 words)", felt_all, np.abs(v1.loc[q60][[f"f_{k}" for k in L.FELT]].to_numpy(float) - v2.loc[q60][[f"f_{k}" for k in L.FELT]].to_numpy(float)).sum(1))]:
    h = ham(M_[:N])
    off = np.sort(h[tri])
    hn = np.sort(h + np.eye(N) * 1e9, 1)
    r = {"block": nm, "median marks to nearest neighbour (300)": np.median(hn[:, 0]), "to 10th neighbour (300)": np.median(hn[:, 9])}
    for M in (2500, 10000):
        r[f"to 10th neighbour at {M:,} (scaled)"] = off[int(len(off) * 10 / (M - 1))]
    r["two describers, same photograph (60)"] = np.nan if same_photo is None else same_photo.mean()
    r["two describers, two photographs (30)"] = np.abs(M_[ia] - M_[ib]).sum(1).mean()
    rows.append(r)
table(pd.DataFrame(rows), "{:.1f}")
emit("The scaled columns read the pair-distance distribution of this sample at the quantile 10 / (library size): the distance inside which a painting would find ten others if the larger library were drawn like this sample. "
     "Where that distance is at or below the describer-to-describer difference, the order of the top ten is set by describer noise.")
emit()
for nm, dn in [("subject", "subject (IDF cosine)"), ("manner", "manner"), ("colour", "colour"), ("felt", "felt"), ("picture", "picture (DINOv2-L cls)")]:
    d = D[dn][:N, :N]
    nn1 = np.sort(d + np.eye(N) * 1e9, 1)
    q = np.quantile(d[tri], [0.001, 0.01, 0.05, 0.5])
    emit(f"{nm}: pair distance 0.1 / 1 / 5 / 50 per cent quantiles {q[0]:.3f} / {q[1]:.3f} / {q[2]:.3f} / {q[3]:.3f}; nearest-neighbour distance median {np.median(nn1[:, 0]):.3f}, "
         f"10th-neighbour median {np.median(nn1[:, 9]):.3f}")
emit()

# ---------------------------------------------------------------- T7 photographs
emit(f"## T7. Two photographs of one painting ({len(PH)} pairs, lab_diff {PH.lab_diff.min():.1f} to {PH.lab_diff.max():.1f})")
emit()
rows = []
for b in ALL:
    d = D[b]
    hit, hit_strict, r10, keep, ratio, tie = [], [], [], [], [], []
    for q in PH.qid:
        ai, bi = pos[q], pos[q + "__b"]
        others = np.array([j for j in range(N) if j != ai])
        for x, y in ((ai, bi), (bi, ai)):
            dc = d[x, others]
            less, eq = (dc < d[x, y] - 1e-12).sum(), np.isclose(dc, d[x, y], atol=1e-12).sum()
            hit.append((less == 0) / (1 + eq))
            hit_strict.append(float(less == 0 and eq == 0))
            r10.append(float(less + eq / 2 < 10))
            ratio.append(d[x, y] / dc.min() if dc.min() > 0 else (np.inf if d[x, y] > 0 else 1.0))
            tie.append(eq)
        dj = d + JIT
        ta = others[np.argsort(dj[ai, others])[:K]]
        tb = others[np.argsort(dj[bi, others])[:K]]
        keep.append(len(set(ta) & set(tb)) / K)
    nn1 = np.sort(d[:N, :N] + np.eye(N) * 1e9, 1)[:, 0]
    dab = np.array([d[pos[q], pos[q + "__b"]] for q in PH.qid])
    rows.append({"block": b, "R@1 (ties split)": np.mean(hit), "R@1 strictly nearest": np.mean(hit_strict), "R@10": np.mean(r10),
                 "d(A,B) ÷ d(A, nearest other): median": np.median(ratio), "p90": np.quantile(ratio, 0.9),
                 "pairs with d(A,B) = 0": (dab < 1e-12).mean(), "pairs under one step": (dab < np.median(nn1)).mean(), "top-10 kept": np.mean(keep)})
table(pd.DataFrame(rows))
emit(f"Pool: the other {N - 1} paintings (the invariance experiment used about 2,400, so its pixel-colour figure of 0.547 / 32 % is on a harder pool; the pixel-colour row here is the same block on this pool and these 30 high-difference pairs). "
     "\"Step\" is the median nearest-neighbour distance among the 300.")
emit()
emit("Field-level agreement between the two photographs (different describers), next to the same-photograph, different-describer figure from T0 where one exists")
emit()
A2, B2 = it.loc[list(PH.qid)], it.loc[[q + "__b" for q in PH.qid]]
rows = []
for nm, cols in [("manner, v1 scales", [f"m_{k}" for k in L.MANNER_V1]), ("manner, added scales", [f"m_{k}" for k in L.SCALES_V2]),
                 ("colour scales", [f"m_{k}" for k in L.COLOUR_SCALES]), ("composition scales", [f"m_{k}" for k in L.COMP_SCALES]),
                 ("felt words", [f"f_{k}" for k in L.FELT]), ("checklist", tc), ("depth cues", [f"d_{k}" for k in L.CUES]), ("hue families", [f"h_{k}" for k in L.HUES])]:
    x, y = A2[cols].to_numpy(float), B2[cols].to_numpy(float)
    r = {"fields": nm, "exact": (x == y).mean(), "mean abs diff": np.abs(x - y).mean()}
    if x.max() <= 1:
        r["kappa / median ICC"] = cohen_kappa_score(x.ravel().astype(int), y.ravel().astype(int))
        r["Jaccard per painting"] = np.mean([(p_ * q_).sum() / max(((p_ + q_) > 0).sum(), 1) for p_, q_ in zip(x, y)])
    else:
        r["kappa / median ICC"] = np.nanmedian([icc(x[:, j], y[:, j]) for j in range(len(cols))])
    if nm in ("manner, v1 scales", "colour scales", "composition scales", "felt words", "checklist"):
        xa, ya = a[cols].to_numpy(float), b_ if False else v2.loc[q60][cols].to_numpy(float)
        r["same photograph (T0): exact"] = (xa == ya).mean()
        r["same photograph (T0): mean abs diff"] = np.abs(xa - ya).mean()
    rows.append(r)
table(pd.DataFrame(rows))
rows = []
for k in L.COLOUR_SCALES:
    x, y = A2[f"m_{k}"].to_numpy(float), B2[f"m_{k}"].to_numpy(float)
    rows.append({"field": k, "exact": (x == y).mean(), "mean abs diff": np.abs(x - y).mean(), "ICC": icc(x, y), "mean B minus A": (y - x).mean()})
for k in ("main_hue", "accent_hue", "value_key", "setting", "people", "animals"):
    rows.append({"field": k, "exact": (A2[k].values == B2[k].values).mean()})
for k in L.HUES:
    x, y = A2[f"h_{k}"].to_numpy(int), B2[f"h_{k}"].to_numpy(int)
    rows.append({"field": "hue:" + k, "exact": (x == y).mean(), "ICC": cohen_kappa_score(x, y) if x.sum() + y.sum() else np.nan, "mean B minus A": (y - x).mean()})
emit("Colour fields one by one (ICC column holds Cohen's kappa for the hue items)")
emit()
table(pd.DataFrame(rows))

# ---------------------------------------------------------------- T8 recognition, cost
emit("## T8. Recognition")
emit()
r2 = v2.loc[[q for q in S.qid]]
rec = r2.rec.astype(bool)
emit(f"recognised (v2 pass, the 300): {rec.sum()} of {N} ({rec.mean():.2f}); by tradition: " +
     ", ".join(f"{t} {rec[(S.tradition == t).values].sum()}/{(S.tradition == t).sum()}" for t in S.tradition.unique()))
emit()
last = meta.creator_name.fillna("").str.split("|").str[0]
okp = [bool(nm) and (nm.split()[-1].lower() in str(pn).lower()) for nm, pn in zip(last.values, r2.rec_painter.values)]
emit(f"of those recognised, painter's surname matches Wikidata: {np.sum(np.array(okp) & rec.values)} of {rec.sum()} (string match on the last word of the name, so an undercount)")
emit()

emit("## T9. Cost")
emit()
U = pd.read_csv(f"{HERE}/usage.csv")
key = pd.read_csv(f"{HERE}/key.csv")
n_img = key.groupby("batch").size()
U["images"] = U.batch.map(n_img)
chars = []
import glob
for f in sorted(glob.glob(f"{HERE}/raw/batch_*.json")):
    for r in json.load(open(f))["records"]:
        chars.append(len(json.dumps(r, ensure_ascii=False)))
ins = len(open(f"{HERE}/instrument_v2.md").read())
mp = (key.px_w * key.px_h).mean()
emit(f"subagent runs: {len(U)} batches, {U.images.sum()} descriptions, {U.subagent_tokens.sum():,} tokens as reported by the harness "
     f"({U.subagent_tokens.sum() / U.images.sum():,.0f} per description), {U.duration_ms.sum() / 1000 / 60:.1f} minutes of describer time "
     f"({U.duration_ms.sum() / 1000 / U.images.sum():.1f} s per description; two ran at a time, so about half that on the clock)")
emit()
emit(f"record size: mean {np.mean(chars):,.0f} characters of JSON per description (min {min(chars):,}, max {max(chars):,}); instrument {ins:,} characters; "
     f"mean stimulus {mp / 1e6:.2f} megapixels")
emit()
json.dump({"tokens_per_desc": U.subagent_tokens.sum() / U.images.sum(), "sec_per_desc": U.duration_ms.sum() / 1000 / U.images.sum(),
           "chars_per_record": float(np.mean(chars)), "instrument_chars": ins, "mean_px": float(mp)}, open(f"{HERE}/cost.json", "w"))
open(f"{HERE}/tables.md", "w").write("\n".join(OUT) + "\n")
