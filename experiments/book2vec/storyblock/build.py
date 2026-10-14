"""Story and digest-World blocks for the 24 books a reader went through.

    .venv/bin/python -m storyblock.build

From data/emb/digest (storyblock.embed) and the digest strings. Suffix _plain / _inst = Qwen3
without / with an instruction; _tfidf = TF-IDF of the digest text. Every embedding block is
centred across its own books and L2-normalised.

    S_story_*         the reader's "story" field
    S_characters_*    roles and arcs joined
    S_storychar_*     the two unit vectors side by side (so cosines are averaged)
    W_digest_*        the reader's "world" field;  W_digestsubj_* adds the "subjects" list
    SM_* / WM_*       the same from the title-only digests (memory, no text; 23 books: the
                      fame-control book has none)
"""

from __future__ import annotations

import numpy as np
from eval.blocks import save_block
from sklearn.feature_extraction.text import TfidfVectorizer
from world.common import EMB, centre_unit

from storyblock.digests import field_text, ids, load

RECIPES = {
    "S_story": ("story",),
    "S_characters": ("characters",),
    "S_storychar": ("story", "characters"),
    "W_digest": ("world",),
    "W_digestsubj": ("world", "subjects"),
}


def digest_matrix(source: str, field: str, tag: str) -> np.ndarray:
    return np.load(EMB / "digest" / f"{source}_{field}_{tag}.npy")


def main() -> None:
    table = ids()
    for source, rename in (("out", {}), ("title_only", {"S_": "SM_", "W_": "WM_"})):
        digests = [load(source, b) for b in table["bid"]]
        have = np.array([d.get("memory") != "none" for d in digests])
        keys = list(table["key"][have])
        for base, fields in RECIPES.items():
            name = base
            for old, new in rename.items():
                name = name.replace(old, new, 1)
            meta = {
                "input_level": "ordered text",
                "metric": "cosine",
                "source": "reader digest from masked text" if source == "out" else "title only",
                "fields": list(fields),
                "flagged": [],
            }
            for tag in ("plain", "inst"):
                X = np.hstack([centre_unit(digest_matrix(source, f, tag)[have]) for f in fields])
                m = {**meta, "what": f"Qwen3-Embedding-0.6B ({tag}) of {'+'.join(fields)}"}
                save_block(f"{name}_{tag}", keys, m, X=X)
            texts = ["\n".join(field_text(d, f) for f in fields) for d in digests]
            texts = [t for t, h in zip(texts, have, strict=True) if h]
            vec = TfidfVectorizer(sublinear_tf=True, stop_words="english", min_df=2)
            m = {**meta, "what": f"TF-IDF of {'+'.join(fields)}"}
            save_block(f"{name}_tfidf", keys, m, X=vec.fit_transform(texts).toarray())
            print(name, len(keys), flush=True)


if __name__ == "__main__":
    main()
