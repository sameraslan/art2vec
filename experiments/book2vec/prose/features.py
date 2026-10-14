"""Prose features of one book (or of a token mask of it), from the compact token arrays."""

from __future__ import annotations

import numpy as np

from prose.tokens import PUNCT_CLASSES

N_TAGS = 64  # upper bound on distinct fine tags; trigram code = t0 * 64**2 + t1 * 64 + t2
TEXT_VARIANTS = ("all_raw", "all_noprop", "narr_raw", "narr_noprop")
PUNCT_RATES = ("comma", "semicolon", "colon", "period", "question", "exclamation", "dash",
               "ellipsis", "paren", "hyphen")  # fmt: skip
SENT_Q = (10, 25, 50, 75, 90)
MAX_WORD_LEN = 13
RHYTHM_NAMES = (
    [f"punct_{p}" for p in PUNCT_RATES]
    + ["sent_log_mean", "sent_log_sd"]
    + [f"sent_log_q{q}" for q in SENT_Q]
    + ["sent_lag1", "sent_share_le5", "sent_share_ge40"]
    + ["para_log_mean_words", "para_log_median_words", "para_log_mean_sents"]
    + ["log_mtld", "mattr500"]
    + ["wlen_mean", "wlen_sd"]
    + [f"wlen_{i}" for i in range(1, MAX_WORD_LEN + 1)]
)
RHYTHM_GROUPS = {
    "punct": [n for n in RHYTHM_NAMES if n.startswith("punct_")],
    "sentence": [n for n in RHYTHM_NAMES if n.startswith(("sent_", "para_"))],
    "lexical": [n for n in RHYTHM_NAMES if n.startswith(("log_mtld", "mattr", "wlen"))],
}


def variant_mask(book: dict[str, np.ndarray], variant: str) -> np.ndarray:
    """Word tokens counted under a text variant: all / narr(ation only) x raw / noprop."""
    text, names = variant.split("_")
    m = book["is_word"].copy()
    if text == "narr":
        m &= ~book["is_quote"]
    if names == "noprop":
        m &= ~book["is_name"]
    return m


def word_counts(
    book: dict[str, np.ndarray], mask: np.ndarray, vocab_of_type: np.ndarray, n_vocab: int
) -> tuple[np.ndarray, int]:
    """Counts of the vocabulary words among the masked tokens, and the masked token total.

    ``vocab_of_type[t]`` is the vocabulary id of the book's type t, or -1.
    """
    ids = vocab_of_type[book["tid"][mask]]
    return np.bincount(ids[ids >= 0], minlength=n_vocab), int(mask.sum())


def trigram_codes(
    book: dict[str, np.ndarray], mask: np.ndarray, tag_ids: np.ndarray, words_only: bool = False
) -> np.ndarray:
    """Codes of the tag trigrams whose three tokens are all in the mask and adjacent.

    ``tag_ids`` maps the book's tag codes to corpus-wide tag ids. With ``words_only`` the
    punctuation is taken out of the sequence first.
    """
    t = tag_ids[book["tag"]]
    if words_only:
        keep = book["is_word"]
        t, mask = t[keep], mask[keep]
    ok = mask[:-2] & mask[1:-1] & mask[2:]
    return (t[:-2] * N_TAGS * N_TAGS + t[1:-1] * N_TAGS + t[2:])[ok]


def mattr(tid: np.ndarray, window: int = 500) -> float:
    """Moving-average type-token ratio: mean share of distinct words in every window."""
    n = len(tid)
    if n < window:
        return len(np.unique(tid)) / max(n, 1)
    prev = previous_occurrence(tid)
    # token j is the first of its type in every window whose start s has prev[j] < s <= j
    start = np.maximum(prev + 1, np.arange(n) - window + 1)
    diff = np.zeros(n + 2)
    np.add.at(diff, start, 1)
    np.add.at(diff, np.arange(n) + 1, -1)
    types = np.cumsum(diff)[: n - window + 1]
    return float(types.mean() / window)


def previous_occurrence(tid: np.ndarray) -> np.ndarray:
    """Index of the previous token of the same type, -1 if none."""
    order = np.argsort(tid, kind="stable")
    prev = np.full(len(tid), -1, dtype=np.int64)
    same = tid[order][1:] == tid[order][:-1]
    prev[order[1:][same]] = order[:-1][same]
    return prev


def mtld(tid: np.ndarray, threshold: float = 0.72) -> float:
    """Measure of textual lexical diversity (forward pass): mean length of the runs over
    which the type-token ratio stays above the threshold."""
    prev = previous_occurrence(tid).tolist()
    factors, start, types = 0.0, 0, 0
    for j, p in enumerate(prev):
        if p < start:
            types += 1
        if types / (j - start + 1) <= threshold:
            factors += 1
            start, types = j + 1, 0
    n_rest = len(prev) - start
    if n_rest:
        factors += (1 - types / n_rest) / (1 - threshold)
    return len(prev) / factors if factors else float(len(prev))


def lag1(x: np.ndarray) -> float:
    if len(x) < 3 or x.std() == 0:
        return 0.0
    return float(np.corrcoef(x[:-1], x[1:])[0, 1])


def rhythm_features(book: dict[str, np.ndarray], mask: np.ndarray) -> np.ndarray:
    """Punctuation, sentence, paragraph, lexical-diversity and word-length features
    (RHYTHM_NAMES). Quote marks are not counted: they measure dialogue, which is Telling."""
    word = book["is_word"] & mask
    n_words = max(int(word.sum()), 1)
    pc = np.bincount(book["punct"][mask], minlength=len(PUNCT_CLASSES))
    out = [1000.0 * pc[PUNCT_CLASSES.index(p)] / n_words for p in PUNCT_RATES]

    per_sent = np.bincount(book["sent"][word])
    s = per_sent[per_sent > 0].astype(float)
    ls = np.log(s)
    out += [ls.mean(), ls.std(), *np.percentile(ls, SENT_Q)]
    out += [lag1(ls), float((s <= 5).mean()), float((s >= 40).mean())]

    per_para = np.bincount(book["para"][word])
    per_para[book["headings"][book["headings"] < len(per_para)]] = 0
    p = per_para[per_para > 0].astype(float)
    sent_para = np.unique(np.stack([book["para"][word], book["sent"][word]]), axis=1)[0]
    sents_in_para = np.bincount(sent_para, minlength=len(per_para))[per_para > 0]
    out += [np.log(p.mean()), np.log(np.median(p)), np.log(sents_in_para.mean())]

    tid = book["tid"][word]
    out += [np.log(mtld(tid)), mattr(tid)]

    type_len = np.char.str_len(np.char.replace(book["types"], "'", ""))
    wl = np.clip(type_len[tid], 1, MAX_WORD_LEN)
    out += [float(type_len[tid].mean()), float(type_len[tid].std())]
    out += list(np.bincount(wl, minlength=MAX_WORD_LEN + 1)[1:] / n_words)
    return np.array(out, dtype=float)


def zscore(X: np.ndarray, ref: np.ndarray | None = None) -> np.ndarray:
    """Columns of X standardised by the mean and sd of ``ref`` (default X itself)."""
    ref = X if ref is None else ref
    sd = ref.std(0)
    return (X - ref.mean(0)) / np.where(sd > 0, sd, 1.0)
