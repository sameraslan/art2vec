"""How much of a block's pair distance is explained by another block (Prose by default)?

    .venv/bin/python -m world.vs_prose REF BLOCK [BLOCK ...] --tag TAG

For each block: Spearman with the reference block's pair distances over all pairs and over
different-author pairs only, and the pair-set AUCs before and after the reference distance is
regressed out (ranks, least squares, all pairs). Writes results/TAG.md.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, load_block, load_testbed
from eval.pairs import build_pairs
from eval.score import frac_negatives_farther, md_table
from scipy.stats import rankdata
from telling.vs_prose import residual

SETS = ("translation_pair", "same_author_unrelated", "series", "retelling", "same_genre")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ref")
    ap.add_argument("blocks", nargs="+")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    tb = load_testbed()
    sets = build_pairs(tb)
    P = load_block(args.ref)
    pos = {k: i for i, k in enumerate(P.keys)}
    iu = np.triu_indices(len(P.keys), 1)
    upper = {(i, j): n for n, (i, j) in enumerate(zip(*iu, strict=True))}
    where = {
        s: np.array([upper[tuple(sorted((pos[a], pos[b])))] for a, b in sets[s]])
        for s in (*SETS, "negatives")
    }
    author = tb.loc[P.keys, "author"].to_numpy()
    diff = (author[:, None] != author[None, :])[iu]
    dp = P.distances()[iu]

    def aucs(v: np.ndarray) -> dict[str, float]:
        neg = v[where["negatives"]]
        return {s: float(frac_negatives_farther(v[where[s]], neg).mean()) for s in SETS}

    rows = []
    for name in args.blocks:
        B = load_block(name)
        assert list(B.keys) == list(P.keys)
        d = B.distances()[iu]
        raw, res = aucs(d), aucs(residual(d, dp))
        row = {
            "block": name,
            f"Spearman with {args.ref}": np.corrcoef(rankdata(d), rankdata(dp))[0, 1],
            "... different authors only": np.corrcoef(rankdata(d[diff]), rankdata(dp[diff]))[0, 1],
        }
        for s in SETS:
            row[f"{s}: raw / ref regressed out"] = f"{raw[s]:.2f} / {res[s]:.2f}"
        rows.append(row)
    md = f"## Blocks against `{args.ref}`\n\n" + md_table(pd.DataFrame(rows)) + "\n"
    (RESULTS / f"{args.tag}.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
