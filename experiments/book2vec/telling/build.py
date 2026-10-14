"""Build the Telling block candidates T1 (scalars) and T2 (shape curves).

    .venv/bin/python -m telling.build

T1_scalars            12 z-scored counts over the ordered text (dialogue share, pronoun person
                      and tense in narration, question / exclamation sentences, chapter
                      length, short paragraphs, time words in narration); Euclidean.
T1_scalars_noquote    the same without anything that depends on quotation marks being found.
T1_bag                9 counts that need only per-book word and tag counts; Euclidean.
T2_curves{20,50}_euc  six curves over the book (CURVES), each z-normalised within the book,
                      concatenated; Euclidean.
T2_curves{20,50}_dtw  the same curves compared by DTW (band = a tenth of the length), root
                      mean square over the six curves; a D block.
T2_{curve}20          one curve at a time (Euclidean), to see which carry anything.
T2_shape              per curve: slope, sd, position of min / max, 4 DCT coefficients (from
                      the 50-segment curves), z-scored; Euclidean. T2_shape_nosd leaves the sd
                      out, because it carries book length.

Split vectors: a / b (odd / even ~1,000-word chunks) for everything; h1 / h2 for the scalars
only, because a curve over the first half is not expected to match one over the second.
Books whose quotation detection failed are listed in meta["flagged"], not removed.
"""

from __future__ import annotations

import numpy as np
from eval.blocks import BLOCK_DIR, cross_distance, save_block
from prose.build import flagged_books
from prose.features import zscore
from prose.tokens import book_keys, half_masks, load_book
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from telling.features import (
    BAG_SCALARS,
    CURVES,
    SCALARS,
    SHAPE_NAMES,
    Lexicons,
    curves,
    dtw_all_pairs,
    scalars,
    shape_numbers,
    znorm,
)

PARTS = ("full", "a", "b", "h1", "h2")
SEGMENTS = (20, 50)
QUOTE_FREE = ("sent_question_share", "sent_exclamation_share", "log_chapter_words",
              "short_paragraph_share")  # fmt: skip


