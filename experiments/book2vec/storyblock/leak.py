"""How much of the Story block could be recall of famous books?

    .venv/bin/python -m storyblock.leak [--tag plain]

Three measurements on the digest embeddings (data/emb/digest), written to
results/story_leak.md:

(a) Retrieval: is a book's from-text digest nearer to its own title-only digest than to the
    title-only digests of the other books? Rank 1 = its own; the title-only digest of the
    same work in another translation or edition is left out of the candidates.
(b) Same-work pairs: cosine between the two independent from-text readings, against each
    reading's cosine with its own title-only digest, and the two title-only digests with each
    other.
(c) Spearman between from-text and title-only pair distances over the books that have both
    (the pair tests of the title-only blocks are scored by storyblock.subset).

Cosines are given raw and centred (the mean of all from-text and title-only vectors of the
field subtracted first; raw cosines between two summaries are all high).
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, load_testbed
from eval.pairs import build_pairs
from eval.score import md_table
from scipy.stats import spearmanr
from world.common import unit

from storyblock.build import digest_matrix
from storyblock.digests import FIELDS, ids, load

SAME_WORK = ("translation_pair", "edition_pair", "retelling")


def cosines(field: str, tag: str, centred: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Text-text, text-title and title-title cosine matrices, and which books have a title digest.

    Rows without a title-only digest give NaN columns.
    """
    T, M = digest_matrix("out", field, tag), digest_matrix("title_only", field, tag)
    have = np.array([load("title_only", b).get("memory") != "none" for b in ids()["bid"]])
    if centred:
        mu = np.vstack([T, M[have]]).mean(0)
        T, M = T - mu, M - mu
    T, M = unit(T), unit(M)
    TM, MM = T @ M.T, M @ M.T
    TM[:, ~have] = np.nan
    MM[~have] = np.nan
    MM[:, ~have] = np.nan
    return T @ T.T, TM, MM


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tag", default="plain", choices=("plain", "inst"))
    args = ap.parse_args()
    table = ids()
    keys = list(table["key"])
    pos = {k: i for i, k in enumerate(keys)}
    sets = build_pairs(load_testbed().loc[sorted(keys)])
    same_work = [(s, a, b) for s in SAME_WORK for a, b in sets[s]]
    partner: dict[int, set[int]] = {}
    for _, a, b in same_work:
        partner.setdefault(pos[a], set()).add(pos[b])
        partner.setdefault(pos[b], set()).add(pos[a])
    memory = [load("title_only", b).get("memory", "") for b in table["bid"]]
    recog = [load("out", b)["recognition"] for b in table["bid"]]
    out = ["## Story leak: from-text digests against title-only digests", ""]

    # (a) retrieval
    rows = []
    summary = []
    for field in FIELDS:
        for centred in (False, True):
            _, TM, _ = cosines(field, args.tag, centred)
            ranks, margins = [], []
            for i in range(len(keys)):
                if np.isnan(TM[i, i]):
                    ranks.append(np.nan)
                    margins.append(np.nan)
                    continue
                cand = [j for j in range(len(keys)) if j != i and j not in partner.get(i, ())]
                cand = [j for j in cand if not np.isnan(TM[i, j])]
                others = TM[i, cand]
                ranks.append(1 + int((others > TM[i, i]).sum()))
                margins.append(TM[i, i] - others.max())
            r = np.array(ranks)
            summary.append(
                {
                    "field": field,
                    "cosine": "centred" if centred else "raw",
                    "books": int(np.isfinite(r).sum()),
                    "own title digest is rank 1": int((r == 1).sum()),
                    "mean rank": np.nanmean(r),
                    "mean cos to own": float(np.nanmean(np.diag(TM))),
                    "mean cos to others": float(np.nanmean(TM[~np.eye(len(keys), dtype=bool)])),
                    "smallest margin over best other": float(np.nanmin(margins)),
                }
            )
            if field == "story" and centred:
                for i, (b, k) in enumerate(zip(table["bid"], keys, strict=True)):
                    rows.append(
                        {
                            "id": b,
                            "key": k,
                            "recognised": recog[i]["recognised"],
                            "at part": recog[i]["at_part"],
                            "title-only memory": memory[i],
                            "cos to own title digest": TM[i, i],
                            "best other": np.nanmax(
                                np.where(np.eye(len(keys))[i] > 0, np.nan, TM[i])
                            ),
                            "rank of own": ranks[i],
                        }
                    )
    out += ["### (a) Does the from-text digest retrieve its own title-only digest?", ""]
    out += [md_table(pd.DataFrame(summary)), ""]
    out += [
        "Per book, story field, centred cosine (best other includes the same work in "
        "another translation).",
        "",
        md_table(pd.DataFrame(rows)),
        "",
    ]

    # (b) same-work pairs
    rows = []
    for field in ("story", "characters", "world"):
        for centred in (False, True):
            TT, TM, MM = cosines(field, args.tag, centred)
            off = ~np.eye(len(keys), dtype=bool)
            for s, a, b in same_work:
                i, j = pos[a], pos[b]
                rows.append(
                    {
                        "field": field,
                        "cosine": "centred" if centred else "raw",
                        "set": s,
                        "pair": f"{a} ~ {b}",
                        "text a ~ text b": TT[i, j],
                        "text a ~ title a": TM[i, i],
                        "text b ~ title b": TM[j, j],
                        "text a ~ title b": TM[i, j],
                        "text b ~ title a": TM[j, i],
                        "title a ~ title b": MM[i, j],
                        "median text ~ text, all pairs": float(np.median(TT[off])),
                    }
                )
    out += [
        "### (b) Two independent readings of one work, against memory",
        "",
        "If `text a ~ text b` is above both `text ~ title` columns, the two readings agree with "
        "each other more than either agrees with what the model remembers from the title.",
        "",
        md_table(pd.DataFrame(rows)),
        "",
    ]
    b = pd.DataFrame(rows)
    wins = b.assign(
        win=b["text a ~ text b"] > b[["text a ~ title a", "text b ~ title b"]].max(axis=1)
    )
    tally = wins.groupby(["field", "cosine"])["win"].agg(["sum", "count"]).reset_index()
    tally.columns = ["field", "cosine", "pairs where the readings agree more", "pairs"]
    out += [md_table(tally), ""]

    # (c) how much of the from-text geometry does memory predict
    rows = []
    for field in FIELDS:
        TT, _, MM = cosines(field, args.tag, True)
        have = ~np.isnan(np.diag(MM))
        iu = np.triu_indices(int(have.sum()), 1)
        tt, mm = TT[np.ix_(have, have)][iu], MM[np.ix_(have, have)][iu]
        rows.append(
            {
                "field": field,
                "books": int(have.sum()),
                "pairs": len(tt),
                "Spearman, from-text vs title-only pair similarity": spearmanr(tt, mm)[0],
            }
        )
    out += [
        "### (c) From-text against title-only pair similarities",
        "",
        md_table(pd.DataFrame(rows)),
        "",
    ]
    md = "\n".join(out)
    (RESULTS / "story_leak.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
