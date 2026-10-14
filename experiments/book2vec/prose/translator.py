"""Author or translator: which does a block follow for translated books?

    .venv/bin/python -m prose.translator BLOCK [BLOCK ...] [--tag translator_test]

Three direct tests per block, all on whole-book distances.

1. Garnett set (six books she translated: three Dostoevsky, one Tolstoy, two Turgenev). For
   each, the nearest book that is not the same work is classed by what it shares with the
   anchor: author and translator, author only, translator only, neither.
2. Pair-level contest: is a same-author / different-translator pair (14 pairs) closer than a
   same-translator / different-author pair (11 pairs, all Garnett)? AUC over the 14 x 11
   comparisons; 0.5 = no preference, 1 = author always wins.
3. Is a second translation of the same work closer than another book by the same author?
   AUC of translation pairs (10) against same_author_unrelated pairs (52), and against
   original-English same-author pairs (33). Near 1 = two translations of one novel are closer
   than two novels by one author; near 0 = the translator moves a book further than a change
   of novel does.

Writes results/TAG.md and TAG.csv.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, load_block, load_testbed
from eval.pairs import build_pairs, share, translator_id
from eval.score import frac_negatives_farther, md_table


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("blocks", nargs="+")
    ap.add_argument("--tag", default="translator_test")
    args = ap.parse_args()
    tb = load_testbed()
    rows = tb.to_dict("index")
    sets = build_pairs(tb)
    garnett = [k for k in tb.index if translator_id(rows[k]) == "garnett"]
    detail, summary = [], []
    for name in args.blocks:
        b = load_block(name)
        D = b.distances()
        pos = {k: i for i, k in enumerate(b.keys)}

        def dist(pairs: list[tuple[str, str]], D: np.ndarray = D, pos: dict = pos) -> np.ndarray:
            return np.array([D[pos[x], pos[y]] for x, y in pairs])

        tally = {"author+translator": 0, "author only": 0, "translator only": 0, "neither": 0}
        for g in garnett:
            order = [b.keys[j] for j in np.argsort(D[pos[g]]) if b.keys[j] != g]
            order = [k for k in order if not share(rows[g], rows[k], "translation_pair")]
            near = order[0]
            same_a = rows[near]["author"] == rows[g]["author"]
            same_t = translator_id(rows[near]) == "garnett"
            kind = (
                "author+translator"
                if same_a and same_t
                else "author only"
                if same_a
                else "translator only"
                if same_t
                else "neither"
            )
            tally[kind] += 1
            cand_a = [k for k in order if rows[k]["author"] == rows[g]["author"]]
            cand_a = [k for k in cand_a if translator_id(rows[k]) != "garnett"]
            cand_t = [k for k in order if translator_id(rows[k]) == "garnett"]
            cand_t = [k for k in cand_t if rows[k]["author"] != rows[g]["author"]]
            detail.append(
                {
                    "block": name,
                    "anchor": g,
                    "nearest_not_same_work": near,
                    "shares": kind,
                    "rank_nearest_same_author_other_translator": min(
                        (order.index(k) + 1 for k in cand_a), default=np.nan
                    ),
                    "rank_nearest_garnett_other_author": min(
                        (order.index(k) + 1 for k in cand_t), default=np.nan
                    ),
                }
            )
        d_auth = dist(sets["same_author_diff_translator"])
        d_tran = dist(sets["same_translator_diff_author"])
        d_tp = dist(sets["translation_pair"])
        summary.append(
            {
                "block": name,
                "nearest: author+translator": tally["author+translator"],
                "author only": tally["author only"],
                "translator only": tally["translator only"],
                "neither": tally["neither"],
                "AUC author beats translator (14 vs 11)": frac_negatives_farther(
                    d_auth, d_tran
                ).mean(),
                "AUC translation pair closer than same-author pair (10 vs 52)": (
                    frac_negatives_farther(d_tp, dist(sets["same_author_unrelated"])).mean()
                ),
                "... than orig-English same-author pair (10 vs 33)": frac_negatives_farther(
                    d_tp, dist(sets["same_author_orig_en"])
                ).mean(),
                "median d translation pair / median d same-author": np.median(d_tp)
                / np.median(dist(sets["same_author_unrelated"])),
            }
        )
    s, d = pd.DataFrame(summary), pd.DataFrame(detail)
    d.to_csv(RESULTS / f"{args.tag}.csv", index=False)
    md = (
        f"## Author or translator ({len(garnett)} Garnett books)\n\n"
        + md_table(s)
        + "\n\nNearest book that is not the same work, per Garnett book (ranks count from 1).\n\n"
        + md_table(d, "{:.0f}")
        + "\n"
    )
    (RESULTS / f"{args.tag}.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
