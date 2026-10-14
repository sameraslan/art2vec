"""Is a Telling block more than Prose again?

    .venv/bin/python -m telling.vs_prose PROSE_BLOCK TELLING_BLOCK [TELLING_BLOCK ...]

For each Telling block: Spearman with the Prose block's pair distances (all pairs, and
different-author pairs only), then the pair-set AUCs of the Telling block before and after
the Prose distance is regressed out of it (ranks, least squares, over all pairs), and the
same for Prose with Telling regressed out. A block that only repeats the other loses its
AUCs when the other is removed. Writes results/telling_vs_prose.md and .csv.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, load_block, load_testbed
from eval.pairs import build_pairs
from eval.score import frac_negatives_farther, md_table
from scipy.stats import rankdata

SETS = ("translation_pair", "same_author_unrelated", "series", "retelling", "same_genre")


def residual(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Ranks of y with the least-squares fit on the ranks of x taken out."""
    ry, rx = rankdata(y), rankdata(x)
    slope = np.cov(ry, rx)[0, 1] / rx.var(ddof=1)
    return ry - slope * rx


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("prose")
    ap.add_argument("telling", nargs="+")
    args = ap.parse_args()
    tb = load_testbed()
    sets = build_pairs(tb)
    P = load_block(args.prose)
    pos = {k: i for i, k in enumerate(P.keys)}
    iu = np.triu_indices(len(P.keys), 1)
    upper = {(i, j): n for n, (i, j) in enumerate(zip(*iu, strict=True))}
    where = {
        name: np.array([upper[tuple(sorted((pos[a], pos[b])))] for a, b in sets[name]])
        for name in (*SETS, "negatives")
    }
    author = tb.loc[P.keys, "author"].to_numpy()
    diff = (author[:, None] != author[None, :])[iu]

    def aucs(v: np.ndarray) -> dict[str, float]:
        neg = v[where["negatives"]]
        return {s: float(frac_negatives_farther(v[where[s]], neg).mean()) for s in SETS}

    dp = P.distances()[iu]
    rows = []
    for name in args.telling:
        T = load_block(name)
        assert list(T.keys) == list(P.keys)
        dt = T.distances()[iu]
        rho = np.corrcoef(rankdata(dt), rankdata(dp))[0, 1]
        rho_diff = np.corrcoef(rankdata(dt[diff]), rankdata(dp[diff]))[0, 1]
        for label, v in (
            (name, dt),
            (f"{name} minus {args.prose}", residual(dt, dp)),
            (args.prose, dp),
            (f"{args.prose} minus {name}", residual(dp, dt)),
        ):
            rows.append({"distance": label, "rho": rho, "rho diff-author": rho_diff, **aucs(v)})
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "telling_vs_prose.csv", index=False, float_format="%.4f")
    n = {s: len(where[s]) for s in SETS}
    df = df.rename(columns={s: f"AUC {s} (n={n[s]})" for s in SETS})
    md = (
        "## Telling against Prose\n\nrho = Spearman between the Telling and the Prose pair "
        f"distances ({len(dp)} pairs; {int(diff.sum())} with different authors). "
        '"A minus B" = A with B regressed out.\n\n' + md_table(df) + "\n"
    )
    (RESULTS / "telling_vs_prose.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
