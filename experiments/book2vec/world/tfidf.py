"""W0: TF-IDF book bags over name-masked and clean text, cosine.

    .venv/bin/python -m world.tfidf

Writes W0_tfidf_{maskB,clean}[_nostop]. Stand-ins (Person3, Place2) are removed before
counting. Words must occur in at least two books, so a name that lives in one book only never
counts; names shared by two books (a series, two translations) do, in the clean variant.
"""

from __future__ import annotations

import numpy as np
from eval.blocks import save_block
from sklearn.feature_extraction.text import TfidfVectorizer

from world.common import STANDIN, book_keys, load_chunks


def docs(variant: str, keys: list[str]) -> dict[str, list[str]]:
    """Whole book, odd / even chunks and first / second half as strings."""
    out: dict[str, list[str]] = {k: [] for k in ("all", "a", "b", "h1", "h2")}
    for key in keys:
        texts = [STANDIN.sub(" ", c["text"]) for c in load_chunks(variant, key)]
        half = len(texts) // 2
        out["all"].append("\n".join(texts))
        out["a"].append("\n".join(texts[0::2]))
        out["b"].append("\n".join(texts[1::2]))
        out["h1"].append("\n".join(texts[:half]))
        out["h2"].append("\n".join(texts[half:]))
    return out


def main() -> None:
    keys = book_keys()
    for variant in ("maskB", "clean"):
        d = docs(variant, keys)
        for stop in (None, "english"):
            vec = TfidfVectorizer(
                lowercase=True,
                token_pattern=r"(?u)\b[^\W\d_]{2,}\b",
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
                stop_words=stop,
                dtype=np.float32,
            )
            X = vec.fit_transform(d["all"])
            # dense 87 x V is small enough (V ~ 60k)
            parts = {f"X_{h}": vec.transform(d[h]).toarray() for h in ("a", "b", "h1", "h2")}
            name = f"W0_tfidf_{variant}" + ("_nostop" if stop else "")
            meta = {
                "what": f"TF-IDF (sublinear tf, min_df 2, max_df 0.95) over {variant} text"
                + (", English stop words removed" if stop else ""),
                "input_level": "book bag",
                "metric": "cosine",
                "variant": variant,
                "vocab": len(vec.vocabulary_),
            }
            print(save_block(name, keys, meta, X=X.toarray(), **parts), len(vec.vocabulary_))


if __name__ == "__main__":
    main()
