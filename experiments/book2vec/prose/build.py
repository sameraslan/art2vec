"""Build the Prose block candidates P1 (word profiles), P2 (tag trigrams), P3 (rhythm).

    .venv/bin/python -m prose.build

One book is loaded at a time; only count vectors are kept. Each block gets X (the whole
book) and X_a / X_b / X_h1 / X_h2 (odd / even chunks, first / second half), all z-scored with
the whole-book mean and sd, which is what Burrows's Delta does.

P1_mfw{N}_{all|narr}_{raw|noprop}_{cull|nocull}
    Cosine Delta on the N most frequent words. narr = narration only (tokens outside quotation
    marks); noprop = proper nouns and words capitalised mid-sentence are taken out before
    counting; cull = a word must occur in at least half of the books.
P2_tag3_{500|1000}[_words]
    z-scored relative frequencies of the most frequent fine-tag trigrams, cosine. _words =
    punctuation taken out of the tag sequence first.
P3_rhythm, P3_punct, P3_sentence, P3_lexical
    z-scored punctuation rates, sentence and paragraph length statistics, MTLD / MATTR and the
    word-length distribution; Euclidean. P3_rhythm is all of them.
"""

from __future__ import annotations

import numpy as np
from eval.blocks import BLOCK_DIR, load_testbed, save_block

from prose.features import (
    N_TAGS,
    RHYTHM_GROUPS,
    RHYTHM_NAMES,
    TEXT_VARIANTS,
    rhythm_features,
    trigram_codes,
    variant_mask,
    word_counts,
    zscore,
)
from prose.tokens import Vocab, book_keys, half_masks, load_book

PARTS = ("full", "a", "b", "h1", "h2")
N_CANDIDATES = 3000
MFW_SIZES = (100, 200, 500)
TRIGRAM_SIZES = (500, 1000)


def flagged_books() -> list[str]:
    """Books whose quotation detection is known to be wrong (see data/annotate_report.csv)."""
    tb = load_testbed()
    return sorted(tb.index[tb["quote_flag"] != ""])


def candidate_vocabulary(keys: list[str]) -> tuple[Vocab, list[str]]:
    """The N_CANDIDATES words with the highest mean relative frequency over the books."""
    vocab = Vocab()
    total = np.zeros(0)
    for key in keys:
        book = load_book(key)
        gid = vocab.encode(book["types"])
        if len(vocab.ids) > len(total):
            total = np.r_[total, np.zeros(len(vocab.ids) - len(total))]
        tid = book["tid"][book["is_word"]]
        total[gid] += np.bincount(tid, minlength=len(gid)) / len(tid)
    names = vocab.names()
    top = np.argsort(-total)[:N_CANDIDATES]
    return vocab, [names[i] for i in top]


def top_trigrams(keys: list[str], tags: Vocab, words_only: bool, n: int) -> np.ndarray:
    """Codes of the n trigrams with the highest mean relative frequency over the books."""
    total = np.zeros(N_TAGS**3)
    for key in keys:
        book = load_book(key)
        codes = trigram_codes(
            book, np.ones(len(book["tid"]), bool), tags.encode(book["tag_names"]), words_only
        )
        total += np.bincount(codes, minlength=N_TAGS**3) / len(codes)
    assert len(tags.ids) <= N_TAGS, "raise N_TAGS"
    return np.argsort(-total)[:n]


def save_split_block(name: str, keys: list[str], meta: dict, Z: dict[str, np.ndarray]) -> None:
    save_block(name, keys, meta, X=Z["full"], X_a=Z["a"], X_b=Z["b"], X_h1=Z["h1"], X_h2=Z["h2"])
    print("wrote", name, Z["full"].shape, flush=True)


