"""Why are these two books neighbours? The passages that put them together.

    .venv/bin/python -m world.why [--block W1_qwen_maskB_c] [--emb qwen_maskB] [--a KEY --b KEY]

Without --a / --b it takes the closest pair of books that are each other's nearest neighbour,
have different authors and are not related (translation, edition, series, retelling). Chunk
embeddings are centred on the corpus mean; the three most similar chunk pairs are printed
(each chunk used once) with the first 60 words of the clean text of each. Writes
results/world_why.md.
"""

from __future__ import annotations

import argparse

import numpy as np
from eval.blocks import RESULTS, load_block, load_testbed
from eval.pairs import build_pairs

from world.build import book_matrices, load_emb
from world.common import book_keys, first_words, load_chunks, unit


def pick_pair(block: str) -> list[tuple[float, str, str]]:
    """Mutual nearest neighbours by different authors, unrelated; closest first."""
    b = load_block(block)
    D = b.distances()
    np.fill_diagonal(D, np.inf)
    nn = D.argmin(1)
    neg = set(build_pairs(load_testbed())["negatives"])
    out = []
    for i, j in enumerate(nn):
        if nn[j] == i and i < j and tuple(sorted((b.keys[i], b.keys[j]))) in neg:
            out.append((float(D[i, j]), str(b.keys[i]), str(b.keys[j])))
    return sorted(out)


def top_chunk_pairs(
    emb: str, a: str, b: str, mu: np.ndarray, n: int = 3
) -> tuple[list[tuple[float, int, int]], float]:
    Ea, ia = load_emb(emb, a)
    Eb, ib = load_emb(emb, b)
    S = unit(Ea - mu) @ unit(Eb - mu).T
    out = []
    S2 = S.copy()
    for _ in range(n):
        i, j = np.unravel_index(S2.argmax(), S2.shape)
        out.append((float(S2[i, j]), int(ia[i]), int(ib[j])))
        S2[i, :] = -np.inf
        S2[:, j] = -np.inf
    return out, float(np.median(S))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--block", default="W1_qwen_maskB_c")
    ap.add_argument("--emb", default="qwen_maskB")
    ap.add_argument("--a", default=None)
    ap.add_argument("--b", default=None)
    args = ap.parse_args()
    tb = load_testbed()
    mutual = pick_pair(args.block)
    a, b = (args.a, args.b) if args.a else mutual[0][1:]
    mu = book_matrices(args.emb, book_keys())["full"].mean(0)
    pairs, median = top_chunk_pairs(args.emb, a, b, mu)
    out = [
        f"## Why are these two books World neighbours? ({args.block})",
        "",
        "Mutual nearest neighbours by different authors, not related by translation, edition, "
        "series or retelling (cosine distance):",
        "",
    ]
    out += [f"- {x} ~ {y}: {d:.3f}" for d, x, y in mutual]
    out += [
        "",
        f"### {tb.at[a, 'title']} ({tb.at[a, 'author']}, {tb.at[a, 'year']}) and "
        f"{tb.at[b, 'title']} ({tb.at[b, 'author']}, {tb.at[b, 'year']})",
        "",
        "The three most similar chunk pairs (centred cosine; the median over all sampled "
        f"chunk pairs of the two books is {median:.2f}). The encoder saw the name-masked "
        "text; the clean text is printed.",
        "",
    ]
    ca, cb = load_chunks("clean", a), load_chunks("clean", b)
    for s, i, j in pairs:
        out += [
            f"**cosine {s:.2f}**",
            "",
            f"- `{a}` chunk {i}: {first_words(ca[i]['text'], 60)} ...",
            f"- `{b}` chunk {j}: {first_words(cb[j]['text'], 60)} ...",
            "",
        ]
    md = "\n".join(out)
    (RESULTS / "world_why.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
