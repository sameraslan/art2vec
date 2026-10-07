"""The three questions a medium answers, and the blocks it answers them with."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

import numpy as np

from art2vec.work import Work

Kind = Literal["content", "felt"]


@dataclass(frozen=True, slots=True)
class LeakNote:
    """What an encoder or descriptor source saw besides the work, and what was checked.

    Every block carries one (FRAMEWORK.md sections 4 and 9). `saw` is a plain
    sentence: "audio only", "Discogs genre and style labels", "crowd
    descriptors from RateYourMusic". `checks` names the leak checks run on
    the block (FRAMEWORK.md section 7).
    """

    saw: str
    checks: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Block:
    """One named matrix of vectors over some of a medium's works.

    `ids[i]` is the work whose vector is `vectors[i]`. Ids are strings, the
    same as `Work.id`; vectors are float32. A work with no data for this
    block is absent from `ids`; nothing is imputed (FRAMEWORK.md section 6).
    `kind` is "content" (read from the artefact) or "felt" (how the work
    makes people feel). `medium`, `model` and `version` pin what produced the
    vectors; fusion refuses to combine blocks of one medium at different
    versions (ARCHITECTURE.md section 7).
    """

    name: str
    kind: Kind
    medium: str
    ids: np.ndarray
    vectors: np.ndarray
    model: str
    version: str
    leak: LeakNote

    def __post_init__(self) -> None:
        ids = np.asarray(self.ids, dtype=str)
        vectors = np.asarray(self.vectors, dtype=np.float32)
        if ids.ndim != 1 or vectors.ndim != 2:
            raise ValueError("ids must be 1-d and vectors 2-d")
        if len(ids) != len(vectors):
            raise ValueError("ids and vectors must have one row per work")
        if len(np.unique(ids)) != len(ids):
            raise ValueError("ids must be unique within a block")
        object.__setattr__(self, "ids", ids)
        object.__setattr__(self, "vectors", vectors)

    @property
    def dim(self) -> int:
        return int(self.vectors.shape[1])


@runtime_checkable
class Medium(Protocol):
    """A plugin for one art form. See ARCHITECTURE.md section 2.

    Three questions and one chore. `canon` is the only method that may read
    ratings, counts or lists. `encode` reads cached artefacts and returns one
    or more content blocks; it is called one shard of works at a time, so it
    must treat each work independently (centring and PCA are a fitted,
    versioned transform stored beside the vectors, not part of `encode`).
    `describe` returns the one felt block. `fetch`, the chore, puts artefacts
    in the cache and is the only method that touches the network.
    """

    name: str
    version: str

    def canon(self) -> list[Work]: ...

    def fetch(self, works: Sequence[Work]) -> None: ...

    def encode(self, works: Sequence[Work]) -> list[Block]: ...

    def describe(self, works: Sequence[Work]) -> Block: ...
