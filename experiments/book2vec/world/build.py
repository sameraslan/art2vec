"""Book vectors from chunk embeddings: mean, centre across the corpus, optionally drop PCs.

    .venv/bin/python -m world.build EMB_NAME [EMB_NAME ...] [--prefix W1] [--take N]

For each data/emb/<EMB_NAME>/ writes blocks <prefix>_<EMB_NAME>_{raw,c,pc1,pc2}:

    raw   mean of the unit chunk embeddings
    c     ... minus the corpus mean, L2-normalised
    pc1   ... with the first principal direction of the centred book vectors projected out
    pc2   ... the first two

Split halves: a / b = every other sampled chunk, h1 / h2 = first / second half of the sample;
they are centred with the whole-book mean and directions. ``--take N`` uses only N evenly
spaced rows of each book's sample (suffix _n<N>).
"""

from __future__ import annotations

import argparse

import numpy as np
from eval.blocks import save_block

from world.common import EMB, book_keys, even_sample, remove_pcs

PARTS = ("full", "a", "b", "h1", "h2")


def load_emb(name: str, key: str) -> tuple[np.ndarray, np.ndarray]:
    return np.load(EMB / name / f"{key}.npy"), np.load(EMB / name / f"{key}.idx.npy")


def pooled(E: np.ndarray) -> dict[str, np.ndarray]:
    """Mean chunk embedding of the whole sample and of its four halves."""
    half = len(E) // 2
    rows = {"full": E, "a": E[0::2], "b": E[1::2], "h1": E[:half], "h2": E[half:]}
    return {p: r.mean(0) for p, r in rows.items()}


def book_matrices(name: str, keys: list[str], take: int = 0) -> dict[str, np.ndarray]:
    out: dict[str, list[np.ndarray]] = {p: [] for p in PARTS}
    for key in keys:
        E, _ = load_emb(name, key)
        if take:
            E = E[even_sample(len(E), take)]
        for p, v in pooled(E).items():
            out[p].append(v)
    return {p: np.stack(v) for p, v in out.items()}


def save_variants(base: str, keys: list[str], M: dict[str, np.ndarray], meta: dict) -> list[str]:
    names = []
    for suffix, k in (("raw", None), ("c", 0), ("pc1", 1), ("pc2", 2)):
        if k is None:
            Z = [M[p] for p in PARTS]
        else:
            Z = remove_pcs(M["full"], k, *(M[p] for p in PARTS[1:]))
        m = {**meta, "centred": k is not None, "pcs_removed": k or 0, "metric": "cosine"}
        name = f"{base}_{suffix}"
        save_block(name, keys, m, X=Z[0], X_a=Z[1], X_b=Z[2], X_h1=Z[3], X_h2=Z[4])
        names.append(name)
    return names


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("names", nargs="+")
    ap.add_argument("--prefix", default="W1")
    ap.add_argument("--take", type=int, default=0)
    ap.add_argument("--model", default="Qwen/Qwen3-Embedding-0.6B")
    args = ap.parse_args()
    keys = book_keys()
    for name in args.names:
        M = book_matrices(name, keys, args.take)
        meta = {
            "what": f"mean of {args.take or 'all sampled'} chunk embeddings ({name})",
            "input_level": "ordered text",
            "model": args.model,
            "emb": name,
            "flagged": [],
        }
        base = f"{args.prefix}_{name}" + (f"_n{args.take}" if args.take else "")
        print(" ".join(save_variants(base, keys, M, meta)))


if __name__ == "__main__":
    main()
