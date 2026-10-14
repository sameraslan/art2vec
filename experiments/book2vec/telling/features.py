"""Telling features of one book (or of a token mask of it): scalars and shape curves."""

from __future__ import annotations

import numpy as np
from prose.tokens import PUNCT_CLASSES

FIRST_SG = ("i", "me", "my", "mine", "myself")
FIRST_PL = ("we", "us", "our", "ours", "ourselves")
SECOND = ("you", "your", "yours", "yourself", "yourselves", "thou", "thee", "thy", "thine", "ye")
THIRD = ("he", "him", "his", "himself", "she", "her", "hers", "herself", "they", "them",
         "their", "theirs", "themselves")  # fmt: skip
TIME_UNITS = [
    "second",
    "seconds",
    "minute",
    "minutes",
    "hour",
    "hours",
    "day",
    "days",
    "week",
    "weeks",
    "month",
    "months",
    "year",
    "years",
    "morning",
    "evening",
    "night",
    "afternoon",
    "noon",
    "midnight",
    "dawn",
    "dusk",
    "today",
    "tomorrow",
    "yesterday",
    "tonight",
    "o'clock",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "january",
    "february",
    "march",
    "april",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "spring",
    "summer",
    "autumn",
    "winter",
    "fortnight",
    "century",
]
TIME_SEQUENCE = [
    "then",
    "now",
    "soon",
    "later",
    "afterwards",
    "afterward",
    "meanwhile",
    "presently",
    "immediately",
    "suddenly",
    "already",
    "ago",
    "before",
    "after",
    "when",
    "while",
    "until",
    "till",
    "since",
    "once",
    "again",
    "always",
    "never",
    "often",
    "sometimes",
    "finally",
    "last",
    "next",
    "first",
    "early",
    "late",
]
PAST, PRESENT = ("VBD",), ("VBP", "VBZ")
TERMINAL = tuple(PUNCT_CLASSES.index(p) for p in ("period", "question", "exclamation", "ellipsis"))
Q, EXCL = PUNCT_CLASSES.index("question"), PUNCT_CLASSES.index("exclamation")
SHORT_PARA = 20
MIN_NARRATION = 30

SCALARS = (
    "dialogue_share",
    "narr_first_sg",
    "narr_first_pl",
    "narr_second",
    "narr_third",
    "narr_past_share",
    "sent_question_share",
    "sent_exclamation_share",
    "log_chapter_words",
    "short_paragraph_share",
    "narr_time_units",
    "narr_time_sequence",
)
# the same counts taken over all text with no use of quotation marks, sentence or paragraph
# boundaries: computable from per-book (word, tag) counts
BAG_SCALARS = (
    "all_first_sg",
    "all_first_pl",
    "all_second",
    "all_third",
    "all_past_share",
    "question_per_1000",
    "exclamation_per_1000",
    "all_time_units",
    "all_time_sequence",
)
CURVES = ("dialogue", "sentence_length", "valence", "arousal", "first_person", "new_vocab")


class Lexicons:
    """Per-book lookups from type id / tag code to the word classes used here."""

    def __init__(self, book: dict[str, np.ndarray], valence: dict[str, float]) -> None:
        types = book["types"]
        self.cls = {
            "first_sg": np.isin(types, FIRST_SG),
            "first_pl": np.isin(types, FIRST_PL),
            "second": np.isin(types, SECOND),
            "third": np.isin(types, THIRD),
            "time_units": np.isin(types, TIME_UNITS),
            "time_sequence": np.isin(types, TIME_SEQUENCE),
        }
        self.valence = np.array([valence.get(t, 0.0) for t in types])
        self.past = np.isin(book["tag_names"], PAST)[book["tag"]]
        self.present = np.isin(book["tag_names"], PRESENT)[book["tag"]]


