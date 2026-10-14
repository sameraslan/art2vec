"""Evaluation of one candidate block. Labels are used here and only here."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import rankdata, skew, spearmanr

from lib import HERE, cosdist, load_pilot_meta, load_versions, multihot, ridge_fit

K = 10


def _auc_rows(D, pos, pool):
    """Per query: P(distance to a positive < distance to a non-positive) within its pool.
    D [q, n]; pos, pool bool [q, n]. Returns (auc per query, valid mask)."""
    Dm = np.where(pool, D, np.inf)
    r = rankdata(Dm, axis=1)  # ascending; items outside the pool rank last
    npos = pos.sum(1)
    nneg = pool.sum(1) - npos
    ok = (npos > 0) & (nneg > 0)
    s = (r * pos).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        u = s - npos * (npos + 1) / 2  # number of (pos, neg) pairs where neg is nearer
        auc = 1 - u / (npos * nneg)
    return auc, ok


def _p_at_k(D, pos, pool, k=K):
    Dm = np.where(pool, D, np.inf)
    idx = np.argpartition(Dm, k, axis=1)[:, :k]
    hit = np.take_along_axis(pos, idx, 1).mean(1)
    chance = pos.sum(1) / np.maximum(pool.sum(1), 1)
    return hit, chance


def _folds(groups, n_splits=5, seed=0):
    """Group k-fold: every group in one fold. groups: array of hashables."""
    ug = pd.unique(groups)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(ug))
    fold_of = {g: i % n_splits for i, g in zip(range(len(ug)), ug[perm])}
    return np.array([fold_of[g] for g in groups])


def _strat_folds(y, n_splits=5, seed=0):
    rng = np.random.default_rng(seed)
    f = np.zeros(len(y), int)
    for c in np.unique(y):
        ix = np.where(y == c)[0]
        ix = ix[rng.permutation(len(ix))]
        f[ix] = np.arange(len(ix)) % n_splits
    return f


def _std(X):
    return (X - X.mean(0)) / (X.std(0) + 1e-9)


def cv_ridge(X, Y, folds, alpha=10.0, standardise=True):
    """Out-of-fold ridge predictions. X standardised inside each fold."""
    P = np.zeros(Y.shape, dtype=np.float64)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        mu, sd = X[tr].mean(0), X[tr].std(0)
        if not standardise:
            sd = np.where(sd > 1e-6, 1.0, 0.0)
        live = sd > 1e-6  # a column that is constant in the training folds is dropped
        mu, sd = mu[live], sd[live]
        ym = Y[tr].mean(0)
        W = ridge_fit(((X[tr][:, live] - mu) / sd).astype(np.float64), (Y[tr] - ym).astype(np.float64), alpha)
        P[te] = ((X[te][:, live] - mu) / sd) @ W + ym
    return P


def cv_classify(X, y, folds, alpha=10.0):
    """One-vs-rest ridge on one-hot targets (a linear probe); returns accuracy, balanced accuracy."""
    classes, yi = np.unique(y, return_inverse=True)
    Y = np.eye(len(classes))[yi]
    pred = cv_ridge(X, Y, folds, alpha).argmax(1)
    acc = (pred == yi).mean()
    bal = np.mean([(pred[yi == c] == c).mean() for c in range(len(classes))])
    return float(acc), float(bal)


class Evaluator:
    def __init__(self, subset=None):
        """subset: optional bool mask over all 2,000 pilot rows; evaluation then uses kept & subset."""
        m = load_pilot_meta()
        self.meta_all = m
        self.keep_fit = m.keep.values  # rows the treatments are fitted on
        if subset is not None:
            m = m.assign(keep=m.keep.values & subset)
        self.keep = m.keep.values
        m = m[m.keep].reset_index(drop=True)
        self.m = m
        n = len(m)
        self.n = n
        # label matrices
        G, _ = multihot(m.genre_set.tolist())
        self.has_genre = G.sum(1) > 0
        self.same_genre = (G @ G.T) > 0
        B, self.broad_vocab = multihot(m.broad_set.tolist())
        self.has_broad = B.sum(1) > 0
        self.same_broad = (B @ B.T) > 0
        Dp, _ = multihot(m.dep_set.tolist(), min_count=2)
        self.has_dep = Dp.sum(1) > 0
        inter = Dp @ Dp.T
        sz = Dp.sum(1)
        self.dep_jacc = (inter / np.maximum(sz[:, None] + sz[None] - inter, 1)).astype(np.float32)
        Mv, _ = multihot(m.move_set.tolist())
        self.has_move = Mv.sum(1) > 0
        self.same_move = (Mv @ Mv.T) > 0
        p = m.painter.to_numpy(dtype=object)
        self.has_painter = p != ""
        self.same_painter = (p[:, None] == p[None]) & self.has_painter[:, None] & self.has_painter[None]
        np.fill_diagonal(self.same_painter, False)
        cnt = pd.Series(p[self.has_painter]).value_counts()
        self.p8 = np.isin(p, cnt[cnt >= 8].index.values)
        self.year = m.inception_year.values.astype(float)
        self.has_year = np.isfinite(self.year)
        self.rank = (m.stratum == "sitelink_rank").values
        self.eye = np.eye(n, dtype=bool)
        # groups for grouped CV: painter, or the painting itself when no painter is recorded
        self.groups = np.where(self.has_painter, p, m.qid.to_numpy(dtype=object))
        self.gfold = _folds(self.groups)
        self._describer()
        self._versions()
        self._chance()

    # ------------------------------------------------------------------ describer ground truth
    def _describer(self):
        r = pd.read_csv(HERE.parent / "describer" / "records_long.csv")
        r = r[r.cond.isin(["orig", "retest"])]
        tcols = [c for c in r.columns if c.startswith("t_")]
        mcols = ["m_abstraction", "m_contour", "m_finish", "m_detail", "m_depth"]
        g = r.groupby("qid")[tcols + [c for c in r.columns if c.startswith("m_")]].mean()
        pos = {q: i for i, q in enumerate(self.m.qid)}
        g = g[g.index.isin(pos)]
        self.d_idx = np.array([pos[q] for q in g.index])
        T = g[tcols].values
        mn = np.minimum(T[:, None], T[None]).sum(-1)
        mx = np.maximum(T[:, None], T[None]).sum(-1)
        iu = np.triu_indices(len(g), 1)
        self.d_iu = iu
        self.d_subj = (1 - mn / np.maximum(mx, 1e-9))[iu]
        self.d_scale = {c[2:]: np.abs(g[c].values[:, None] - g[c].values[None])[iu] for c in mcols}
        self.d_raw = {c[2:]: g[c].values.astype(float) for c in mcols}
        M3 = g[["m_abstraction", "m_contour", "m_finish"]].values
        self.d_man3 = np.sqrt(((M3[:, None] - M3[None]) ** 2).sum(-1))[iu]
        M5 = g[mcols].values
        self.d_man5 = np.sqrt(((M5[:, None] - M5[None]) ** 2).sum(-1))[iu]
        self.d_n = len(g)

    # ------------------------------------------------------------------ version pairs
    def _versions(self):
        ids, vm, pairs = load_versions()
        self.v_ids = ids
        self.v_pos = {q: i for i, q in enumerate(ids)}
        self.pairs = pairs
        self.p_pos = {q: i for i, q in enumerate(self.m.qid)}

    def _chance(self):
        c = {}
        g = self.has_genre
        sg = self.same_genre[g][:, g]
        c["genre_p10"] = float((sg.sum(1) - 1).mean() / (g.sum() - 1))
        d = self.has_dep
        J = self.dep_jacc[d][:, d]
        c["depicts_j10"] = float((J.sum(1) - 1).mean() / (d.sum() - 1))
        mv = self.has_move
        sm = self.same_move[mv][:, mv]
        c["move_p10"] = float((sm.sum(1) - 1).mean() / (mv.sum() - 1))
        hp = self.has_painter
        c["painter_p10"] = float(self.same_painter[hp][:, hp].sum(1).mean() / (hp.sum() - 1))
        self.chance = c

    # ------------------------------------------------------------------ the evaluation
    def evaluate(self, Zp, Zv=None, probes=True, k_probe=64):
        """Zp: [n_kept, d] pilot vectors (kept rows only). Zv: [355, d] versions vectors or None."""
        out = {"dim": int(Zp.shape[1])}
        self._Z = Zp
        D = cosdist(Zp)
        D[self.eye] = np.inf
        out.update(self._subject(D))
        out.update(self._describer_eval(D))
        out.update(self._manner(D))
        out.update(self._neigh(D))
        if Zv is not None:
            out.update(self._version_eval(Zp, Zv))
        if probes:
            out.update(self._probes(Zp[:, :k_probe]))
        return out

    def topk(self, D, mask=None, k=K):
        if mask is None:
            return np.argpartition(D, k, axis=1)[:, :k]
        Dm = D[mask][:, mask]
        return np.argpartition(Dm, k, axis=1)[:, :k]

    def _subject(self, D):
        o = {}
        g = self.has_genre
        idx = self.topk(D, g)
        o["genre_p10"] = float(np.take_along_axis(self.same_genre[g][:, g], idx, 1).mean())
        d = self.has_dep
        idx = self.topk(D, d)
        o["depicts_j10"] = float(np.take_along_axis(self.dep_jacc[d][:, d], idx, 1).mean())
        b = self.has_broad
        idx = self.topk(D, b)
        o["broad_p10"] = float(np.take_along_axis(self.same_broad[b][:, b], idx, 1).mean())
        # the same two with the query's own painter taken out of the pool
        Dx = np.where(self.same_painter, np.inf, D)
        idx = self.topk(Dx, g)
        o["genre_p10_otherpainter"] = float(np.take_along_axis(self.same_genre[g][:, g], idx, 1).mean())
        idx = self.topk(Dx, d)
        o["depicts_j10_otherpainter"] = float(np.take_along_axis(self.dep_jacc[d][:, d], idx, 1).mean())
        return o

    def _describer_eval(self, D):
        Dd = D[self.d_idx][:, self.d_idx][self.d_iu]
        rk = rankdata(Dd)
        rs, r3 = rankdata(self.d_subj), rankdata(self.d_man3)
        c = lambda a, b: float(np.corrcoef(a, b)[0, 1])
        o = {"desc_subj": c(rk, rs), "desc_man3": c(rk, r3), "desc_man5": c(rk, rankdata(self.d_man5))}
        for kname, v in self.d_scale.items():
            o[f"desc_{kname}"] = c(rk, rankdata(v))
        # partial rank correlations
        r_sm = c(rs, r3)
        part = lambda rxy, rxz, ryz: (rxy - rxz * ryz) / np.sqrt((1 - rxz**2) * (1 - ryz**2))
        # local version: the 3 nearest among the 60, their label distance over the mean label distance
        n = self.d_n
        Dsq = np.full((n, n), np.inf, dtype=np.float64)
        Dsq[self.d_iu] = Dd
        Dsq = np.minimum(Dsq, Dsq.T)
        nn = np.argsort(Dsq, axis=1)[:, :3]
        def local(v):
            L = np.zeros((n, n)); L[self.d_iu] = v; L = L + L.T
            return float(np.take_along_axis(L, nn, 1).mean() / (L.sum() / (n * (n - 1))))
        o["desc_subj_nn3"] = local(self.d_subj)
        o["desc_man3_nn3"] = local(self.d_man3)
        for kname, v in self.d_scale.items():
            o[f"desc_{kname}_nn3"] = local(v)
        # leave-one-out linear readout of each manner scale from the first 16 dimensions
        Zd = self._Z[self.d_idx][:, :16].astype(np.float64)
        Zd = (Zd - Zd.mean(0)) / (Zd.std(0) + 1e-9)
        H = Zd @ np.linalg.solve(Zd.T @ Zd + 10.0 * np.eye(Zd.shape[1]), Zd.T)
        h = np.diag(H) + 1 / len(Zd)
        for kname, v in self.d_raw.items():
            yc = v - v.mean()
            loo = yc - (yc - H @ yc) / (1 - h)
            o[f"read_{kname}"] = float(np.corrcoef(rankdata(loo), rankdata(yc))[0, 1])
        o["desc_subj_given_man"] = float(part(o["desc_subj"], o["desc_man3"], r_sm))
        o["desc_man_given_subj"] = float(part(o["desc_man3"], o["desc_subj"], r_sm))
        return o

    def _manner(self, D):
        o = {}
        q = self.p8 & self.has_broad
        Dq = D[q]
        pos = self.same_painter[q]
        pool_all = np.broadcast_to(self.has_painter[None], Dq.shape) & ~self.eye[q]
        pool_b = pool_all & self.has_broad[None]
        sb = self.same_broad[q]
        yq = self.year[q]
        with np.errstate(invalid="ignore"):
            era = np.abs(yq[:, None] - self.year[None]) <= 30
        for name, pool in (("all", pool_all), ("diffgenre", pool_b & ~sb), ("samegenre", pool_b & sb),
                           ("era", pool_all & era), ("diffgenre_era", pool_b & ~sb & era)):
            pp = pos & pool
            auc, ok = _auc_rows(Dq, pp, pool)
            hit, ch = _p_at_k(Dq, pp, pool)
            o[f"painter_auc_{name}"] = float(auc[ok].mean())
            o[f"painter_p10_{name}"] = float(hit[ok].mean())
            o[f"painter_p10chance_{name}"] = float(ch[ok].mean())
            o[f"painter_nq_{name}"] = int(ok.sum())
        # movement: any, and with the query's own painter removed from the pool
        q = self.has_move
        Dq = D[q]
        pos = self.same_move[q]
        pool = np.broadcast_to(self.has_move[None], Dq.shape) & ~self.eye[q]
        hit, _ = _p_at_k(Dq, pos & pool, pool)
        o["move_p10"] = float(hit.mean())
        pool2 = pool & ~self.same_painter[q]
        auc, ok = _auc_rows(Dq, pos & pool2, pool2)
        o["move_auc_otherpainter"] = float(auc[ok].mean())
        q2 = self.has_move & self.has_broad
        Dq = D[q2]
        pool3 = (np.broadcast_to((self.has_move & self.has_broad)[None], Dq.shape) & ~self.eye[q2]
                 & ~self.same_painter[q2] & ~self.same_broad[q2])
        auc, ok = _auc_rows(Dq, self.same_move[q2] & pool3, pool3)
        o["move_auc_otherpainter_diffgenre"] = float(auc[ok].mean())
        return o

    def _neigh(self, D):
        o = {}
        idx = self.topk(D)
        hp = self.has_painter
        o["painter_repeat10"] = float(np.take_along_axis(self.same_painter, idx, 1)[hp].mean())
        hy = self.has_year
        idy = self.topk(D, hy)
        y = self.year[hy]
        dy = np.abs(y[idy] - y[:, None])
        rng = np.random.default_rng(0)
        ridx = rng.integers(0, len(y), size=idy.shape)
        dr = np.abs(y[ridx] - y[:, None])
        o["year_spread10"] = float(np.median(np.median(dy, 1)))
        o["year_spread_rand"] = float(np.median(np.median(dr, 1)))
        o["year_spread_ratio"] = o["year_spread10"] / o["year_spread_rand"]
        n10 = np.bincount(idx.ravel(), minlength=self.n)
        o["hub_skew"] = float(skew(n10))
        o["hub_zero"] = float((n10 == 0).mean())
        o["hub_max"] = int(n10.max())
        return o

    def _version_eval(self, Zp, Zv):
        """Rank of the partner among the pilot gallery (pilot minus the pair itself) plus the partner."""
        pr = self.pairs
        ia = np.array([self.v_pos[q] for q in pr.qid_a])
        ib = np.array([self.v_pos[q] for q in pr.qid_b])
        Dvp = cosdist(Zv, Zp)  # [355, n]
        Dvv = cosdist(Zv)
        ranks, ratios = [], []
        for a, b, qa, qb in zip(ia, ib, pr.qid_a, pr.qid_b):
            rr, ra = [], []
            for x, y in ((a, b), (b, a)):
                d = Dvp[x].copy()
                for q in (qa, qb):
                    if q in self.p_pos:
                        d[self.p_pos[q]] = np.inf
                rr.append(1 + int((d < Dvv[x, y]).sum()))
                ra.append(np.log(max(Dvv[x, y], 1e-6) / max(d.min(), 1e-6)))
            ranks.append(np.mean(rr))
            ratios.append(np.exp(np.mean(ra)))
        r = np.array(ranks)
        ratio = np.array(ratios)  # distance to the partner / distance to the nearest other painting
        o = {}
        yes = (pr.composition_match == "yes").values
        series = (pr.relation == "series_motif").values
        var_ns = (pr.composition_match == "variant").values & ~series
        same, other = (pr.hand == "same_hand").values, (pr.hand == "other_hand").values
        for name, msk in (("all", np.ones(len(pr), bool)), ("yes", yes), ("variant", var_ns), ("series", series),
                          ("yes_same", yes & same), ("yes_other", yes & other),
                          ("same", same & ~series), ("other", other & ~series)):
            o[f"ver_n_{name}"] = int(msk.sum())
            o[f"ver_med_{name}"] = float(np.median(r[msk]))
            o[f"ver_top1_{name}"] = float((r[msk] <= 1).mean())
            o[f"ver_top10_{name}"] = float((r[msk] <= 10).mean())
            o[f"ver_ratio_{name}"] = float(np.median(ratio[msk]))
        # does the rank separate other-hand copies from same-hand versions (same composition only)?
        from scipy.stats import mannwhitneyu
        a, b = r[yes & other], r[yes & same]
        u = mannwhitneyu(a, b, alternative="two-sided")
        o["ver_hand_auc"] = float(u.statistic / (len(a) * len(b)))  # P(other-hand ranked farther)
        o["ver_hand_p"] = float(u.pvalue)
        a, b = ratio[yes & other], ratio[yes & same]
        u = mannwhitneyu(a, b, alternative="two-sided")
        o["ver_ratio_hand_auc"] = float(u.statistic / (len(a) * len(b)))
        o["ver_ratio_hand_p"] = float(u.pvalue)
        unk = (pr.hand == "unknown").values
        a = ratio[yes & (other | unk)]
        u = mannwhitneyu(a, b, alternative="two-sided")
        o["ver_ratio_hand_auc_incl_anon"] = float(u.statistic / (len(a) * len(b)))
        o["ver_ratio_hand_p_incl_anon"] = float(u.pvalue)
        o["ver_ratio_yes_anon"] = float(np.median(ratio[yes & unk]))
        self.last_ver = (r, ratio)
        return o

    def _probes(self, Z):
        o = {}
        Z = Z.astype(np.float64)
        # painter (8+ works), stratified folds
        q = self.p8
        acc, bal = cv_classify(Z[q], self.m.painter.to_numpy(dtype=object)[q], _strat_folds(self.m.painter.to_numpy(dtype=object)[q]))
        o["probe_painter_acc"] = acc
        o["probe_painter_n"] = int(q.sum())
        # year, grouped by painter: European rank stratum, and everything
        for name, q in (("eu", self.has_year & self.rank), ("all", self.has_year)):
            y = self.year[q][:, None]
            p = cv_ridge(Z[q], y, self.gfold[q])
            o[f"probe_year_r2_{name}"] = float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())
            o[f"probe_year_mae_{name}"] = float(np.abs(y - p).mean())
        q = self.has_year & self.rank
        Zc = Z[q] - Z[q].mean(0)
        yc = self.year[q] - self.year[q].mean()
        o["pc_year_r"] = [float(np.corrcoef(Zc[:, i], yc)[0, 1]) for i in range(min(4, Z.shape[1]))]
        o["pc_year_maxabs"] = float(np.max(np.abs(o["pc_year_r"])))
        # movement (first token, classes with 20+), grouped by painter
        mv = self.m.move_set.map(lambda s: s[0] if s else "").to_numpy(dtype=object)
        cnt = pd.Series(mv[mv != ""]).value_counts()
        q = np.isin(mv, cnt[cnt >= 20].index.values)
        acc, bal = cv_classify(Z[q], mv[q], self.gfold[q])
        o["probe_move_acc"], o["probe_move_bal"] = acc, bal
        o["probe_move_majority"] = float(cnt.max() / q.sum())
        o["probe_move_k"] = int((cnt >= 20).sum())
        # tradition (7 classes), stratified
        tr = self.m.tradition.to_numpy(dtype=object)
        q = tr != "unknown"
        acc, bal = cv_classify(Z[q], tr[q], _strat_folds(tr[q]))
        o["probe_trad_bal"] = bal
        # ... and non-European against European only among the six non-European traditions
        q = (tr != "unknown") & (tr != "european_american")
        acc, bal = cv_classify(Z[q], tr[q], _strat_folds(tr[q]))
        o["probe_trad_noneu_bal"] = bal
        # fame: rank stratum, log sitelinks, grouped by painter
        q = self.rank
        y = np.log(self.m.sitelinks.values[q].astype(float))[:, None]
        p = cv_ridge(Z[q], y, self.gfold[q])
        o["probe_fame_r2"] = float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())
        o["probe_fame_rho"] = float(spearmanr(y[:, 0], p[:, 0]).statistic)
        # fame within painter: demean both by painter (8+ works in the rank stratum)
        q = self.rank & self.p8
        df = pd.DataFrame(Z[q])
        g = self.m.painter.to_numpy(dtype=object)[q]
        Zw = (df - df.groupby(g).transform("mean")).values
        yw = pd.Series(np.log(self.m.sitelinks.values[q].astype(float)))
        yw = (yw - yw.groupby(g).transform("mean")).values[:, None]
        p = cv_ridge(Zw, yw, self.gfold[q], alpha=100.0)
        o["probe_fame_within_rho"] = float(spearmanr(yw[:, 0], p[:, 0]).statistic)
        o["probe_fame_within_r2"] = float(1 - ((yw - p) ** 2).sum() / (yw**2).sum())
        o["probe_fame_within_n"] = int(q.sum())
        # museum: rank stratum, museums with 25+, grouped by painter; baseline = year + country
        col = self.m.collection_name.fillna("").to_numpy(dtype=object)
        cnt = pd.Series(col[self.rank & (col != "")]).value_counts()
        mus = cnt[cnt >= 25].index.values
        q = self.rank & np.isin(col, mus) & self.has_year
        yr = (self.year[q] - 1600) / 200
        ctry = self.m.country_name.fillna("?").to_numpy(dtype=object)[q]
        cc = pd.Series(ctry).value_counts()
        ctry = np.where(np.isin(ctry, cc[cc >= 5].index.values), ctry, "other")
        base = np.column_stack([yr, yr**2, yr**3, pd.get_dummies(ctry).values.astype(float)])
        f = self.gfold[q]
        grid = (1.0, 10.0, 100.0, 1000.0)  # best of the grid for each, the same favour to all three
        a_v = max(cv_classify(Z[q], col[q], f, alpha=a)[0] for a in grid)
        a_b = max(cv_classify(base, col[q], f, alpha=a)[0] for a in grid)
        Z16 = _std(Z[q][:, :16])
        a_bv = max(cv_classify(np.column_stack([base, Z16 * w]), col[q], f, alpha=a)[0] for a in grid for w in (1.0,))
        o["probe_museum_acc"], o["probe_museum_base"], o["probe_museum_base_plus"] = a_v, a_b, a_bv
        o["probe_museum_n"], o["probe_museum_k"] = int(q.sum()), int(len(mus))
        o["probe_museum_majority"] = float(pd.Series(col[q]).value_counts().max() / q.sum())
        return o