def main() -> None:
    keys = book_keys()
    n = len(keys)
    flagged = flagged_books()
    valence = SentimentIntensityAnalyzer().lexicon
    sc = {p: np.zeros((n, len(SCALARS))) for p in PARTS}
    bag = {p: np.zeros((n, len(BAG_SCALARS))) for p in PARTS}
    cv = {s: {p: np.zeros((n, len(CURVES), s)) for p in ("full", "a", "b")} for s in SEGMENTS}
    for i, key in enumerate(keys):
        book = load_book(key)
        lex = Lexicons(book, valence)
        for part, m in half_masks(book).items():
            sc[part][i], bag[part][i] = scalars(book, lex, m)
            if part in ("full", "a", "b"):
                for s in SEGMENTS:
                    cv[s][part][i] = curves(book, lex, m, s)
        print(f"{i + 1}/{n} {key}", flush=True)

    ch = SCALARS.index("log_chapter_words")
    no_chapters = sorted(k for k, v in zip(keys, sc["full"][:, ch], strict=True) if np.isnan(v))
    median = np.nanmedian(sc["full"][:, ch])
    for p in PARTS:
        col = sc[p][:, ch]
        col[np.isnan(col)] = np.where(np.isnan(sc["full"][:, ch]), median, sc["full"][:, ch])[
            np.isnan(col)
        ]
    np.savez_compressed(
        BLOCK_DIR / "_T_raw.npz",
        keys=np.array(keys),
        scalar_names=np.array(SCALARS),
        bag_names=np.array(BAG_SCALARS),
        curve_names=np.array(CURVES),
        scalars=sc["full"],
        bag=bag["full"],
        curves20=cv[20]["full"],
        curves50=cv[50]["full"],
    )

    def split(Z: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        out = {"X_a": Z["a"], "X_b": Z["b"]}
        if "h1" in Z:
            out |= {"X_h1": Z["h1"], "X_h2": Z["h2"]}
        return out

    base = {"metric": "euclidean", "no_chapter_headings_found": no_chapters}
    Z = {p: zscore(sc[p], sc["full"]) for p in PARTS}
    meta = {
        **base,
        "what": "z-scored Telling scalars",
        "input_level": "ordered text",
        "features": list(SCALARS),
        "flagged": flagged,
        "level_note": "dialogue share and narration-only rates need quotation marks in running "
        "text; chapter and paragraph lengths need layout",
    }
    save_block("T1_scalars", keys, meta, X=Z["full"], **split(Z))
    cols = [SCALARS.index(c) for c in QUOTE_FREE]
    Zq = {p: np.c_[Z[p][:, cols], zscore(bag[p], bag["full"])] for p in PARTS}
    meta = {
        **base,
        "what": "z-scored Telling scalars that do not depend on quotation detection",
        "input_level": "ordered text",
        "features": [*QUOTE_FREE, *BAG_SCALARS],
        "flagged": [],
    }
    save_block("T1_scalars_noquote", keys, meta, X=Zq["full"], **split(Zq))
    Zb = {p: zscore(bag[p], bag["full"]) for p in PARTS}
    meta = {
        "metric": "euclidean",
        "what": "z-scored Telling counts from word and tag totals only",
        "input_level": "book bag",
        "features": list(BAG_SCALARS),
        "flagged": [],
        "level_note": "person, tense, ?/! and time-word rates over all text: computable from "
        "HathiTrust per-page (word, POS) counts (the split halves need the page bags)",
    }
    save_block("T1_bag", keys, meta, X=Zb["full"], **split(Zb))

    curve_meta = {
        "input_level": "ordered text",
        "curves": list(CURVES),
        "flagged": flagged,
        "level_note": "position in the book is needed; page-level bags in page order would "
        "give valence, arousal, first-person and new-vocabulary curves but not dialogue or "
        "sentence length",
    }
    for s in SEGMENTS:
        zc = {p: znorm(cv[s][p]) for p in ("full", "a", "b")}
        flat = {p: zc[p].reshape(n, -1) for p in zc}
        meta = {**curve_meta, "metric": "euclidean", "segments": s,
                "what": f"six z-normalised curves over {s} segments"}  # fmt: skip
        save_block(f"T2_curves{s}_euc", keys, meta, X=flat["full"], **split(flat))
        band = max(1, s // 10)
        D = np.zeros((n, n))
        D_ab = np.zeros((n, n))
        for c in range(len(CURVES)):
            D += dtw_all_pairs(zc["full"][:, c], zc["full"][:, c], band) ** 2
            D_ab += dtw_all_pairs(zc["a"][:, c], zc["b"][:, c], band) ** 2
        D, D_ab = np.sqrt(D / len(CURVES)), np.sqrt(D_ab / len(CURVES))
        D = (D + D.T) / 2
        np.fill_diagonal(D, 0.0)
        meta = {**curve_meta, "metric": "precomputed", "segments": s, "dtw_band": band,
                "what": f"DTW between six z-normalised curves over {s} segments"}  # fmt: skip
        save_block(f"T2_curves{s}_dtw", keys, meta, D=D, D_ab=D_ab)
        if s == 20:
            for c, name in enumerate(CURVES):
                one = {p: zc[p][:, c] for p in zc}
                quote_free = name not in ("dialogue", "first_person")
                meta = {**curve_meta, "metric": "euclidean", "segments": s, "curves": [name],
                        "flagged": [] if quote_free else flagged,
                        "what": f"z-normalised {name} curve over {s} segments"}  # fmt: skip
                save_block(f"T2_{name}20", keys, meta, X=one["full"], **split(one))
        print("curves", s, "done", flush=True)

    shp = {p: np.stack([shape_numbers(c).ravel() for c in cv[50][p]]) for p in ("full", "a", "b")}
    Zs = {p: zscore(shp[p], shp["full"]) for p in shp}
    meta = {**curve_meta, "metric": "euclidean",
            "features": [f"{c}_{f}" for c in CURVES for f in SHAPE_NAMES],
            "what": "z-scored shape numbers of the six 50-segment curves"}  # fmt: skip
    save_block("T2_shape", keys, meta, X=Zs["full"], **split(Zs))
    # the sd of a raw curve grows as segments get shorter, so it carries book length
    keep = [i for i, f in enumerate(meta["features"]) if not f.endswith("_sd")]
    meta = {**meta, "features": [meta["features"][i] for i in keep],
            "what": meta["what"] + ", without the sd of each curve"}  # fmt: skip
    Zn = {p: Zs[p][:, keep] for p in Zs}
    save_block("T2_shape_nosd", keys, meta, X=Zn["full"], **split(Zn))
    d = cross_distance(Z["full"], Z["full"], "euclidean")
    print("T1 mean distance", d.mean(), "no chapter headings:", no_chapters)


if __name__ == "__main__":
    main()
