"""Felt block from the reader's 24 word scores, and how the readers used the scale.

    .venv/bin/python -m felt.build

Blocks (24 books; the title-only ones 23):

    F_reader        scores z-scored per word across the books, cosine
    F_reader_raw    raw 0-3 scores, Euclidean
    FM_title        z-scored title-only scores (memory, no text), cosine

results/felt_reader.md: score distribution, agreement of two readings of one work, and
agreement of from-text with title-only scores.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, load_testbed, save_block
from eval.pairs import build_pairs
from eval.score import md_table
from scipy.stats import spearmanr
from storyblock.digests import FELT_WORDS, ids, load

SAME_WORK = ("translation_pair", "edition_pair", "retelling")
OTHER = ("series", "same_author_unrelated")


def felt_matrix(source: str) -> np.ndarray:
    """24 x 24 scores; NaN rows where the reader gave none."""
    rows = []
    for bid in ids()["bid"]:
        f = load(source, bid).get("felt")
        rows.append([f[w] for w in FELT_WORDS] if f else [np.nan] * len(FELT_WORDS))
    return np.array(rows, float)


def zs(X: np.ndarray) -> np.ndarray:
    sd = X.std(0)
    return (X - X.mean(0)) / np.where(sd > 0, sd, 1.0)


def corr_rows(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Pearson between every row of A and every row of B."""
    A = A - A.mean(1, keepdims=True)
    B = B - B.mean(1, keepdims=True)
    A /= np.maximum(np.linalg.norm(A, axis=1, keepdims=True), 1e-12)
    B /= np.maximum(np.linalg.norm(B, axis=1, keepdims=True), 1e-12)
    return A @ B.T


def main() -> None:
    table = ids()
    keys = list(table["key"])
    pos = {k: i for i, k in enumerate(keys)}
    F, M = felt_matrix("out"), felt_matrix("title_only")
    have = ~np.isnan(M).any(1)
    meta = {"input_level": "ordered text", "flagged": [], "words": list(FELT_WORDS)}
    save_block(
        "F_reader",
        keys,
        {**meta, "what": "reader felt scores, z per word", "metric": "cosine"},
        X=zs(F),
    )
    save_block(
        "F_reader_raw",
        keys,
        {**meta, "what": "reader felt scores, raw", "metric": "euclidean"},
        X=F,
    )
    save_block(
        "FM_title",
        list(np.array(keys)[have]),
        {**meta, "what": "title-only felt scores, z per word", "metric": "cosine"},
        X=zs(M[have]),
    )
    out = ["## Felt: the reader's 24 word scores", ""]

    dist = pd.DataFrame(
        {
            "source": ["from text (24 books)", "title only (23 books)"],
            **{
                f"share of {v}s": [float((v == F).mean()), float((M[have] == v).mean())]
                for v in range(4)
            },
            "mean": [F.mean(), M[have].mean()],
            "mean per-book sd": [F.std(1).mean(), M[have].std(1).mean()],
        }
    )
    out += ["### Is the scale used?", "", md_table(dist), ""]
    words = pd.DataFrame(
        {
            "word": FELT_WORDS,
            "mean": F.mean(0),
            "sd across books": F.std(0),
            "0": (F == 0).sum(0),
            "1": (F == 1).sum(0),
            "2": (F == 2).sum(0),
            "3": (F == 3).sum(0),
            "Spearman text vs title (23 books)": [
                spearmanr(F[have, j], M[have, j])[0] for j in range(len(FELT_WORDS))
            ],
        }
    )
    out += ["Per word, from text.", "", md_table(words.sort_values("mean", ascending=False)), ""]

    sets = build_pairs(load_testbed().loc[sorted(keys)])
    Craw, Cz = corr_rows(F.copy(), F.copy()), corr_rows(zs(F), zs(F))
    off = ~np.eye(len(keys), dtype=bool)
    neg = np.array([(pos[a], pos[b]) for a, b in sets["negatives"]])
    rows = []
    for s in (*SAME_WORK, *OTHER):
        for a, b in sets[s]:
            i, j = pos[a], pos[b]
            rows.append(
                {
                    "set": s,
                    "pair": f"{a} ~ {b}",
                    "Pearson raw": Craw[i, j],
                    "Spearman raw": spearmanr(F[i], F[j])[0],
                    "Pearson z": Cz[i, j],
                    "mean abs diff": float(np.abs(F[i] - F[j]).mean()),
                    "exact agreement": float((F[i] == F[j]).mean()),
                    "rank of b from a (z)": 1 + int((Cz[i][off[i]] > Cz[i, j]).sum()),
                    "rank of a from b (z)": 1 + int((Cz[j][off[j]] > Cz[i, j]).sum()),
                }
            )
    base = {
        "set": "negatives (median)",
        "pair": f"{len(neg)} pairs",
        "Pearson raw": float(np.median(Craw[neg[:, 0], neg[:, 1]])),
        "Pearson z": float(np.median(Cz[neg[:, 0], neg[:, 1]])),
        "mean abs diff": float(np.median(np.abs(F[neg[:, 0]] - F[neg[:, 1]]).mean(1))),
        "exact agreement": float(np.median((F[neg[:, 0]] == F[neg[:, 1]]).mean(1))),
    }
    out += [
        "### Two independent readings of one work (and series / same-author pairs)",
        "",
        "Pearson z = correlation after each word is z-scored across the 24 books, which takes "
        "out the profile all books share. Ranks are among the 23 other books (1 = nearest).",
        "",
        md_table(pd.DataFrame([*rows, base])),
        "",
    ]

    C = corr_rows(zs(F[have]), zs(M[have]))
    kk = np.array(keys)[have]
    rows = []
    for i, k in enumerate(kk):
        rows.append(
            {
                "key": k,
                "Pearson raw": float(np.corrcoef(F[have][i], M[have][i])[0, 1]),
                "Pearson z": C[i, i],
                "rank of own title vector (z)": 1 + int((np.delete(C[i], i) > C[i, i]).sum()),
                "mean abs diff": float(np.abs(F[have][i] - M[have][i]).mean()),
                "exact agreement": float((F[have][i] == M[have][i]).mean()),
            }
        )
    d = pd.DataFrame(rows)
    mean_row = {"key": "MEAN", **d.drop(columns="key").mean().to_dict()}
    out += [
        "### From-text felt against title-only felt",
        "",
        md_table(pd.concat([d, pd.DataFrame([mean_row])])),
        "",
        f"Own title-only vector is the nearest of the 23 for "
        f"{int((d['rank of own title vector (z)'] == 1).sum())} of {len(d)} books (same-work "
        "partners are among the candidates).",
        "",
    ]
    md = "\n".join(out)
    (RESULTS / "felt_reader.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
