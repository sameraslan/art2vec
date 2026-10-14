"""How many chunks does a World book vector need?

    .venv/bin/python -m world.convergence --pick           # print the 12 books to embed fully
    .venv/bin/python -m world.convergence [--emb qwen_maskB]

Twelve long books have every chunk embedded (data/emb/<emb>_all). For k = 5, 10, 20, 40 chunks
(evenly spaced with a random phase, 5 draws) the book vector is compared with the all-chunk
vector: cosine before and after centring on the corpus mean, Spearman of its distances to the
other 86 books (their vectors come from the usual 40-chunk sample), overlap of the five
nearest neighbours, and whether the nearest neighbour is the same. Writes
results/world_convergence.md.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS
from eval.score import md_table
from scipy.stats import spearmanr

from world.build import book_matrices, load_emb
from world.common import CHUNKS, book_keys, unit

N_BOOKS = 12
MIN_CHUNKS = 150
SIZES = (5, 10, 20, 40, 80)


def pick() -> list[str]:
    """The 12 books with the fewest chunks among those with at least MIN_CHUNKS."""
    n = {k: sum(1 for _ in (CHUNKS / "maskB" / f"{k}.jsonl").open()) for k in book_keys()}
    long = sorted((v, k) for k, v in n.items() if v >= MIN_CHUNKS)
    return [k for _, k in long[:N_BOOKS]]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--emb", default="qwen_maskB")
    ap.add_argument("--pick", action="store_true")
    args = ap.parse_args()
    books = pick()
    if args.pick:
        print(" ".join(books))
        return
    keys = book_keys()
    corpus = book_matrices(args.emb, keys)["full"]
    mu = corpus.mean(0)
    C = unit(corpus - mu)
    rng = np.random.default_rng(0)
    rows = []
    for key in books:
        E, _ = load_emb(f"{args.emb}_all", key)
        i = keys.index(key)
        others = np.delete(np.arange(len(keys)), i)
        v_all = E.mean(0)
        d_all = 1 - C[others] @ unit(v_all - mu)
        top_all = set(np.argsort(d_all)[:5])
        for k in SIZES:
            for _ in range(5):
                step = len(E) / k
                idx = (rng.uniform(0, step) + step * np.arange(k)).astype(int)
                v = E[idx].mean(0)
                d = 1 - C[others] @ unit(v - mu)
                rows.append(
                    {
                        "key": key,
                        "n_chunks": len(E),
                        "k": k,
                        "cos_raw": float(unit(v) @ unit(v_all)),
                        "cos_centred": float(unit(v - mu) @ unit(v_all - mu)),
                        "rho_dist": spearmanr(d, d_all)[0],
                        "top5_overlap": len(top_all & set(np.argsort(d)[:5])) / 5,
                        "same_nearest": float(np.argmin(d) == np.argmin(d_all)),
                    }
                )
    d = pd.DataFrame(rows)
    d.to_csv(RESULTS / "world_convergence.csv", index=False, float_format="%.4f")
    s = d.groupby("k")[["cos_raw", "cos_centred", "rho_dist", "top5_overlap", "same_nearest"]]
    mean = s.mean().reset_index()
    worst = d.groupby("k")[["cos_centred", "top5_overlap"]].min().reset_index()
    mean["worst cos_centred"] = worst["cos_centred"]
    per_book = (
        d[d["k"] == 40]
        .groupby(["key", "n_chunks"])[["cos_centred", "rho_dist", "top5_overlap", "same_nearest"]]
        .mean()
        .reset_index()
    )
    md = "\n".join(
        [
            f"## World convergence ({args.emb}; 12 books with every chunk embedded)",
            "",
            "Means over 12 books x 5 draws. cos = cosine of the k-chunk book vector with the "
            "all-chunk vector; rho_dist = Spearman of the distances to the other 86 books.",
            "",
            md_table(mean, "{:.3f}"),
            "",
            "Per book at k = 40.",
            "",
            md_table(per_book, "{:.3f}"),
            "",
        ]
    )
    (RESULTS / "world_convergence.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
