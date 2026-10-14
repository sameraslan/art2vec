"""P5: a content-controlled style encoder on short passages sampled across each book.

    caffeinate -i .venv/bin/python -m prose.style_embed --variant clean --name style_clean
        [--per-book 60] [--words 120] [--batch 16] [--device mps]

Passages of about ``--words`` words start at evenly spaced positions through the book (the
same positions in every text variant, because chunk idx is aligned), at the first sentence
start after the position. Writes data/emb/<name>/<key>.npy and <key>.idx.npy (the chunk idx of
each passage); resumable. Book vectors and blocks: ``world.build <name> --prefix P5``.
"""

from __future__ import annotations

import argparse
import re
import time

import numpy as np
from world.common import EMB, book_keys, load_chunks
from world.embed import encode, free_memory_pct, load_model, unload

MODEL = "StyleDistance/styledistance"
SENT_END = re.compile(r"[.!?][\"'”’)]*$")


def passages(chunks: list[dict], n: int, n_words: int) -> tuple[list[str], np.ndarray]:
    """n passages of about n_words words at evenly spaced positions, and their chunk idx."""
    texts, idx = [], []
    for p in np.linspace(0, len(chunks), n, endpoint=False):
        c = int(p)
        w = chunks[c]["text"].split()
        start = int((p - c) * max(len(w) - n_words, 0))
        for s in range(start, min(start + 60, max(len(w) - n_words, 0))):
            if s == 0 or SENT_END.search(w[s - 1]):
                start = s
                break
        texts.append(" ".join(w[start : start + n_words]))
        idx.append(c)
    return texts, np.array(idx)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variant", default="clean")
    ap.add_argument("--name", required=True)
    ap.add_argument("--per-book", type=int, default=60)
    ap.add_argument("--words", type=int, default=120)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", default="mps")
    args = ap.parse_args()
    out = EMB / args.name
    out.mkdir(parents=True, exist_ok=True)
    model = load_model(MODEL, args.device, 256)
    t0 = time.time()
    for key in book_keys():
        path = out / f"{key}.npy"
        if path.exists():
            continue
        while free_memory_pct() < 20:
            print("memory pressure: pausing 30 s", flush=True)
            time.sleep(30)
        texts, idx = passages(load_chunks(args.variant, key), args.per_book, args.words)
        E = encode(model, texts, None, args.batch)
        np.save(out / f"{key}.idx.npy", idx)
        np.save(path, E)
        print(f"{key} {len(texts)} passages, {time.time() - t0:.0f} s", flush=True)
    unload(model)


if __name__ == "__main__":
    main()
