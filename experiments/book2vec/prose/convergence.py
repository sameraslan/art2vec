"""How many words does a Prose vector need?

    .venv/bin/python -m prose.convergence [--seeds 5]

For each book with at least MIN_WORDS words, draws random non-contiguous samples of 1k ... 50k
words: the book is cut into runs of whole sentences of about 100 words, and runs are drawn at
random without replacement. From each sample the P1 (500 most frequent words, names removed),
P2 (1,000 tag trigrams) and P3 (rhythm) vectors are built, z-scored across the sampled books,
and combined as in P4. Reported per size, averaged over seeds:

    rho_full      Spearman between sample distances and the whole-book distances
    auc_author    AUC, same_author_unrelated pairs against negatives (eval.score definitions)
    auc_transl    AUC, translation pairs against negatives
    self_acc      a second, disjoint sample of the same size is drawn from every book; how
                  often a book's first sample has its own second sample as nearest (sizes up
                  to 20k, so that two disjoint samples always fit)

The vocabulary (which words, which trigrams) is the one chosen on the whole corpus.
Writes results/prose_convergence.csv and .md.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, cross_distance, load_block, load_testbed
from eval.pairs import build_pairs
from eval.score import frac_negatives_farther, md_table, split_retrieval
from scipy.stats import spearmanr

from prose.features import (
    N_TAGS,
    rhythm_features,
    trigram_codes,
    variant_mask,
    word_counts,
    zscore,
)
from prose.tokens import Vocab, load_book

SIZES = (1000, 2000, 5000, 10000, 20000, 50000)
MIN_WORDS = 50000
RUN = 100
P1, P2, P3 = "P1_mfw500_all_noprop_nocull", "P2_tag3_1000", "P3_rhythm"
METRIC = {"P1": "cosine", "P2": "cosine", "P3": "euclidean"}


def sentence_runs(book: dict[str, np.ndarray]) -> np.ndarray:
    """Run id per token: whole sentences grouped into runs of about RUN words."""
    words_before = np.cumsum(book["is_word"]) - book["is_word"]
    first = np.r_[True, book["sent"][1:] != book["sent"][:-1]]
    start_words = words_before[first]
    run_of_sent = start_words // RUN
    _, run_of_sent = np.unique(run_of_sent, return_inverse=True)
    return run_of_sent[np.cumsum(first) - 1]


def median_scaled(D: np.ndarray, ref: np.ndarray | None = None) -> np.ndarray:
    ref = D if ref is None else ref
    return D / np.median(ref[np.triu_indices(len(ref), 1)])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seeds", type=int, default=5)
    args = ap.parse_args()

    tb = load_testbed()
    keys = [k for k in tb.index if tb.at[k, "n_words"] >= MIN_WORDS]
    n = len(keys)
    b1, b2, b3 = load_block(P1), load_block(P2), load_block(P3)
    words = {w: i for i, w in enumerate(b1.meta["words"])}
    tags = Vocab()
    tri_codes = []
    for name in b2.meta["trigrams"]:
        a, b, c = tags.encode(np.array(name.split(" ")))
        tri_codes.append(a * N_TAGS * N_TAGS + b * N_TAGS + c)
    tri_index = np.full(N_TAGS**3, -1)
    tri_index[tri_codes] = np.arange(len(tri_codes))
    dims = {"P1": len(words), "P2": len(tri_codes), "P3": b3.X.shape[1]}

    shape = (args.seeds, len(SIZES), 2, n)
    feats = {p: np.full((*shape, d), np.nan) for p, d in dims.items()}
    for i, key in enumerate(keys):
        book = load_book(key)
        vocab_of_type = np.array([words.get(t, -1) for t in book["types"]])
        tag_ids = tags.lookup(book["tag_names"])
        tag_ids[tag_ids < 0] = N_TAGS - 1
        vmask = variant_mask(book, "all_noprop")
        runs = sentence_runs(book)
        n_runs = int(runs.max()) + 1
        for seed in range(args.seeds):
            rng = np.random.default_rng([seed, i])
            order = rng.permutation(n_runs)
            for s, size in enumerate(SIZES):
                k = size // RUN
                for half in range(2 if 2 * k <= n_runs else 1):
                    chosen = np.zeros(n_runs, bool)
                    chosen[order[half * k : (half + 1) * k]] = True
                    m = chosen[runs]
                    counts, total = word_counts(book, m & vmask, vocab_of_type, dims["P1"])
                    feats["P1"][seed, s, half, i] = counts / total
                    idx = tri_index[trigram_codes(book, m, tag_ids)]
                    feats["P2"][seed, s, half, i] = np.bincount(
                        idx[idx >= 0], minlength=dims["P2"]
                    ) / len(idx)
                    feats["P3"][seed, s, half, i] = rhythm_features(book, m)
        print(f"{i + 1}/{n} {key}", flush=True)

    keep = np.isin(b1.keys, keys)
    full = {"P1": b1.subset(keep), "P2": b2.subset(keep), "P3": b3.subset(keep)}
    assert list(full["P1"].keys) == keys
    D_full = {p: median_scaled(b.distances()) for p, b in full.items()}
    D_full["P4"] = sum(D_full.values()) / 3
    sets = build_pairs(tb.loc[keys])
    pos = {k: i for i, k in enumerate(keys)}
    ix = {
        name: np.array([(pos[a], pos[b]) for a, b in sets[name]])
        for name in ("same_author_unrelated", "translation_pair", "negatives")
    }
    iu = np.triu_indices(n, 1)

    def auc(D: np.ndarray, name: str) -> float:
        d_pos = D[ix[name][:, 0], ix[name][:, 1]]
        d_neg = D[ix["negatives"][:, 0], ix["negatives"][:, 1]]
        return float(frac_negatives_farther(d_pos, d_neg).mean())

    rows = []
    for s, size in enumerate(SIZES):
        for seed in range(args.seeds):
            D, S = {}, {}
            for p in ("P1", "P2", "P3"):
                X = feats[p][seed, s, 0]
                Z = zscore(X)
                D[p] = cross_distance(Z, Z, METRIC[p])
                Y = feats[p][seed, s, 1]
                if not np.isnan(Y).any():
                    S[p] = cross_distance(Z, zscore(Y, X), METRIC[p])
            scaled = {p: median_scaled(d) for p, d in D.items()}
            D["P4"] = sum(scaled.values()) / 3
            if len(S) == 3:
                S["P4"] = sum(median_scaled(S[p], D[p]) for p in S) / 3
            for p in ("P1", "P2", "P3", "P4"):
                rows.append(
                    {
                        "block": p,
                        "words": size,
                        "seed": seed,
                        "rho_full": spearmanr(D[p][iu], D_full[p][iu])[0],
                        "auc_author": auc(D[p], "same_author_unrelated"),
                        "auc_transl": auc(D[p], "translation_pair"),
                        "self_acc": split_retrieval(S[p])[0] if p in S else np.nan,
                    }
                )
    for p in ("P1", "P2", "P3", "P4"):
        rows.append(
            {
                "block": p,
                "words": 0,
                "seed": -1,
                "rho_full": 1.0,
                "auc_author": auc(D_full[p], "same_author_unrelated"),
                "auc_transl": auc(D_full[p], "translation_pair"),
                "self_acc": np.nan,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "prose_convergence.csv", index=False, float_format="%.4f")
    g = df.groupby(["block", "words"])
    mean, sd = g.mean(numeric_only=True), g.std(numeric_only=True)
    table = pd.DataFrame(
        {
            "block": [b for b, _ in mean.index],
            "words": ["whole book" if w == 0 else f"{w:,}" for _, w in mean.index],
        }
    )
    for col in ("rho_full", "auc_author", "auc_transl", "self_acc"):
        table[col] = [
            "" if np.isnan(m) else (f"{m:.3f}" if np.isnan(e) else f"{m:.3f} ± {e:.3f}")
            for m, e in zip(mean[col], sd[col], strict=True)
        ]
    table = table.iloc[
        sorted(range(len(table)), key=lambda r: (mean.index[r][0], mean.index[r][1] or 10**9))
    ]
    head = (
        f"## Prose convergence\n\n{n} books with at least {MIN_WORDS:,} words; "
        f"{len(ix['same_author_unrelated'])} same-author pairs, "
        f"{len(ix['translation_pair'])} translation pairs, {len(ix['negatives'])} negatives; "
        f"mean ± sd over {args.seeds} random samples. P1 = {P1}, P2 = {P2}, P3 = {P3}, "
        "P4 = mean of the three median-scaled distances.\n\n"
    )
    md = head + md_table(table) + "\n"
    (RESULTS / "prose_convergence.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
