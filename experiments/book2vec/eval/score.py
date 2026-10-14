"""Score block files against the labelled pair sets.

    .venv/bin/python -m eval.score NAME_OR_PATH [...] --tag TAG [--ref NAME]
                                   [--exclude KEY ...] [--exclude-flagged] [--boot 2000]

Writes results/TAG_scores.csv, TAG_pairs.csv, TAG_checks.csv, TAG_cross.csv and TAG.md.

What the numbers are
- AUC: the probability that a labelled pair is closer than a random negative pair (different
  authors, not related by translation / edition / series / retelling). 0.5 is chance, 1 means
  every labelled pair is closer than every negative. The interval is a 95% percentile bootstrap
  over the labelled pairs only; pairs that share a book are not independent, so it is a little
  too narrow. With --ref, dAUC is this block minus the reference on the same pairs (paired
  bootstrap); an interval that contains 0 means the difference is within noise.
- pct_rank: for each ordered pair (anchor, partner), the share of the other books that are
  closer to the anchor than the partner is. 0 = the partner is the nearest book.
- recall@k: of the books that have a partner in the set, the share with a partner in their k
  nearest. Chance for one partner is about k / (n - 1).
- split a/b, h1/h2: half of a book is the query, the other halves of all books are the
  candidates; accuracy is how often its own other half is the nearest (both directions).
- rho_*: Spearman between pair distance and a nuisance difference, over all pairs unless said
  otherwise; p from a Mantel permutation of the book labels.
- top-5 make-up and hubness (skew of the 5-nearest in-degree; share of books in no top 5).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, skew

from eval.blocks import RESULTS, Block, load_block, load_testbed
from eval.pairs import ORDER, Pair, build_pairs

K_NEIGHBOURS = 5


def frac_negatives_farther(d_pos: np.ndarray, d_neg: np.ndarray) -> np.ndarray:
    """For each positive distance, the share of negatives that are farther (ties count half)."""
    neg = np.sort(d_neg)
    lo = np.searchsorted(neg, d_pos, side="left")
    hi = np.searchsorted(neg, d_pos, side="right")
    return 1.0 - (lo + hi) / 2.0 / len(neg)


def boot_mean(v: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float]:
    """95% percentile bootstrap interval of the mean of v."""
    if len(v) < 2:
        return (np.nan, np.nan)
    idx = rng.integers(0, len(v), size=(n_boot, len(v)))
    lo, hi = np.percentile(v[idx].mean(1), [2.5, 97.5])
    return float(lo), float(hi)


def neighbour_ranks(D: np.ndarray) -> np.ndarray:
    """R[i, j] = number of other books closer to i than j is (ties count half); R[i, i] = -1."""
    n = len(D)
    R = np.empty((n, n))
    for i in range(n):
        d = D[i].copy()
        d[i] = -np.inf
        R[i] = rankdata(d, method="average") - 2.0
    np.fill_diagonal(R, -1)
    return R


def score_pair_set(
    D: np.ndarray, R: np.ndarray, pairs: list[tuple[int, int]], d_neg: np.ndarray
) -> tuple[dict, np.ndarray]:
    """Scores for one pair set, and the per-pair share of negatives that are farther."""
    n = len(D)
    if not pairs:
        return {"n_pairs": 0}, np.array([])
    ii = np.array([p[0] for p in pairs])
    jj = np.array([p[1] for p in pairs])
    per_pair = frac_negatives_farther(D[ii, jj], d_neg)
    ranks = np.concatenate([R[ii, jj], R[jj, ii]])
    partners: dict[int, list[int]] = {}
    for i, j in pairs:
        partners.setdefault(i, []).append(j)
        partners.setdefault(j, []).append(i)
    best = np.array([min(R[a, p] for p in ps) for a, ps in partners.items()])
    out = {
        "n_pairs": len(pairs),
        "n_anchors": len(partners),
        "auc": float(per_pair.mean()),
        "pct_rank": float(ranks.mean() / (n - 2)),
        "recall@1": float((best < 1).mean()),
        "recall@5": float((best < 5).mean()),
        "median_dist": float(np.median(D[ii, jj])),
    }
    return out, per_pair


def split_retrieval(S: np.ndarray | None) -> tuple[float, float]:
    """Accuracy and mean percentile rank of a book's own other half; S[i, j] = d(a_i, b_j)."""
    if S is None:
        return (np.nan, np.nan)
    n = len(S)
    own = np.diag(S)
    lower, ties = own[:, None] > S, own[:, None] == S
    r_rows = lower.sum(1) + 0.5 * (ties.sum(1) - 1)
    lower, ties = own[None, :] > S, own[None, :] == S
    r_cols = lower.sum(0) + 0.5 * (ties.sum(0) - 1)
    r = np.concatenate([r_rows, r_cols])
    return float((r < 1).mean()), float(r.mean() / (n - 1))


