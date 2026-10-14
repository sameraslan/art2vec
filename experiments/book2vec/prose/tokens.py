"""Compact per-book token arrays, so every feature script is a few bincounts.

    .venv/bin/python -m prose.tokens [--force]

Reads data/tok/<key>.parquet one book at a time and writes data/feat/<key>.npz with one entry
per token (line-break SPACE tokens dropped):

    types       (v,) str   the book's distinct lower-cased tokens (apostrophes folded to ')
    tid         int32      index into types
    tag_names   (t,) str   the fine tags used in this book
    tag         int8       index into tag_names
    is_word     bool       has a letter and is not punctuation
    is_name     bool       word that is PROPN, or capitalised after a word / comma inside a
                           sentence (except "I")
    is_quote    bool       inside quotation marks (from the prep)
    punct       int8       punctuation class, see PUNCT_CLASSES (0 = not punctuation)
    sent        int32      sentence id
    para        int32      paragraph id
    chunk       int16      index of the ~1,000-word chunk (data/chunks/clean) holding the token
    headings    int32      paragraph ids that look like chapter headings
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from eval.blocks import ROOT, load_testbed

FEAT = ROOT / "data" / "feat"
PUNCT_CLASSES = (
    "none",
    "comma",
    "semicolon",
    "colon",
    "period",
    "question",
    "exclamation",
    "dash",
    "ellipsis",
    "paren",
    "quote_mark",
    "hyphen",
    "other",
)
_PUNCT_MAP = {
    ",": 1,
    ";": 2,
    ":": 3,
    ".": 4,
    "?": 5,
    "!": 6,
    "—": 7,
    "–": 7,
    "--": 7,
    "―": 7,
    "…": 8,
    "...": 8,
    "(": 9,
    ")": 9,
    "[": 9,
    "]": 9,
    "-": 11,
}
_QUOTE_CHARS = set("\"'“”‘’«»`")
_HEADING = re.compile(
    r"^(?:(?:chapter|chap\.|book|part|volume|vol\.|letter|record|stave|canto|section|"
    r"epilogue|prologue|conclusion)\b.{0,70}|[IVXLC]+\.?|[IVXLC]+\.\s.{1,70}|\d{1,3}\.?)$",
    re.IGNORECASE,
)
_ROMAN = re.compile(r"^[IVXLC]+\.?(\s|$)")


def punct_class(text: str, is_punct: bool) -> int:
    if not is_punct:
        return 0
    if text in _PUNCT_MAP:
        return _PUNCT_MAP[text]
    if text and all(c in _QUOTE_CHARS for c in text):
        return 10
    if text and set(text) <= {"."} and len(text) > 1:
        return 8
    if text and set(text) <= {"-", "—", "–"}:
        return 7
    return 12


def heading_paragraphs(clean_text: str) -> np.ndarray:
    """Paragraph ids of chapter-like headings (the last of a run of consecutive headings)."""
    paras = clean_text.split("\n\n")
    is_head = []
    for p in paras:
        p = p.strip()
        ok = "\n" not in p and bool(_HEADING.match(p))
        if ok and not _ROMAN.match(p.upper()) and p[:1].islower():
            ok = False
        # a bare "I" between ordinary paragraphs is a heading only in upper case
        if ok and re.fullmatch(r"[ivxlc]+\.?", p):
            ok = False
        is_head.append(ok)
    ids = [i for i, h in enumerate(is_head) if h and not (i + 1 < len(paras) and is_head[i + 1])]
    return np.array(ids, dtype=np.int32)


def extract(key: str) -> dict[str, np.ndarray]:
    """The compact arrays for one book."""
    cols = ["para_id", "sent_id", "text", "lower", "pos", "tag", "is_quote"]
    df = pd.read_parquet(ROOT / "data" / "tok" / f"{key}.parquet", columns=cols)
    df = df[df["pos"] != "SPACE"].reset_index(drop=True)
    text = df["text"].to_numpy(object)
    lower = df["lower"].str.replace("[’‘`]", "'", regex=True)
    pos = df["pos"].astype(str).to_numpy()
    is_punct = pos == "PUNCT"
    has_alpha = df["text"].str.contains(r"[^\W\d_]", regex=True).to_numpy()
    is_word = has_alpha & ~is_punct & (pos != "SYM")
    punct = np.array([punct_class(t, p) for t, p in zip(text, is_punct, strict=True)], np.int8)

    sent = df["sent_id"].to_numpy(np.int32)
    prev_same_sent = np.r_[False, sent[1:] == sent[:-1]]
    prev_word = np.r_[False, is_word[:-1]]
    prev_soft = np.r_[False, np.isin(punct[:-1], (1, 2, 9, 11))]
    cap = df["text"].str[:1].str.isupper().to_numpy(bool)
    cap_mid = cap & is_word & prev_same_sent & (prev_word | prev_soft) & (lower != "i").to_numpy()
    is_name = is_word & ((pos == "PROPN") | cap_mid)

    types, tid = np.unique(lower.to_numpy(str), return_inverse=True)
    tag_cat = df["tag"].astype("category").cat.remove_unused_categories()

    para = df["para_id"].to_numpy(np.int32)
    chunk_of_para = np.zeros(para.max() + 1, dtype=np.int16)
    with open(ROOT / "data" / "chunks" / "clean" / f"{key}.jsonl") as fh:
        for line in fh:
            c = json.loads(line)
            chunk_of_para[c["start_para"] : c["end_para"] + 1] = c["idx"]
    clean = (ROOT / "data" / "clean" / f"{key}.txt").read_text()
    return {
        "types": types,
        "tid": tid.astype(np.int32),
        "tag_names": np.array(tag_cat.cat.categories, dtype=str),
        "tag": tag_cat.cat.codes.to_numpy(np.int8),
        "is_word": is_word,
        "is_name": is_name,
        "is_quote": df["is_quote"].to_numpy(bool),
        "punct": punct,
        "sent": sent,
        "para": para,
        "chunk": chunk_of_para[para],
        "headings": heading_paragraphs(clean),
    }


def load_book(key: str) -> dict[str, np.ndarray]:
    """Load one book's arrays (about 12 bytes per token)."""
    with np.load(FEAT / f"{key}.npz", allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def book_keys() -> list[str]:
    return list(load_testbed().index)


class Vocab:
    """A growing string -> id map shared across books (ids in order of first appearance)."""

    def __init__(self) -> None:
        self.ids: dict[str, int] = {}

    def encode(self, names: np.ndarray) -> np.ndarray:
        """Ids for the given strings, adding the unseen ones."""
        return np.array([self.ids.setdefault(str(n), len(self.ids)) for n in names], np.int64)

    def lookup(self, names: np.ndarray) -> np.ndarray:
        """Ids for the given strings, -1 where unseen."""
        return np.array([self.ids.get(str(n), -1) for n in names], np.int64)

    def names(self) -> list[str]:
        return list(self.ids)


def half_masks(book: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Token masks: full, a / b (odd / even chunks), h1 / h2 (first / second half by chunk)."""
    chunk = book["chunk"]
    n_chunks = int(chunk.max()) + 1
    first = chunk < (n_chunks + 1) // 2
    return {
        "full": np.ones(len(chunk), bool),
        "a": chunk % 2 == 0,
        "b": chunk % 2 == 1,
        "h1": first,
        "h2": ~first,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    FEAT.mkdir(parents=True, exist_ok=True)
    for key in book_keys():
        out: Path = FEAT / f"{key}.npz"
        if out.exists() and not args.force:
            continue
        arrays = extract(key)
        np.savez_compressed(out, **arrays)
        n_ch = len(arrays["headings"])
        print(
            f"{key}: {len(arrays['tid'])} tokens, {int(arrays['is_word'].sum())} words, "
            f"{len(arrays['types'])} types, {int(arrays['chunk'].max()) + 1} chunks, "
            f"{n_ch} headings, names {arrays['is_name'].sum() / arrays['is_word'].sum():.3f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
