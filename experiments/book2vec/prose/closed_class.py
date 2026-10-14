"""Prose control: a strict closed-class word list, with and without personal pronouns.

    .venv/bin/python -m prose.closed_class

Cosine Delta (z-scored relative frequencies, cosine) on fixed lists instead of the most
frequent words of the corpus:

    P6_closed_nopron   determiners, prepositions, conjunctions, auxiliaries and modals,
                       clitics, and the pronouns that do not track cast or narration
                       (demonstrative, relative, interrogative, indefinite)
    P6_closed_pron     the same plus personal and possessive pronouns
    P6_pron_only       personal and possessive pronouns alone

No open-class word is on any list, so subject matter cannot enter except through grammar.
"""

from __future__ import annotations

import numpy as np
from eval.blocks import save_block

from prose.features import zscore
from prose.tokens import book_keys, half_masks, load_book

DETERMINERS = "the a an this that these those every each either neither no any some all both "
DETERMINERS += "such another much many few several half what which whose whatever whichever"
PREPOSITIONS = (
    "of in to for with on at by from into upon about after before over under through between "
    "against among without within during towards toward across behind beyond above below "
    "beside besides near off out up down round around along until till since except per "
    "amid amongst beneath throughout past like unto onto despite via"
)
CONJUNCTIONS = (
    "and but or nor yet so if because although though while whilst whereas unless when "
    "whenever where wherever whether than as that lest once"
)
AUXILIARIES = (
    "be is am are was were been being have has had having do does did will would shall "
    "should can could may might must ought need dare 's 're 'm 've 'd 'll n't not to"
)
OTHER_PRONOUNS = (
    "who whom which what there one ones none nothing something anything everything nobody "
    "somebody anybody everybody someone anyone everyone other others whoever"
)
PERSONAL = (
    "i me my mine myself we us our ours ourselves you your yours yourself yourselves thou thee "
    "thy thine he him his himself she her hers herself it its itself they them their theirs "
    "themselves"
)


def words(*lists: str) -> list[str]:
    return list(dict.fromkeys(w for s in lists for w in s.split()))


LISTS = {
    "P6_closed_nopron": words(DETERMINERS, PREPOSITIONS, CONJUNCTIONS, AUXILIARIES, OTHER_PRONOUNS),
    "P6_closed_pron": words(
        DETERMINERS, PREPOSITIONS, CONJUNCTIONS, AUXILIARIES, OTHER_PRONOUNS, PERSONAL
    ),
    "P6_pron_only": words(PERSONAL),
}
PARTS = ("full", "a", "b", "h1", "h2")


def main() -> None:
    keys = book_keys()
    vocab = LISTS["P6_closed_pron"]
    wid = {w: i for i, w in enumerate(vocab)}
    freq = {p: np.zeros((len(keys), len(vocab))) for p in PARTS}
    for i, key in enumerate(keys):
        book = load_book(key)
        of_type = np.array([wid.get(str(t), -1) for t in book["types"]])
        for part, m in half_masks(book).items():
            m = m & book["is_word"]
            ids = of_type[book["tid"][m]]
            freq[part][i] = np.bincount(ids[ids >= 0], minlength=len(vocab)) / max(m.sum(), 1)
    for name, lst in LISTS.items():
        cols = np.array([wid[w] for w in lst])
        cols = cols[freq["full"][:, cols].sum(0) > 0]
        Z = {p: zscore(freq[p][:, cols], freq["full"][:, cols]) for p in PARTS}
        meta = {
            "what": f"Cosine Delta on a fixed closed-class list of {len(cols)} words",
            "input_level": "book bag",
            "metric": "cosine",
            "words": [vocab[c] for c in cols],
            "flagged": [],
        }
        save_block(
            name, keys, meta, X=Z["full"], X_a=Z["a"], X_b=Z["b"], X_h1=Z["h1"], X_h2=Z["h2"]
        )
        print(name, len(cols), flush=True)


if __name__ == "__main__":
    main()