def mantel(
    D: np.ndarray, C: np.ndarray, mask: np.ndarray, rng: np.random.Generator, n_perm: int
) -> tuple[float, float]:
    """Spearman between D and C over the pairs in mask (upper triangle), with a permutation p."""
    iu = np.triu_indices(len(D), 1)
    m = mask[iu]
    if m.sum() < 10:
        return (np.nan, np.nan)
    x = rankdata(D[iu][m])
    rho = float(np.corrcoef(x, rankdata(C[iu][m]))[0, 1])
    hits = 0
    for _ in range(n_perm):
        p = rng.permutation(len(D))
        Cp, Mp = C[np.ix_(p, p)], mask[np.ix_(p, p)]
        mp = Mp[iu]
        r = np.corrcoef(rankdata(D[iu][mp]), rankdata(Cp[iu][mp]))[0, 1]
        hits += abs(r) >= abs(rho)
    return rho, (hits + 1) / (n_perm + 1)


def checks(
    block: Block, D: np.ndarray, R: np.ndarray, tb: pd.DataFrame, rng: np.random.Generator
) -> dict:
    """Split-half retrieval, nuisance correlations, neighbour make-up and hubness."""
    n = len(D)
    out: dict = {"block": block.name, "n_books": n, "input_level": block.meta.get("input_level")}
    for kind in ("ab", "h12"):
        acc, pr = split_retrieval(block.split_distances(kind))
        out[f"split_{kind}_acc"], out[f"split_{kind}_pct_rank"] = acc, pr
    t = tb.loc[block.keys]
    year = t["year"].to_numpy(float)
    dyear = np.abs(year[:, None] - year[None, :])
    logw = np.log(t["n_words"].to_numpy(float))
    dlen = np.abs(logw[:, None] - logw[None, :])
    author = t["author"].to_numpy()
    same_author = author[:, None] == author[None, :]
    en = (t["orig_language"] == "en").to_numpy()
    en2 = en[:, None] & en[None, :]
    everything = np.ones((n, n), bool)
    out["rho_year"], out["p_year"] = mantel(D, dyear, everything, rng, 199)
    out["rho_year_en"], out["p_year_en"] = mantel(D, dyear, en2, rng, 199)
    out["rho_year_en_diffauthor"], _ = mantel(D, dyear, en2 & ~same_author, rng, 0)
    out["rho_logwords"], out["p_logwords"] = mantel(D, dlen, everything, rng, 199)
    out["rho_logwords_diffauthor"], _ = mantel(D, dlen, ~same_author, rng, 0)

    top = (R >= 0) & (R < K_NEIGHBOURS)
    off = ~np.eye(n, dtype=bool)
    has_sib = (same_author & off).any(1)
    out["top5_same_author"] = float((top & same_author)[has_sib].sum() / top[has_sib].sum())
    out["chance_same_author"] = float((same_author & off)[has_sib].sum() / off[has_sib].sum())
    genres = [x.get("genre", set()) for x in t["tags"]]
    same_genre = np.array([[bool(a & b) for b in genres] for a in genres])
    has_g = np.array([bool(g) for g in genres])
    out["top5_same_genre"] = float((top & same_genre)[has_g].sum() / top[has_g].sum())
    out["chance_same_genre"] = float((same_genre & off)[has_g].sum() / off[has_g].sum())
    out["top5_abs_year_diff"] = float(dyear[top].mean())
    out["chance_abs_year_diff"] = float(dyear[off].mean())
    out["top5_abs_logwords_diff"] = float(dlen[top].mean())
    out["chance_abs_logwords_diff"] = float(dlen[off].mean())
    indeg = top.sum(0)
    out["hub_skew"] = float(skew(indeg))
    out["hub_share_in_no_top5"] = float((indeg == 0).mean())
    out["hub_max_indegree"] = int(indeg.max())
    out["hub_top_book"] = str(block.keys[indeg.argmax()])
    return out


