"""The felt block: RateYourMusic descriptors of kind 1 only, weighted by page position.

The sorting of all 176 descriptors lives in descriptors.csv beside this file (word, kind, reason)
and is changed in pull requests like code. Not yet extracted. Source: recmyrecord
`data-pipeline/rmr_pipeline/audio.py` `descriptors` and `vocab.py`.
"""

from __future__ import annotations

import csv
from collections.abc import Sequence
from importlib import resources

from art2vec.medium import Block, LeakNote
from art2vec.work import Work

LEAK = LeakNote(saw="crowd descriptors from RateYourMusic, felt-response words only")

FELT = 1
TEXTURE = 2
SUBJECT = 3
POSITION = 4


def table() -> dict[str, int]:
    """Every descriptor and its kind, from descriptors.csv."""
    text = resources.files("art2vec.album2vec").joinpath("descriptors.csv").read_text()
    return {row["word"]: int(row["kind"]) for row in csv.DictReader(text.splitlines())}


def felt_words() -> list[str]:
    """The words that enter the distance: kind 1, in table order."""
    return [word for word, kind in table().items() if kind == FELT]


def block(works: Sequence[Work]) -> Block:
    raise NotImplementedError("not yet extracted from recmyrecord")
