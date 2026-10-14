"""Labelled pair sets built from the group_tags of the testbed.

    .venv/bin/python -m eval.pairs            # print the sets and their sizes

Sets (pairs are unordered, stored as sorted key tuples):

    translation_pair              same work, different translator
    edition_pair                  same work, two editions by the author
    same_author_unrelated         same author, no shared translation / edition / series / sequel /
                                  retelling tag (so: unrelated plots)
    same_author_orig_en           ... of those, books written in English
    same_author_same_translator   ... of those, translated, same translator
    same_author_diff_translator   ... of those, translated, different translators
    series                        same series tag
    retelling                     same retelling tag (not two translations of one work), or the
                                  same sequel_pair tag
    same_translator_diff_author   control: one translator, two authors (Garnett)
    same_genre                    control: share a genre tag, different authors

``negatives`` are the pairs with different authors that are in none of translation_pair,
edition_pair, series, retelling: what "a random non-pair" means in the scores. Same-genre and
same-translator pairs stay among the negatives, because genre and translator are not supposed
to be relations between works.
"""

from __future__ import annotations

from itertools import combinations

import pandas as pd

from eval.blocks import load_testbed

Pair = tuple[str, str]
RELATED = ("translation_pair", "edition_pair", "series", "retelling")
ORDER = (
    "translation_pair",
    "edition_pair",
    "same_author_unrelated",
    "same_author_orig_en",
    "same_author_same_translator",
    "same_author_diff_translator",
    "series",
    "retelling",
    "same_translator_diff_author",
    "same_genre",
)


def translator_id(row: dict) -> str:
    """Translator tag if there is one, else the first name in the translator column."""
    tag = row["tags"].get("translator")
    if tag:
        return sorted(tag)[0]
    name = row["translator"].split(";")[0].strip().lower()
    return name.split()[-1] if name else ""


def share(a: dict, b: dict, tag: str) -> bool:
    return bool(a["tags"].get(tag, set()) & b["tags"].get(tag, set()))


def build_pairs(tb: pd.DataFrame | None = None) -> dict[str, list[Pair]]:
    """All pair sets plus "negatives", restricted to the books in ``tb``."""
    tb = load_testbed() if tb is None else tb
    sets: dict[str, list[Pair]] = {name: [] for name in (*ORDER, "negatives")}
    rows = {k: r for k, r in zip(tb.index, tb.to_dict("records"), strict=True)}
    for ka, kb in combinations(sorted(rows), 2):
        a, b = rows[ka], rows[kb]
        pair = (ka, kb)
        same_author = a["author"] == b["author"]
        translation = share(a, b, "translation_pair")
        edition = share(a, b, "edition_pair")
        series = share(a, b, "series")
        sequel = share(a, b, "sequel_pair")
        retelling = (share(a, b, "retelling") and not translation) or sequel
        ta, tr = translator_id(a), translator_id(b)
        if translation:
            sets["translation_pair"].append(pair)
        if edition:
            sets["edition_pair"].append(pair)
        if series:
            sets["series"].append(pair)
        if retelling:
            sets["retelling"].append(pair)
        if same_author and not (translation or edition or series or retelling):
            sets["same_author_unrelated"].append(pair)
            if a["orig_language"] == "en" and b["orig_language"] == "en":
                sets["same_author_orig_en"].append(pair)
            elif ta and tr:
                which = "same" if ta == tr else "diff"
                sets[f"same_author_{which}_translator"].append(pair)
        if not same_author and ta and ta == tr:
            sets["same_translator_diff_author"].append(pair)
        if not same_author and share(a, b, "genre"):
            sets["same_genre"].append(pair)
        if not same_author and not (translation or edition or series or retelling):
            sets["negatives"].append(pair)
    return sets


def main() -> None:
    sets = build_pairs()
    for name, pairs in sets.items():
        print(f"{name}: {len(pairs)} pairs")
        if name not in ("negatives", "same_genre"):
            for a, b in pairs:
                print(f"    {a} ~ {b}")


if __name__ == "__main__":
    main()