def cross_table(
    blocks: list[Block], dists: list[np.ndarray], tb: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Spearman between the off-diagonal distances of every two blocks; all pairs, and
    different-author pairs only. Uses the books common to all blocks."""
    common = sorted(set.intersection(*(set(b.keys) for b in blocks)))
    author = tb.loc[common, "author"].to_numpy()
    iu = np.triu_indices(len(common), 1)
    diff = (author[:, None] != author[None, :])[iu]
    vecs = []
    for b, D in zip(blocks, dists, strict=True):
        pos = {k: i for i, k in enumerate(b.keys)}
        idx = np.array([pos[k] for k in common])
        vecs.append(D[np.ix_(idx, idx)][iu])
    names = [b.name for b in blocks]
    allp = np.corrcoef([rankdata(v) for v in vecs])
    difp = np.corrcoef([rankdata(v[diff]) for v in vecs])
    return (
        pd.DataFrame(np.atleast_2d(allp), index=names, columns=names),
        pd.DataFrame(np.atleast_2d(difp), index=names, columns=names),
    )


def score_blocks(
    blocks: list[Block],
    tb: pd.DataFrame,
    *,
    ref: str | None = None,
    n_boot: int = 2000,
    seed: int = 0,
) -> dict[str, pd.DataFrame]:
    """Everything score.py reports, as data frames: scores, pairs, checks, cross, cross_diff."""
    rng = np.random.default_rng(seed)
    score_rows, pair_rows, check_rows, dists = [], [], [], []
    per_pair_by_block: dict[str, dict[str, np.ndarray]] = {}
    for b in blocks:
        missing = set(b.keys) - set(tb.index)
        if missing:
            raise ValueError(f"{b.name}: keys not in the testbed: {sorted(missing)[:5]}")
        D = b.distances()
        D = (D + D.T) / 2
        np.fill_diagonal(D, 0.0)
        dists.append(D)
        R = neighbour_ranks(D)
        pos = {k: i for i, k in enumerate(b.keys)}
        sets = build_pairs(tb.loc[sorted(b.keys)])
        neg = np.array([(pos[a], pos[c]) for a, c in sets["negatives"]])
        d_neg = D[neg[:, 0], neg[:, 1]]
        per_pair_by_block[b.name] = {}
        for name in ORDER:
            pairs: list[Pair] = sets[name]
            idx = [(pos[a], pos[c]) for a, c in pairs]
            row, per_pair = score_pair_set(D, R, idx, d_neg)
            row = {"block": b.name, "set": name, "n_neg": len(d_neg), **row}
            if len(per_pair):
                row["auc_lo"], row["auc_hi"] = boot_mean(per_pair, rng, n_boot)
            score_rows.append(row)
            per_pair_by_block[b.name][name] = per_pair
            for (a, c), (i, j), v in zip(pairs, idx, per_pair, strict=True):
                pair_rows.append(
                    {
                        "block": b.name,
                        "set": name,
                        "a": a,
                        "b": c,
                        "dist": D[i, j],
                        "share_neg_farther": v,
                        "rank_b_from_a": R[i, j],
                        "rank_a_from_b": R[j, i],
                    }
                )
        check_rows.append(checks(b, D, R, tb, rng))
    scores = pd.DataFrame(score_rows)
    if ref is not None:
        scores[["dauc_vs_ref", "dauc_lo", "dauc_hi"]] = np.nan
        for r in scores.index:
            blk, name = scores.at[r, "block"], scores.at[r, "set"]
            mine = per_pair_by_block[blk][name]
            other = per_pair_by_block[ref][name]
            if blk != ref and len(mine) == len(other) and len(mine):
                d = mine - other
                lo, hi = boot_mean(d, rng, n_boot)
                scores.loc[r, ["dauc_vs_ref", "dauc_lo", "dauc_hi"]] = [d.mean(), lo, hi]
    cross, cross_diff = cross_table(blocks, dists, tb)
    return {
        "scores": scores,
        "pairs": pd.DataFrame(pair_rows),
        "checks": pd.DataFrame(check_rows),
        "cross": cross,
        "cross_diff": cross_diff,
    }


def md_table(df: pd.DataFrame, floatfmt: str = "{:.2f}") -> str:
    """A plain markdown table (no tabulate dependency)."""

    def cell(v: object) -> str:
        if isinstance(v, float | np.floating):
            return "" if np.isnan(v) else floatfmt.format(v)
        return str(v)

    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(cell(v) for v in row) + " |" for row in df.to_numpy(object)]
    return "\n".join(lines)


def two(c: pd.DataFrame, a: str, b: str, fmt: str) -> list[str]:
    """Format two columns of c into one, row by row."""
    return [fmt.format(x, y) for x, y in zip(c[a], c[b], strict=True)]


def render_markdown(res: dict[str, pd.DataFrame], title: str, ref: str | None) -> str:
    """The markdown report for one scoring run."""
    s = res["scores"]
    s = s[s["n_pairs"] > 0]
    names = list(dict.fromkeys(s["block"]))
    sets = [x for x in ORDER if x in set(s["set"])]
    n = s.drop_duplicates("set").set_index("set")["n_pairs"]
    head = {x: f"{x} (n={int(n[x])})" for x in sets}
    out = [f"## {title}", ""]
    n_neg = int(s["n_neg"].iloc[0])
    out += [
        f"AUC that a labelled pair is closer than a negative pair ({n_neg} negatives; "
        "[95% bootstrap interval over the labelled pairs]). n = labelled pairs.",
        "",
    ]
    auc = pd.DataFrame({"block": names})
    for x in sets:
        sub = s[s["set"] == x].set_index("block")
        auc[head[x]] = [
            f"{sub.at[b, 'auc']:.2f} [{sub.at[b, 'auc_lo']:.2f}, {sub.at[b, 'auc_hi']:.2f}]"
            if b in sub.index and sub.at[b, "n_pairs"] > 1
            else (f"{sub.at[b, 'auc']:.2f}" if b in sub.index else "")
            for b in names
        ]
    out += [md_table(auc), ""]
    if ref is not None and "dauc_vs_ref" in s:
        out += [f"AUC difference from `{ref}` on the same pairs [paired bootstrap 95%].", ""]
        dd = pd.DataFrame({"block": [b for b in names if b != ref]})
        for x in sets:
            sub = s[s["set"] == x].set_index("block")
            dd[head[x]] = [
                f"{sub.at[b, 'dauc_vs_ref']:+.2f} [{sub.at[b, 'dauc_lo']:+.2f}, "
                f"{sub.at[b, 'dauc_hi']:+.2f}]"
                if b in sub.index and sub.at[b, "n_pairs"] > 1
                else ""
                for b in dd["block"]
            ]
        out += [md_table(dd), ""]
    out += ["Mean percentile rank of the partner (0 = nearest book) / recall@1 / recall@5.", ""]
    rk = pd.DataFrame({"block": names})
    for x in sets:
        sub = s[s["set"] == x].set_index("block")
        rk[head[x]] = [
            f"{sub.at[b, 'pct_rank']:.2f} / {sub.at[b, 'recall@1']:.2f} / "
            f"{sub.at[b, 'recall@5']:.2f}"
            if b in sub.index
            else ""
            for b in names
        ]
    out += [md_table(rk), ""]
    c = res["checks"]
    out += [
        "Split-half self-retrieval (accuracy; chance is 1/n), and Spearman of distance with "
        "|year difference| and |log word-count difference| (Mantel p in brackets; en = both "
        "books written in English; diff = different authors only).",
        "",
    ]
    t1 = pd.DataFrame(
        {
            "block": c["block"],
            "n": c["n_books"],
            "input": c["input_level"],
            "split a/b": c["split_ab_acc"],
            "split h1/h2": c["split_h12_acc"],
            "rho year": two(c, "rho_year", "p_year", "{:.2f} ({:.3f})"),
            "rho year en": two(c, "rho_year_en", "p_year_en", "{:.2f} ({:.3f})"),
            "rho year en diff": c["rho_year_en_diffauthor"],
            "rho logwords": two(c, "rho_logwords", "p_logwords", "{:.2f} ({:.3f})"),
            "rho logwords diff": c["rho_logwords_diffauthor"],
        }
    )
    out += [md_table(t1), ""]
    out += [
        "Top-5 neighbour make-up (observed / chance) and hubness (skew of the 5-nearest "
        "in-degree; share of books in nobody's top 5; largest in-degree and the book).",
        "",
    ]
    t2 = pd.DataFrame(
        {
            "block": c["block"],
            "same author": two(c, "top5_same_author", "chance_same_author", "{:.2f} / {:.2f}"),
            "same genre": two(c, "top5_same_genre", "chance_same_genre", "{:.2f} / {:.2f}"),
            "mean abs year diff": two(
                c, "top5_abs_year_diff", "chance_abs_year_diff", "{:.0f} / {:.0f}"
            ),
            "mean abs log-words diff": two(
                c, "top5_abs_logwords_diff", "chance_abs_logwords_diff", "{:.2f} / {:.2f}"
            ),
            "hub skew": c["hub_skew"],
            "in no top 5": c["hub_share_in_no_top5"],
            "max in-degree": two(c, "hub_max_indegree", "hub_top_book", "{} ({})"),
        }
    )
    out += [md_table(t2), ""]
    if len(names) > 1:
        for key, label in (("cross", "all pairs"), ("cross_diff", "different-author pairs only")):
            out += [f"Spearman between the pair distances of two blocks, {label}.", ""]
            out += [md_table(res[key].round(2).reset_index(names="block")), ""]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("blocks", nargs="+")
    ap.add_argument("--tag", required=True, help="prefix of the output files in results/")
    ap.add_argument("--title", default=None)
    ap.add_argument("--ref", default=None, help="block name to take AUC differences from")
    ap.add_argument("--exclude", nargs="*", default=[], help="book keys to leave out")
    ap.add_argument("--exclude-flagged", action="store_true", help="leave out meta['flagged']")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out", type=Path, default=RESULTS)
    args = ap.parse_args()

    tb = load_testbed()
    blocks = [load_block(p) for p in args.blocks]
    drop = set(args.exclude)
    if args.exclude_flagged:
        for b in blocks:
            drop |= set(b.meta.get("flagged", []))
    if drop:
        blocks = [b.subset(~np.isin(b.keys, sorted(drop))) for b in blocks]
    res = score_blocks(blocks, tb, ref=args.ref, n_boot=args.boot)
    args.out.mkdir(parents=True, exist_ok=True)
    res["scores"].to_csv(args.out / f"{args.tag}_scores.csv", index=False, float_format="%.4f")
    res["pairs"].to_csv(args.out / f"{args.tag}_pairs.csv", index=False, float_format="%.5f")
    res["checks"].to_csv(args.out / f"{args.tag}_checks.csv", index=False, float_format="%.4f")
    cross = pd.concat({"all": res["cross"], "diff_author": res["cross_diff"]})
    cross.to_csv(args.out / f"{args.tag}_cross.csv", float_format="%.4f")
    title = args.title or args.tag
    if drop:
        title += f" (without {', '.join(sorted(drop))})"
    md = render_markdown(res, title, args.ref)
    (args.out / f"{args.tag}.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
