"""Split each variant into chunks of about 1,000 words on paragraph boundaries, in order.

data/chunks/<variant>/<key>.jsonl, one JSON object per line: key, idx, n_words, start_para,
end_para (inclusive paragraph indices into data/<variant>/<key>.txt), text.

The boundaries are chosen once, on the clean text, and reused for maskA and maskB, so chunk idx
means the same passage in every variant (n_words differs slightly once names are replaced).
A chunk never ends on a chapter heading, a paragraph is never split (so a very long paragraph
gives a long chunk), and a short tail is folded into the last chunk.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import (
    CHUNKS,
    CLEAN,
    DEFAULT_TESTBED,
    MASK_A,
    MASK_B,
    is_stale,
    n_words,
    read_paragraphs,
    read_testbed,
    select,
)

VARIANTS = {"clean": CLEAN, "maskA": MASK_A, "maskB": MASK_B}
TARGET = 1000
MIN_TAIL = 400


def looks_like_heading(para: str) -> bool:
    return n_words(para) <= 12 and not para.rstrip().endswith((".", "!", "?", "”", '"', ","))


def boundaries(paras: list[str], target: int = TARGET) -> list[tuple[int, int]]:
    """Inclusive (start_para, end_para) ranges of about `target` words each."""
    counts = [n_words(p) for p in paras]
    spans: list[tuple[int, int]] = []
    start, total = 0, 0
    for i, c in enumerate(counts):
        if total and total + c > target and (total + c - target) > (target - total):
            end = i - 1
            while end > start and looks_like_heading(paras[end]):
                end -= 1  # a heading belongs with what follows it
            spans.append((start, end))
            start = end + 1
            total = sum(counts[start:i])
        total += c
    if start < len(paras):
        if spans and total < MIN_TAIL:
            spans[-1] = (spans[-1][0], len(paras) - 1)
        else:
            spans.append((start, len(paras) - 1))
    return spans


def write_chunks(key: str, variant: str, paras: list[str], spans: list[tuple[int, int]]) -> int:
    out = CHUNKS / variant / f"{key}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for idx, (a, b) in enumerate(spans):
            text = "\n\n".join(paras[a : b + 1])
            rec = {"key": key, "idx": idx, "n_words": n_words(text), "start_para": a}
            rec |= {"end_para": b, "text": text}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(out)
    return len(spans)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--testbed", type=Path, default=DEFAULT_TESTBED)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    done = n_chunks = 0
    for row in select(read_testbed(args.testbed), args.only):
        key = row["key"]
        clean_path = CLEAN / f"{key}.txt"
        if not clean_path.exists():
            print(f"{key}: no clean text, skipped")
            continue
        clean = read_paragraphs(clean_path)
        spans = boundaries(clean)
        for variant, folder in VARIANTS.items():
            src = folder / f"{key}.txt"
            if not src.exists():
                print(f"{key}: no {variant} text, skipped")
                continue
            out = CHUNKS / variant / f"{key}.jsonl"
            if not args.force and not is_stale(out, src, clean_path, Path(__file__)):
                continue
            paras = clean if variant == "clean" else read_paragraphs(src)
            if len(paras) != len(clean):
                print(f"FAILED {key}: {variant} has {len(paras)} paragraphs, clean {len(clean)}")
                continue
            n_chunks += write_chunks(key, variant, paras, spans)
            done += 1
    print(f"chunk: {done} files written, {n_chunks} chunks, under {CHUNKS}")


if __name__ == "__main__":
    main()
