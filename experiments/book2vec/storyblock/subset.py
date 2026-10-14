"""Score blocks on the 24-book reader subset and list every labelled pair's rank.

    .venv/bin/python -m storyblock.subset BLOCK [BLOCK ...] --tag TAG [--title T] [--drop KEY ..]

Blocks over all 87 books are cut down to the subset first, so ranks and negatives are counted
among the subset's books only. Writes results/TAG.md (the harness tables followed by the pair
table) and the harness CSVs. In the pair table a cell is "rank of b from a / rank of a from b"
(1 = nearest of the other books), then the share of negative pairs that are farther.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, Block, load_block, load_testbed
from eval.pairs import build_pairs
from eval.score import md_table, render_markdown, score_blocks

from storyblock.digests import ids

PAIR_SETS = ("translation_pair", "edition_pair", "retelling", "series", "same_author_unrelated")


def subset_blocks(names: list[str], drop: list[str] | None = None) -> list[Block]:
    keep = set(ids()["key"]) - set(drop or [])
    out = []
    for n in names:
        b = load_block(n)
        out.append(b.subset(np.isin(b.keys, sorted(keep))))
    return out


def pair_table(pairs: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    """One row per labelled pair, one column per block."""
    p = pairs[pairs["set"].isin(PAIR_SETS)]
    rows = []
    for (s, a, b), g in p.groupby(["set", "a", "b"], sort=False):
        g = g.set_index("block")
        row = {"set": s, "pair": f"{a} ~ {b}"}
        for n in names:
            if n in g.index:
                r = g.loc[n]
                row[n] = (
                    f"{r['rank_b_from_a'] + 1:.0f} / {r['rank_a_from_b'] + 1:.0f} "
                    f"({r['share_neg_farther']:.2f})"
                )
            else:
                row[n] = ""
        rows.append(row)
    out = pd.DataFrame(rows)
    out["set"] = pd.Categorical(out["set"], PAIR_SETS, ordered=True)
    return out.sort_values(["set", "pair"]).astype({"set": str})


def subset_pair_counts() -> pd.DataFrame:
    tb = load_testbed()
    sets = build_pairs(tb.loc[sorted(ids()["key"])])
    return pd.DataFrame(
        [
            {
                "set": k,
                "n": len(v),
                "pairs": "; ".join(f"{a}~{b}" for a, b in v) if len(v) < 12 else "",
            }
            for k, v in sets.items()
        ]
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("blocks", nargs="+")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--title", default=None)
    ap.add_argument("--drop", nargs="*", default=[])
    args = ap.parse_args()
    blocks = subset_blocks(args.blocks, args.drop)
    res = score_blocks(blocks, load_testbed())
    names = [b.name for b in blocks]
    md = render_markdown(res, args.title or args.tag, None)
    md += "\n\nEvery labelled pair: rank of b from a / rank of a from b (1 = nearest), and in "
    md += "brackets the share of negative pairs that are farther apart.\n\n"
    md += md_table(pair_table(res["pairs"], names)) + "\n"
    (RESULTS / f"{args.tag}.md").write_text(md)
    for part in ("scores", "pairs", "checks"):
        res[part].to_csv(RESULTS / f"{args.tag}_{part}.csv", index=False, float_format="%.4f")
    cross = pd.concat({"all": res["cross"], "diff_author": res["cross_diff"]})
    cross.to_csv(RESULTS / f"{args.tag}_cross.csv", float_format="%.4f")
    print(md)


if __name__ == "__main__":
    main()
