"""Combine blocks by averaging their standardised distances.

    .venv/bin/python -m eval.combine NEW_NAME BLOCK [BLOCK ...] [--weights W ...] [--scale sd]

Each block's distance matrix is divided by the median of its off-diagonal entries (so no block
dominates by scale), then the matrices are averaged. With --scale sd the divisor is the
standard deviation of the off-diagonal entries instead, so every block contributes the same
variance; use it when one block's distances are all nearly equal (it would otherwise add a
constant and no ordering). Split-half matrices (a/b, h1/h2) are
scaled by the same constant and averaged when every input has them. The result is a D block.
"""

from __future__ import annotations

import argparse

import numpy as np

from eval.blocks import Block, load_block, save_block

LEVEL_RANK = {"book bag": 0, "page bag": 1, "ordered text": 2}


def combine(
    blocks: list[Block], weights: list[float] | None = None, scale: str = "median"
) -> dict[str, np.ndarray]:
    """Weighted mean of scaled distance matrices: D, and D_ab / D_h12 when possible."""
    keys = blocks[0].keys
    if any(list(b.keys) != list(keys) for b in blocks):
        raise ValueError("blocks must have the same keys in the same order")
    w = np.ones(len(blocks)) if weights is None else np.asarray(weights, float)
    w = w / w.sum()
    iu = np.triu_indices(len(keys), 1)
    stat = np.median if scale == "median" else np.std
    scales = [stat(b.distances()[iu]) for b in blocks]
    out = {"D": sum(wi * b.distances() / s for wi, b, s in zip(w, blocks, scales, strict=True))}
    out["D"] = (out["D"] + out["D"].T) / 2
    np.fill_diagonal(out["D"], 0.0)
    for kind in ("ab", "h12"):
        parts = [b.split_distances(kind) for b in blocks]
        if all(p is not None for p in parts):
            out[f"D_{kind}"] = sum(wi * p / s for wi, p, s in zip(w, parts, scales, strict=True))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("name")
    ap.add_argument("blocks", nargs="+")
    ap.add_argument("--weights", nargs="*", type=float, default=None)
    ap.add_argument("--scale", choices=("median", "sd"), default="median")
    args = ap.parse_args()
    blocks = [load_block(b) for b in args.blocks]
    arrays = combine(blocks, args.weights, args.scale)
    level = max((b.meta["input_level"] for b in blocks), key=LEVEL_RANK.__getitem__)
    flagged = sorted({k for b in blocks for k in b.meta.get("flagged", [])})
    meta = {
        "what": f"mean of {args.scale}-scaled distances of " + ", ".join(b.name for b in blocks),
        "input_level": level,
        "metric": "precomputed",
        "parts": [b.name for b in blocks],
        "weights": args.weights,
        "scale": args.scale,
        "flagged": flagged,
    }
    print(save_block(args.name, blocks[0].keys, meta, **arrays))


if __name__ == "__main__":
    main()