def scalars(
    book: dict[str, np.ndarray], lex: Lexicons, mask: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """SCALARS and BAG_SCALARS for the masked tokens. log_chapter_words is NaN when fewer
    than three headings are found in the mask."""
    word = book["is_word"] & mask
    narr = word & ~book["is_quote"]
    n_word, n_narr = max(int(word.sum()), 1), max(int(narr.sum()), 1)
    tid = book["tid"]

    def rate(cls: str, m: np.ndarray, n: int) -> float:
        return 1000.0 * lex.cls[cls][tid[m]].sum() / n

    def past_share(m: np.ndarray) -> float:
        past, present = (lex.past & m).sum(), (lex.present & m).sum()
        return past / max(past + present, 1)

    term = mask & np.isin(book["punct"], TERMINAL)
    last = np.full(int(book["sent"].max()) + 1, -1)
    last[book["sent"][term]] = book["punct"][term]  # later tokens overwrite: last terminal mark
    ended = last[last >= 0]
    n_sent = max(len(ended), 1)

    per_para = np.bincount(book["para"][word])
    heads = book["headings"][book["headings"] < len(per_para)]
    in_mask = np.zeros(len(per_para) + 1, bool)
    in_mask[np.unique(book["para"][mask])] = True
    n_heads = int(in_mask[heads].sum())
    per_para[heads] = 0
    p = per_para[per_para > 0]

    out = [
        (word & book["is_quote"]).sum() / n_word,
        rate("first_sg", narr, n_narr),
        rate("first_pl", narr, n_narr),
        rate("second", narr, n_narr),
        rate("third", narr, n_narr),
        past_share(narr & mask),
        (ended == Q).sum() / n_sent,
        (ended == EXCL).sum() / n_sent,
        np.log(n_word / n_heads) if n_heads >= 3 else np.nan,
        (p <= SHORT_PARA).mean(),
        rate("time_units", narr, n_narr),
        rate("time_sequence", narr, n_narr),
    ]
    pc = np.bincount(book["punct"][mask], minlength=len(PUNCT_CLASSES))
    bag = [
        rate("first_sg", word, n_word),
        rate("first_pl", word, n_word),
        rate("second", word, n_word),
        rate("third", word, n_word),
        past_share(mask),
        1000.0 * pc[Q] / n_word,
        1000.0 * pc[EXCL] / n_word,
        rate("time_units", word, n_word),
        rate("time_sequence", word, n_word),
    ]
    return np.array(out, float), np.array(bag, float)


def fill_gaps(c: np.ndarray) -> np.ndarray:
    """Linear interpolation over NaN segments (zeros if nothing is defined)."""
    ok = ~np.isnan(c)
    if not ok.any():
        return np.zeros_like(c)
    x = np.arange(len(c))
    return np.interp(x, x[ok], c[ok])


def curves(book: dict[str, np.ndarray], lex: Lexicons, mask: np.ndarray, n_seg: int) -> np.ndarray:
    """(len(CURVES), n_seg) raw curves over the book, by word position in the whole book."""
    is_word = book["is_word"]
    pos = np.cumsum(is_word) - is_word
    seg = np.minimum(pos * n_seg // max(int(is_word.sum()), 1), n_seg - 1)
    word = is_word & mask
    narr = word & ~book["is_quote"]
    tid = book["tid"]

    def per_seg(m: np.ndarray, weights: np.ndarray | None = None) -> np.ndarray:
        w = None if weights is None else weights[m]
        return np.bincount(seg[m], weights=w, minlength=n_seg).astype(float)

    n_w, n_n = per_seg(word), per_seg(narr)
    with np.errstate(invalid="ignore", divide="ignore"):
        dialogue = per_seg(word & book["is_quote"]) / n_w
        val = lex.valence[tid]
        valence = per_seg(word, val) / n_w
        arousal = per_seg(word, np.abs(val)) / n_w
        first = (lex.cls["first_sg"] | lex.cls["first_pl"])[tid].astype(float)
        first_person = np.where(n_n >= MIN_NARRATION, per_seg(narr, first) / n_n, np.nan)

        sent = book["sent"][word]
        length = np.bincount(sent)
        ids = np.flatnonzero(length)
        first_tok = np.full(len(length), -1)
        first_tok[sent[::-1]] = seg[word][::-1]  # earliest token of each sentence wins
        seg_of_sent = first_tok[ids]
        sent_len = np.bincount(
            seg_of_sent, weights=np.log(length[ids]), minlength=n_seg
        ) / np.bincount(seg_of_sent, minlength=n_seg)

        wt = tid[word]
        _, first_idx = np.unique(wt, return_index=True)
        is_new = np.zeros(len(wt))
        is_new[first_idx] = 1.0
        new_vocab = np.bincount(seg[word], weights=is_new, minlength=n_seg) / n_w
    raw = np.stack([dialogue, sent_len, valence, arousal, first_person, new_vocab])
    return np.stack([fill_gaps(c) for c in raw])


def znorm(c: np.ndarray) -> np.ndarray:
    """Each curve (last axis) to zero mean and unit sd; flat curves become zeros."""
    sd = c.std(-1, keepdims=True)
    return (c - c.mean(-1, keepdims=True)) / np.where(sd > 1e-12, sd, 1.0)


def shape_numbers(c: np.ndarray) -> np.ndarray:
    """Per curve: slope, sd of the raw curve, position of min and of max (after a 5-segment
    moving average), and DCT-II coefficients 1-4 of the z-normalised curve."""
    n = c.shape[-1]
    z = znorm(c)
    x = (np.arange(n) - (n - 1) / 2) / n
    slope = (z * x).sum(-1) / (x**2).sum()
    kernel = np.ones(5) / 5
    smooth = np.stack([np.convolve(row, kernel, mode="valid") for row in z])
    k = np.arange(1, 5)[:, None]
    basis = np.cos(np.pi * k * (np.arange(n) + 0.5) / n) * np.sqrt(2.0 / n)
    dct = z @ basis.T / np.sqrt(n)
    return np.concatenate(
        [
            slope[:, None],
            c.std(-1)[:, None],
            (smooth.argmin(-1) / (smooth.shape[-1] - 1))[:, None],
            (smooth.argmax(-1) / (smooth.shape[-1] - 1))[:, None],
            dct,
        ],
        axis=1,
    )


SHAPE_NAMES = ("slope", "sd", "argmin", "argmax", "dct1", "dct2", "dct3", "dct4")


def dtw_all_pairs(A: np.ndarray, B: np.ndarray, band: int) -> np.ndarray:
    """DTW distance between every row of A (n, S) and every row of B (m, S): squared
    differences summed along the best path inside a Sakoe-Chiba band, then the square root."""
    s = A.shape[1]
    inf = np.full((len(A), len(B)), np.inf)
    acc: dict[tuple[int, int], np.ndarray] = {}
    for i in range(s):
        for j in range(max(0, i - band), min(s, i + band + 1)):
            cost = (A[:, i, None] - B[None, :, j]) ** 2
            if i == 0 and j == 0:
                acc[i, j] = cost
                continue
            best = np.minimum(
                np.minimum(acc.get((i - 1, j), inf), acc.get((i, j - 1), inf)),
                acc.get((i - 1, j - 1), inf),
            )
            acc[i, j] = cost + best
        for j in range(s):
            acc.pop((i - 2, j), None)
    return np.sqrt(acc[s - 1, s - 1])