def main() -> None:
    keys = book_keys()
    flagged = flagged_books()
    _, cand = candidate_vocabulary(keys)
    cand_id = {w: i for i, w in enumerate(cand)}
    tags = Vocab()
    tri = {
        False: top_trigrams(keys, tags, False, max(TRIGRAM_SIZES)),
        True: top_trigrams(keys, tags, True, max(TRIGRAM_SIZES)),
    }
    tri_index = {}
    for words_only, codes in tri.items():
        idx = np.full(N_TAGS**3, -1)
        idx[codes] = np.arange(len(codes))
        tri_index[words_only] = idx

    n = len(keys)
    mfw = {v: {p: np.zeros((n, N_CANDIDATES)) for p in PARTS} for v in TEXT_VARIANTS}
    tg = {w: {p: np.zeros((n, max(TRIGRAM_SIZES))) for p in PARTS} for w in (False, True)}
    rh = {p: np.zeros((n, len(RHYTHM_NAMES))) for p in PARTS}
    for i, key in enumerate(keys):
        book = load_book(key)
        vocab_of_type = np.array([cand_id.get(t, -1) for t in book["types"]])
        tag_ids = tags.lookup(book["tag_names"])
        vmask = {v: variant_mask(book, v) for v in TEXT_VARIANTS}
        for part, m in half_masks(book).items():
            for v in TEXT_VARIANTS:
                counts, total = word_counts(book, m & vmask[v], vocab_of_type, N_CANDIDATES)
                mfw[v][part][i] = counts / max(total, 1)
            for words_only in (False, True):
                codes = trigram_codes(book, m, tag_ids, words_only)
                idx = tri_index[words_only][codes]
                counts = np.bincount(idx[idx >= 0], minlength=max(TRIGRAM_SIZES))
                tg[words_only][part][i] = counts / len(codes)
            rh[part][i] = rhythm_features(book, m)
        print(f"{i + 1}/{n} {key}", flush=True)

    for v in TEXT_VARIANTS:
        full = mfw[v]["full"]
        order = np.argsort(-full.mean(0))
        in_half = (full > 0).mean(0) >= 0.5
        for cull in (True, False):
            ranked = [j for j in order if in_half[j]] if cull else list(order)
            for size in MFW_SIZES:
                cols = np.array(ranked[:size])
                Z = {p: zscore(mfw[v][p][:, cols], full[:, cols]) for p in PARTS}
                text, names = v.split("_")
                meta = {
                    "what": f"Cosine Delta on the {size} most frequent words",
                    "input_level": "book bag"
                    if text == "all" and names == "raw"
                    else "ordered text",
                    "metric": "cosine",
                    "text": "narration only" if text == "narr" else "all text",
                    "proper_nouns_removed": names == "noprop",
                    "culled_to_half_of_books": cull,
                    "n_words": size,
                    "words": [cand[j] for j in cols],
                    "flagged": flagged if text == "narr" else [],
                    "level_note": "all-text raw counts are a bag of words (book bag for the "
                    "whole-book vector; the split halves need page bags). Narration-only and "
                    "name removal need the running text (quotation marks, sentence position); "
                    "name removal by POS tag alone would work on HathiTrust page features.",
                }
                save_split_block(
                    f"P1_mfw{size}_{text}_{names}_{'cull' if cull else 'nocull'}", keys, meta, Z
                )

    names = tags.names()
    for words_only in (False, True):
        for size in TRIGRAM_SIZES:
            Z = {
                p: zscore(tg[words_only][p][:, :size], tg[words_only]["full"][:, :size])
                for p in PARTS
            }
            tri_names = [
                " ".join(names[x] for x in divmod_tags(int(c))) for c in tri[words_only][:size]
            ]
            meta = {
                "what": f"z-scored frequencies of the {size} most frequent fine-tag trigrams",
                "input_level": "ordered text",
                "metric": "cosine",
                "punctuation_in_sequence": not words_only,
                "n_trigrams": size,
                "trigrams": tri_names,
                "flagged": [],
                "level_note": "needs tag sequences; HathiTrust gives per-page tag counts only",
            }
            save_split_block(f"P2_tag3_{size}{'_words' if words_only else ''}", keys, meta, Z)

    groups = {"rhythm": list(RHYTHM_NAMES), **RHYTHM_GROUPS}
    for g, cols_names in groups.items():
        cols = [RHYTHM_NAMES.index(c) for c in cols_names]
        Z = {p: zscore(rh[p][:, cols], rh["full"][:, cols]) for p in PARTS}
        meta = {
            "what": f"z-scored {g} features",
            "input_level": "ordered text",
            "metric": "euclidean",
            "features": cols_names,
            "flagged": [],
            "level_note": "sentence and paragraph lengths and MTLD need the running text; "
            "punctuation rates and word lengths alone are a page bag",
        }
        save_split_block(f"P3_{g}", keys, meta, Z)
    np.savez_compressed(
        BLOCK_DIR / "_P3_raw.npz", keys=np.array(keys), names=np.array(RHYTHM_NAMES), **rh
    )


def divmod_tags(code: int) -> tuple[int, int, int]:
    a, rest = divmod(code, N_TAGS * N_TAGS)
    b, c = divmod(rest, N_TAGS)
    return a, b, c


if __name__ == "__main__":
    main()
