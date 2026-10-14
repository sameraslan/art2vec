"""A small self-check of the harness on synthetic vectors.

    .venv/bin/python -m eval.test_harness        (or: .venv/bin/python -m pytest eval)

Builds vectors for the real testbed keys from planted factors: an "author" block where books
by one author share a centre, a "work" block where two translations of one work share a
centre, and a pure-noise block. The harness should find each planted structure where it was
put, and only there.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from eval.blocks import load_block, load_testbed, save_block
from eval.combine import combine
from eval.pairs import build_pairs
from eval.score import score_blocks, split_retrieval


def planted(labels: list[str], rng: np.random.Generator, d: int = 30, noise: float = 0.5):
    """One vector per label value plus noise; returns full, half-a and half-b vectors."""
    centres = {v: rng.normal(size=d) for v in sorted(set(labels))}
    base = np.array([centres[v] for v in labels]) + noise * rng.normal(size=(len(labels), d))
    return base, base + 0.2 * rng.normal(size=base.shape), base + 0.2 * rng.normal(size=base.shape)


def test_harness() -> None:
    rng = np.random.default_rng(1)
    tb = load_testbed()
    keys = list(tb.index)
    work = [
        next(iter(t.get("translation_pair", set()) | t.get("edition_pair", set())), k)
        for k, t in zip(keys, tb["tags"], strict=True)
    ]
    meta = {"what": "synthetic", "input_level": "book bag", "metric": "cosine"}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        Xa, a1, a2 = planted(list(tb["author"]), rng)
        Xw, w1, w2 = planted(work, rng)
        Xn = rng.normal(size=(len(keys), 30))
        save_block("syn_author", keys, meta, X=Xa, X_a=a1, X_b=a2, block_dir=tmp)
        save_block("syn_work", keys, meta, X=Xw, X_a=w1, X_b=w2, block_dir=tmp)
        save_block("syn_noise", keys, meta, X=Xn, block_dir=tmp)
        blocks = [load_block(tmp / f"{n}.npz") for n in ("syn_author", "syn_work", "syn_noise")]
        res = score_blocks(blocks, tb, ref="syn_noise", n_boot=200)
        both = combine(blocks[:2])

    s = res["scores"].set_index(["block", "set"])
    c = res["checks"].set_index("block")
    sets = build_pairs(tb)
    assert s.at[("syn_author", "same_author_unrelated"), "n_pairs"] == len(
        sets["same_author_unrelated"]
    )
    # planted structure is found where it was put
    assert s.at[("syn_author", "same_author_unrelated"), "auc"] > 0.95
    assert s.at[("syn_author", "translation_pair"), "auc"] > 0.95  # same author too
    assert s.at[("syn_work", "translation_pair"), "auc"] > 0.95
    assert s.at[("syn_work", "translation_pair"), "recall@1"] == 1.0
    assert s.at[("syn_work", "translation_pair"), "pct_rank"] < 0.02
    # and not where it was not
    assert 0.35 < s.at[("syn_work", "same_author_unrelated"), "auc"] < 0.65
    assert 0.3 < s.at[("syn_noise", "translation_pair"), "auc"] < 0.7
    lo, hi = s.loc[("syn_noise", "same_genre"), ["auc_lo", "auc_hi"]]
    assert lo < 0.5 < hi
    assert s.at[("syn_author", "same_author_unrelated"), "dauc_lo"] > 0
    # split halves, make-up, cross table
    assert c.at["syn_author", "split_ab_acc"] > 0.9
    assert np.isnan(c.at["syn_noise", "split_ab_acc"])
    assert c.at["syn_author", "top5_same_author"] > 3 * c.at["syn_author", "chance_same_author"]
    assert abs(c.at["syn_noise", "rho_year"]) < 0.15
    assert res["cross"].at["syn_author", "syn_noise"] < 0.1
    assert res["cross"].at["syn_author", "syn_author"] > 0.999
    assert res["cross_diff"].at["syn_author", "syn_work"] < 0.1
    # helpers
    acc, rank = split_retrieval(np.array([[0.0, 1.0], [1.0, 0.0]]))
    assert (acc, rank) == (1.0, 0.0)
    assert both["D"].shape == (len(keys), len(keys)) and "D_ab" in both
    print("harness ok:")
    print(res["scores"].query("n_pairs > 0")[["block", "set", "n_pairs", "auc"]].to_string())


if __name__ == "__main__":
    test_harness()
