"""Felt without a reader: project passage embeddings onto the 24 felt words.

    .venv/bin/python -m felt.project [--emb qwen_maskB]

Each sampled chunk embedding is compared (cosine) with the embedding of a definition of each
felt word ("A passage that feels bleak."; or the bare word behind a retrieval instruction),
the scores are averaged per book, and each word is z-scored across the 87 books. Blocks
F_proj_{plain,inst}[_n20] (87 books, cosine). results/felt_projection.md compares the
projection with the reader's scores on the 24 books: Spearman per word (across books) and per
book (across words).
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from eval.blocks import RESULTS, save_block
from eval.score import md_table
from scipy.stats import spearmanr
from storyblock.digests import FELT_WORDS, ids
from world.build import load_emb
from world.common import EMB, book_keys, even_sample

from felt.build import felt_matrix, zs

PARTS = ("full", "a", "b", "h1", "h2")


def project(emb: str, words: np.ndarray, keys: list[str], take: int) -> dict[str, np.ndarray]:
    """Mean chunk-to-word cosine per book: whole sample and its halves."""
    out: dict[str, list[np.ndarray]] = {p: [] for p in PARTS}
    for key in keys:
        E, _ = load_emb(emb, key)
        if take:
            E = E[even_sample(len(E), take)]
        S = E @ words.T
        half = len(S) // 2
        parts = {"full": S, "a": S[0::2], "b": S[1::2], "h1": S[:half], "h2": S[half:]}
        for p, v in parts.items():
            out[p].append(v.mean(0))
    return {p: np.stack(v) for p, v in out.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--emb", default="qwen_maskB")
    args = ap.parse_args()
    keys = book_keys()
    sub = [keys.index(k) for k in ids()["key"]]
    F = felt_matrix("out")
    out = ["## Felt from passage embeddings, against the reader", ""]
    summary, per_word = [], {"word": FELT_WORDS, "reader sd": F.std(0)}
    for tag in ("plain", "inst"):
        words = np.load(EMB / "digest" / f"felt_words_{tag}.npy")
        for take in (0, 20):
            P = project(args.emb, words, keys, take)
            mu, sd = P["full"].mean(0), P["full"].std(0)
            Z = {p: (v - mu) / sd for p, v in P.items()}
            name = f"F_proj_{tag}" + (f"_n{take}" if take else "")
            meta = {
                "what": f"mean cosine of {take or 40} {args.emb} chunk embeddings to 24 felt-word "
                f"definitions ({tag}), z per word over 87 books",
                "input_level": "ordered text",
                "metric": "cosine",
                "flagged": [],
            }
            save_block(
                name, keys, meta, X=Z["full"], X_a=Z["a"], X_b=Z["b"], X_h1=Z["h1"], X_h2=Z["h2"]
            )
            Zs = Z["full"][sub]
            Zs24 = zs(Zs)
            by_word = np.array([spearmanr(Zs[:, j], F[:, j])[0] for j in range(F.shape[1])])
            by_book_raw = np.array([spearmanr(Zs[i], F[i])[0] for i in range(len(sub))])
            Fz = zs(F)
            by_book_z = np.array([spearmanr(Zs24[i], Fz[i])[0] for i in range(len(sub))])
            # chance level: the same per-book correlation against another book's reader scores
            shuffled = np.array(
                [
                    spearmanr(Zs24[i], Fz[j])[0]
                    for i in range(len(sub))
                    for j in range(len(sub))
                    if i != j
                ]
            )
            summary.append(
                {
                    "projection": name,
                    "per word: mean Spearman over 24 words": np.nanmean(by_word),
                    "words with Spearman > 0.4": int((by_word > 0.4).sum()),
                    "per book: mean Spearman, raw reader scores": by_book_raw.mean(),
                    "per book: mean Spearman, both z-scored": by_book_z.mean(),
                    "... against another book's reader scores": shuffled.mean(),
                    "books where own reader vector is the best match": int(
                        sum(
                            np.argmax([spearmanr(Zs24[i], Fz[j])[0] for j in range(len(sub))]) == i
                            for i in range(len(sub))
                        )
                    ),
                }
            )
            per_word[name] = by_word
    out += [md_table(pd.DataFrame(summary)), ""]
    pw = pd.DataFrame(per_word).sort_values("F_proj_plain", ascending=False)
    out += [
        "Spearman per word across the 24 books (reader score against projection).",
        "",
        md_table(pw),
        "",
    ]
    md = "\n".join(out)
    (RESULTS / "felt_projection.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
