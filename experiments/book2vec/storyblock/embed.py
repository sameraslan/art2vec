"""Embed the reader digests and the felt-word definitions with Qwen3-Embedding-0.6B.

    caffeinate -i .venv/bin/python -m storyblock.embed

Writes data/emb/digest/<source>_<field>_<plain|inst>.npy, 24 rows in ids.csv order (a zero row
where the digest field is empty: the title-only digest of the fame-control book), and
felt_words_<plain|inst>.npy (24 rows, one per felt word). About 450 short texts.
"""

from __future__ import annotations

import numpy as np
from world.common import EMB
from world.embed import encode, load_model, prompt_for, unload

from storyblock.digests import FELT_WORDS, FIELDS, field_text, ids, load

INSTRUCTION = {"story": "plot", "characters": "plot", "world": "world", "subjects": "world"}
FELT_QUERY = "Given a mood, retrieve passages of fiction that leave their reader in that mood"


def main() -> None:
    out = EMB / "digest"
    out.mkdir(parents=True, exist_ok=True)
    model = load_model(max_tokens=1024)
    bids = list(ids()["bid"])
    for source in ("out", "title_only"):
        digests = [load(source, b) for b in bids]
        for field in FIELDS:
            texts = [field_text(d, field) for d in digests]
            have = np.array([bool(t) for t in texts])
            for tag, prompt in (("plain", None), ("inst", prompt_for(INSTRUCTION[field]))):
                E = np.zeros((len(texts), 1024), np.float32)
                E[have] = encode(model, [t for t in texts if t], prompt, 4)
                np.save(out / f"{source}_{field}_{tag}.npy", E)
                print(source, field, tag, int(have.sum()), flush=True)
    plain = encode(model, [f"A passage that feels {w}." for w in FELT_WORDS], None, 8)
    inst = encode(model, list(FELT_WORDS), prompt_for(FELT_QUERY), 8)
    np.save(out / "felt_words_plain.npy", plain)
    np.save(out / "felt_words_inst.npy", inst)
    unload(model)


if __name__ == "__main__":
    main()
